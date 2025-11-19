import functools
import inspect
import time

from datetime import datetime
from typing import Any, Callable, Dict, Optional
from utils.position_manager import HedgePositionManager
from utils.statistics import Statistics
from utils.signal_manager import SignalManager
from utils.risk_signal import RiskSignal
from enums.risk_signal_types import RiskScope, RiskAction
from usecase.order_level.exchange_order_check import (
    exchange_order_slippage_check,
    exchange_order_latency_check,
    exchange_order_failure_check,
)
from usecase.order_level.symbol_order_check import (
    symbol_order_slippage_check,
    symbol_order_latency_check,
    symbol_order_failure_check,
)
from usecase.tick_level.spread_check import (
    spread_threshold_check,
    spread_price_amount_abnormal_check,
)
from usecase.tick_level.latency_check import bbo_latency_check
from usecase.global_level.balance_check import (
    available_balance_ratio_check,
    balance_zero_check,
    balance_unbalance_check,
    balance_drawdown_check,
    intraday_profit_threshold_check,
)
from usecase.global_level.exposure_check import (
    symbol_exposure_check,
    symbol_single_leg_check,
    symbol_notional_exposure_check
)
from usecase.global_level.leverage_check import leverage_check
from usecase.global_level.position_check import position_liquidation_price_check
from usecase.global_level.commission_check import commission_check

__version__ = "0.1.7"


class RiskManager:
    """
    风控信号管理器，用于定义风控信号检查的和内容。
    每一个风控信号应该由以下内容组成：
    - symbol 层：对单独 symbol 进行风控的检查
    - exchange 层：对单独交易所进行风控的检查
    - account 层：对单独账户进行风控的检查
    - global 层：对全局进行风控的检查
    对于不同层级的解释如下：
    - symbol 层：单独监控某一个 symbol 的行情、持仓、PnL 异常等情况并进行风控。
    - exchange 层：单独监控某一个或者几个交易所发生异常行为，例如交易所拔网线等。
    - account 层：单独监控整个账户的余额、持仓、PnL 的异常并进行风控。例如账户可用资金为 0, 账户可用资金不足 20% 等。
    - global 层：对全局进行风控的检查。例如账户回撤超过 5%，账户可用资金超过 x 秒没有被平衡等。
    当用户调用风控结果的时候，最终返回一个 RiskSignal 对象。如果一切正常，则返回的是一个空 RiskSignal 对象。通过对风控信号解析可以获取对应的风控内容
    """

    def __init__(
        self,
        abnormal_spread_threshold: float = 0.2,
        abnormal_bbo_latency_threshold: int = 5000,
        abnormal_order_slippage_threshold: float = 30.0,
        abnormal_order_latency_threshold: int = 600,
        max_account_leverage: float = 8.0,
        max_symbol_leverage: float = 1.0,
        abnormal_position_exposure_threshold: float = 0.05,
        available_balance_warning_threshold: float = 0.2,
        available_balance_unbalance_threshold: float = 1.2,
        total_drawdown_threshold: float = 0.95,
        intraday_loss_threshold: float = 1000.0,
        liquidation_price_warning_threshold: float = 0.01,
    ):
        """
        风控管理器
        - 自动绑定并缓存 Strategy 成员
        - 缓存并追踪关键字段: bbo / depth / funding / order / pm
        - 缓存风控配置参数（阈值）
        """
        # 缓存风控配置参数（阈值）
        self.abnormal_spread_threshold = abnormal_spread_threshold
        self.abnormal_bbo_latency_threshold = abnormal_bbo_latency_threshold
        self.abnormal_order_slippage_threshold = abnormal_order_slippage_threshold
        self.abnormal_order_latency_threshold = abnormal_order_latency_threshold
        self.max_account_leverage = max_account_leverage
        self.max_symbol_leverage = max_symbol_leverage
        self.abnormal_position_exposure_threshold = abnormal_position_exposure_threshold
        self.available_balance_warning_threshold = available_balance_warning_threshold
        self.available_balance_unbalance_threshold = available_balance_unbalance_threshold
        self.total_drawdown_threshold = total_drawdown_threshold
        self.intraday_loss_threshold = intraday_loss_threshold
        self.liquidation_price_warning_threshold = liquidation_price_warning_threshold

        self._strategy: Optional[Any] = None
        self.cached_attrs: Dict[str, Any] = {}
        self.bbo: Any = None
        self.fundings: Any = None
        self.pm: Any = None
        self.ex_map: Any = None
        self.balances: Any = None
        self.trader: Any = None
        self.previous_commission: Optional[Any] = None

        # on_* 方法参数本地缓存。用于识别行情异常、订单异常、全局异常。
        self._last_signal: Optional[Dict[str, Any]] = None
        # on_* 参数本地缓存（仅针对指定的方法）
        self.latest_bbo: Any = None
        self.latest_order: Any = None
        self.latest_order_account_id: Optional[Any] = None
        self.latest_strategy_index: Optional[Any] = None
        self.latest_strategy_symbol: Optional[Any] = None
        self.latest_commission: Optional[Any] = None

        # 本地订单状态统计（时间窗口触发）
        # 订单状态统计分为：exchange 和 symbol 两个层级。窗口为 10 秒，阈值为 5 次。
        self._win_receipt_ex: Dict[str, Dict[str, int]] = {}
        self._win_receipt_sym: Dict[str, Dict[str, int]] = {}
        self._win_slip_ex: Dict[str, Dict[str, int]] = {}
        self._win_slip_sym: Dict[str, Dict[str, int]] = {}
        self._win_lat_ex: Dict[str, Dict[str, int]] = {}
        self._win_lat_sym: Dict[str, Dict[str, int]] = {}


    def run(self):
        """
        还没想好，这个方法用来做什么，但是应该需要
        """
        return

    def check_tick_risk(self) -> RiskSignal:
        """
        检查 tick 级别的风控，需要传入 bbo 数据或者 depth 数据，并不一定都要传入。实现以下风控功能：
        - 行情价差异常监控
            - symbol 相同，价差超过 20%
            - symbol 价格本身有问题，例如 bid1 == ask1，又或者 0 价格和 amount
            - symbol 的行情距离当前时间太远，被交易所拔网线
        - 行情延迟风控
        """
        if not self.latest_bbo or 'symbol' not in self.latest_bbo:
            return RiskSignal()
        symbol = self.latest_bbo['symbol']
        if symbol not in self.bbo[0] or symbol not in self.bbo[1]:
            return RiskSignal()
        check_bbo = [self.bbo[0][symbol], self.bbo[1][symbol]]
        spread_check = spread_threshold_check(
            check_bbo,
            abnormal_spread_threshold=self.abnormal_spread_threshold,
        )
        price_amount_abnormal_check = spread_price_amount_abnormal_check(check_bbo)
        latency_check = bbo_latency_check(
            check_bbo,
            abnormal_bbo_latency_threshold=self.abnormal_bbo_latency_threshold,
        )

        # 生成信号并返回
        # 所有检查函数返回 True 表示正常，False 表示异常
        rs = RiskSignal()
        if not spread_check:
            # 价差异常，禁止该 symbol 开仓
            rs.add(
                scope=RiskScope.TICK,
                action=RiskAction.STOP_ALL,
                message="价差异常，禁止该 symbol 开仓",
                target_id=symbol,
            )
        if not price_amount_abnormal_check:
            # 交易所的价格和数量异常，禁止该 symbol 交易
            rs.add(
                scope=RiskScope.TICK,
                action=RiskAction.STOP_ALL,
                message="交易所的价格和数量异常，禁止该 symbol 交易",
                target_id=symbol,
            )
        if not latency_check:
            # 交易所的行情延迟异常，禁止该 symbol 交易
            rs.add(
                scope=RiskScope.TICK,
                action=RiskAction.STOP_ALL,
                message="交易所的行情延迟异常，禁止该 symbol 交易",
                target_id=symbol,
            )
        
        self._last_signal = rs.to_dict()
        return rs

    def check_order_receipt_risk(self, index: int, symbol: str, order_receipt: Dict[str, Any]) -> RiskSignal:
        """
        订单回执风控：当相同交易所/相同symbol第一次检测到失败，创建10秒窗口；
        10秒内相同错误累计>=5次则生成 RiskSignal；否则过期销毁窗口。
        失败定义：order_receipt 中不包含 'Ok' 字段。
        """
        rs = RiskSignal()
        # 推断交易所标识
        try:
            exchange = str(self.ex_map[index]) if isinstance(self.ex_map, dict) and index in self.ex_map else str(index)
        except Exception:
            exchange = str(index)
        is_failure = isinstance(order_receipt, dict) and ("Ok" not in order_receipt)
        if not is_failure:
            return rs
        window_ms = 10000
        min_hits = 5
        # 交易所窗口
        if self._bump_window(self._win_receipt_ex, exchange, window_ms, min_hits):
            rs.add(
                scope=RiskScope.ORDER,
                action=RiskAction.STOP_ALL,
                message="交易所层面：10秒内订单回执失败达到阈值，停止所有交易",
                target_id=exchange,
                context={"window_ms": window_ms, "min_hits": min_hits},
            )
        # Symbol 窗口
        if self._bump_window(self._win_receipt_sym, symbol, window_ms, min_hits):
            rs.add(
                scope=RiskScope.ORDER,
                action=RiskAction.STOP_ALL,
                message="Symbol 层面：10秒内订单回执失败达到阈值，停止该Symbol交易",
                target_id=symbol,
                context={"window_ms": window_ms, "min_hits": min_hits},
            )
        self._last_signal = rs.to_dict()
        return rs

    def check_order_risk(self) -> RiskSignal:
        """
        订单质量风控（10秒窗口累计）：
        - 首次发现：滑点 > 0.15%（15 bps）或 下单延迟 > 800ms -> 启动窗口
        - 10秒内相同错误累计 >= 5 次 -> 生成 RiskSignal；否则窗口过期销毁
        """
        rs = RiskSignal()
        if not isinstance(self.latest_order, dict):
            self._last_signal = rs.to_dict()
            return rs
        symbol = str(self.latest_order.get("symbol", "unknown"))
        exchange = str(self.latest_order.get("exchange", "unknown"))

        window_ms = 10_000
        min_hits = 5
        # 使用 RiskManager 中缓存的阈值
        ex_slip_bad, ex_slip_bps, _ = exchange_order_slippage_check(
            self.latest_order,
            threshold_bps=self.abnormal_order_slippage_threshold,
        )
        ex_lat_bad, ex_lat_ms, _ = exchange_order_latency_check(
            self.latest_order,
            threshold_ms=self.abnormal_order_latency_threshold,
        )
        sym_slip_bad, sym_slip_bps, _ = symbol_order_slippage_check(
            symbol,
            self.latest_order,
            threshold_bps=self.abnormal_order_slippage_threshold,
        )
        sym_lat_bad, sym_lat_ms, _ = symbol_order_latency_check(
            symbol,
            self.latest_order,
            threshold_ms=self.abnormal_order_latency_threshold,
        )

        # 交易所层面窗口计数
        if ex_slip_bad and self._bump_window(self._win_slip_ex, exchange, window_ms, min_hits):
            rs.add(
                scope=RiskScope.ORDER,
                action=RiskAction.STOP_ALL,
                message="交易所层面：10秒内滑点超阈值达到次数阈值，暂停交易",
                target_id=exchange,
                context={"window_ms": window_ms, "min_hits": min_hits, "slippage_bps": ex_slip_bps},
            )
        if ex_lat_bad and self._bump_window(self._win_lat_ex, exchange, window_ms, min_hits):
            rs.add(
                scope=RiskScope.ORDER,
                action=RiskAction.STOP_ALL,
                message="交易所层面：10秒内下单延迟超阈值达到次数阈值，暂停交易",
                target_id=exchange,
                context={"window_ms": window_ms, "min_hits": min_hits, "latency_ms": ex_lat_ms},
            )

        # Symbol 层面窗口计数
        if sym_slip_bad and self._bump_window(self._win_slip_sym, symbol, window_ms, min_hits):
            rs.add(
                scope=RiskScope.ORDER,
                action=RiskAction.STOP_ALL,
                message="Symbol 层面：10秒内滑点超阈值达到次数阈值，暂停交易",
                target_id=symbol,
                context={"window_ms": window_ms, "min_hits": min_hits, "slippage_bps": sym_slip_bps},
            )
        if sym_lat_bad and self._bump_window(self._win_lat_sym, symbol, window_ms, min_hits):
            rs.add(
                scope=RiskScope.ORDER,
                action=RiskAction.STOP_ALL,
                message="Symbol 层面：10秒内下单延迟超阈值达到次数阈值，暂停交易",
                target_id=symbol,
                context={"window_ms": window_ms, "min_hits": min_hits, "latency_ms": sym_lat_ms},
            )

        self._last_signal = rs.to_dict()
        return rs

    def check_global_risk(self) -> RiskSignal:
        """
        检查全局风控，实现了以下风控功能：
        - 整体账户余额回撤
        - 当日收益超过阈值后禁止开仓，只可以平仓
        - 可用资金为 0 风控
        - 账户可用资金风控
        - 账户杠杆风控
        - 账户可用资金不平衡风控
        - 单个 symbol 杠杆率过高风控
        - symbol 敞口风控
        - symbol 单腿风控
        """
        # 需要使用以下数据：self.balances, self.statistics, self.pm
        # - 使用 self.balances 完成需求：可用资金为 0 风控；账户可用资金风控；账户可用资金不平衡风控。
        # - 使用 self.statistics 完成需求：整体账户余额回撤; 当日收益超过阈值禁止开仓；
        # - 使用 self.pm 完成需求：账户杠杆风控；单个 symbol 杠杆率过高风控; symbol 敞口风控; symbol 单腿风控。
        balance_ratio_check = available_balance_ratio_check(
            self.balances,
            available_balance_warning_threshold=self.available_balance_warning_threshold,
        )
        zero_check = balance_zero_check(self.balances)
        unbalance_check = balance_unbalance_check(
            self.balances,
            available_balance_unbalance_threshold=self.available_balance_unbalance_threshold,
        )

        # 以下的用例检查，需要引入 self.statistics 来实现
        drawdown_check = balance_drawdown_check(
            self.statistics,
            total_drawdown_threshold=self.total_drawdown_threshold,
        )
        profit_threshold_check = intraday_profit_threshold_check(
            self.statistics,
            intraday_loss_threshold=self.intraday_loss_threshold,
        )

        exposure_check = symbol_exposure_check(
            self.symbols[0],
            self.pm,
            abnormal_position_exposure_threshold=self.abnormal_position_exposure_threshold,
        )
        notional_exposure_check = symbol_notional_exposure_check(
            self.symbols[0],
            self.bbo,
            self.pm,
            abnormal_position_exposure_threshold=self.abnormal_position_exposure_threshold,
        )
        single_leg_check = symbol_single_leg_check(self.symbols[0], self.pm)

        # 杠杆的判断需要用 balance 、 bbo 和  position manager 合起来判断。
        leverage_result = leverage_check(
            self.symbols[0],
            self.bbo,
            self.balances,
            self.pm,
            max_symbol_leverage=self.max_symbol_leverage,
            max_account_leverage=self.max_account_leverage,
        )
        # leverage_result 是一个字典：{'account_leverage': False, 'symbol_leverage': {}}
        # account_leverage 为 True 表示账户杠杆过高，False 表示正常
        # symbol_leverage 是一个字典，key 是 symbol，value 是 True/False
        leverage_check_passed = not leverage_result.get('account_leverage', False) and len(leverage_result.get('symbol_leverage', {})) == 0

        liquidation_price_check = position_liquidation_price_check(
            self.positions,
            self.bbo,
            liquidation_price_warning_threshold=self.liquidation_price_warning_threshold,
        )

        # 使用 self.trader 来获取手续费等级，和之前的费率进行对比。
        # 使用第一个账户的索引，或者使用 latest_order_account_id（如果存在）
        account_idx = self.latest_order_account_id if self.latest_order_account_id is not None else 0
        # fee_rate = self.trader.get_fee_rate(account_idx, "BTC_USDT")
        fee_rate = {'buyer': 0.0, 'maker': 0.0002, 'seller': 0.0, 'taker': 0.0005}
        if not self.previous_commission:
            self.previous_commission = fee_rate
            commission_check_result = True
        else:
            commission_check_result = commission_check(self.previous_commission, fee_rate)

        if balance_ratio_check and zero_check and unbalance_check \
           and drawdown_check and profit_threshold_check and not exposure_check['exposure'] \
           and not notional_exposure_check['exposure'] and single_leg_check and leverage_check_passed \
           and commission_check_result and not liquidation_price_check['Info']:
            rs = RiskSignal()
            self._last_signal = rs.to_dict()
            return rs
        else:
            rs = RiskSignal()
            if not balance_ratio_check:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.STOP_OPEN,
                    message="可用资金比例异常，暂停开仓",
                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if not zero_check:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.STOP_OPEN,
                    message="账户资金为 0，暂停开仓",
                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if not unbalance_check:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.STOP_OPEN,
                    message="账户资金不平衡，暂停开仓",
                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if not drawdown_check:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.STOP_OPEN,
                    message="账户资金回撤过大，暂停开仓",                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if not profit_threshold_check:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.STOP_OPEN,
                    message="当日收益超过阈值，暂停开仓",
                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if exposure_check['exposure']:
                rs.add(
                    scope=RiskScope.SYMBOL,
                    action=RiskAction.CLOSE_POSITION,
                    message="symbol 敞口过大，关闭该 symbol 敞口",
                    target_id=exposure_check['exposure'],
                )
                self._last_signal = rs.to_dict()
            if notional_exposure_check['exposure']:
                rs.add(
                    scope=RiskScope.SYMBOL,
                    action=RiskAction.CLOSE_POSITION,
                    message="symbol 名义市值敞口过大，关闭该 symbol 敞口",
                    target_id=notional_exposure_check['exposure'],
                )
                self._last_signal = rs.to_dict()
            if not single_leg_check:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.CLOSE_POSITION, 
                    message="symbol 单腿风控，关闭该 symbol 单腿",
                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if not leverage_check_passed:
                # 检查账户杠杆
                if leverage_result.get('account_leverage', False):
                    rs.add(
                        scope=RiskScope.GLOBAL,
                        action=RiskAction.STOP_OPEN,
                        message="账户杠杆过高，暂停开仓",
                        target_id="ALL",
                    )
                # 检查 symbol 杠杆
                for symbol, is_high_leverage in leverage_result.get('symbol_leverage', {}).items():
                    if is_high_leverage:
                        rs.add(
                            scope=RiskScope.SYMBOL,
                            action=RiskAction.STOP_OPEN,
                            message=f"symbol {symbol} 杠杆过高，暂停该 symbol 交易",
                            target_id=symbol,
                        )
                self._last_signal = rs.to_dict()
            if not commission_check_result:
                rs.add(
                    scope=RiskScope.GLOBAL,
                    action=RiskAction.STOP_ALL,
                    message="交易所手续费发生变化，暂停所有交易",
                    target_id="ALL",
                )
                self._last_signal = rs.to_dict()
            if liquidation_price_check['Info']:
                rs.add(
                    scope=RiskScope.SYMBOL,
                    action=RiskAction.CLOSE_POSITION,
                    message="position 强制平仓价格异常，关闭该 position",
                    target_id=liquidation_price_check['Info'].keys(),
                    context={"liquidation_price_check": liquidation_price_check['Info']},
                )
                self._last_signal = rs.to_dict()
        return rs

    def bind_strategy(self, strategy_instance: Any) -> None:
        """
        绑定策略实例，并初始化一次成员快照与关键字段缓存。
        """
        self._strategy = strategy_instance
        self._snapshot_strategy_members()
        self.update_from_strategy()

    def update_from_strategy(self) -> None:
        """
        从绑定的 Strategy 实例同步关键字段与成员快照。
        将策略所有的成员变量都缓存到该 RiskManager 实例中
        """
        if self._strategy is None:
            return
        # 缓存关键字段
        self.base_index = getattr(self._strategy, "base_index", 2)
        self.bbo = getattr(self._strategy, "bbo", [{} for _ in range(self.base_index)])
        self.fundings = getattr(self._strategy, "fundings", None)
        self.pm = getattr(self._strategy, "pm", None)
        self.ex_map = getattr(self._strategy, "ex_map", None)
        self.balances = getattr(self._strategy, "balances", None)
        self.trader = getattr(self._strategy, "trader", None)
        self.positions = getattr(self._strategy, "positions", [[], []])
        self.depth = getattr(self._strategy, "depth", [{} for _ in range(self.base_index)])
        self.symbols = getattr(self._strategy, "symbols", None)
        self.statistics = getattr(self._strategy, "statistics", Statistics())
        # 刷新所有非可调用的成员快照
        self._snapshot_strategy_members()

    def _cache_on_event(self, method_name: str, args: tuple, kwargs: dict) -> None:
        """
        根据 on_* 方法名将传入参数缓存到 RiskManager。
        仅缓存以下方法：
        - on_bbo(self, exchange, bbo)
        - on_depth(self, exchange, depth)
        - on_order(self, account_id, order)
        - on_strategy(self, index, symbol)
        - on_balance(self, account_id, balance)
        - on_funding(self, exchange, funding)
        并且根据新接收到的数据，对 self.bbo 、self.depth 、self.balances 和 self.fundings进行更新
        """
        if method_name == "on_bbo":
            exchange = kwargs.get("exchange", args[0] if len(args) > 0 else None)
            bbo = kwargs.get("bbo", args[1] if len(args) > 1 else None)
            index = self.ex_map[exchange]
            self.bbo[index][bbo.get('symbol', '')] = bbo
            self.latest_bbo = bbo
        elif method_name == "on_depth":
            exchange = kwargs.get("exchange", args[0] if len(args) > 0 else None)
            depth = kwargs.get("depth", args[1] if len(args) > 1 else None)
            index = self.ex_map[exchange]
            self.depth[index][depth.get('symbol', '')] = depth
            latest_bbo = {
                'symbol': depth.get('symbol', ''),
                'bid_price': depth['bids'][0][0],
                'bid_qty': depth['bids'][0][1],
                'ask_price': depth['asks'][0][0],
                'ask_qty': depth['asks'][0][1],
                'timestamp': depth['timestamp']
            }
            self.bbo[index][depth.get('symbol', '')] = latest_bbo
            self.latest_bbo = latest_bbo
        elif method_name == "on_order":
            account_id = kwargs.get("account_id", args[0] if len(args) > 0 else None)
            order = kwargs.get("order", args[1] if len(args) > 1 else None)
            self.latest_order_account_id = account_id
            self.latest_order = order
        elif method_name == "on_strategy":
            index = kwargs.get("index", args[0] if len(args) > 0 else None)
            symbol = kwargs.get("symbol", args[1] if len(args) > 1 else None)
            self.latest_strategy_index = index
            self.latest_strategy_symbol = symbol
        elif method_name == "on_balance":
            account_id = kwargs.get("account_id", args[0] if len(args) > 0 else None)
            balances = kwargs.get("balances", args[1] if len(args) > 1 else None)
            usdt = next((x for x in balances if x["asset"] == "USDT"), None)
            self.balances[account_id].update(usdt)
        elif method_name == "on_funding":
            exchange = kwargs.get("exchange", args[0] if len(args) > 0 else None)
            funding = kwargs.get("funding", args[1] if len(args) > 1 else None)
            index = self.ex_map[exchange]
            for item in funding:
                self.fundings[index][item.get('symbol', '')] = item

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    def _bump_window(self, store: Dict[str, Dict[str, int]], key: str, window_ms: int, min_hits: int) -> bool:
        """
        在 store[key] 上进行 10 秒窗口计数：达到 min_hits 返回 True，并清空该窗口；否则返回 False。
        规则：
        - 第一次命中：创建窗口 {start, count=1}
        - 窗口内再次命中：count+1；若 count>=min_hits -> 返回 True 并删除窗口
        - 超过窗口时间且未达阈值：销毁旧窗口，重新从1开始
        """
        now = self._now_ms()
        entry = store.get(key)
        if entry is None or (now - entry.get("start", 0)) > window_ms:
            store[key] = {"start": now, "count": 1}
            return False
        entry["count"] = entry.get("count", 0) + 1
        if entry["count"] >= min_hits:
            try:
                del store[key]
            except Exception:
                store[key] = {"start": now, "count": 0}
            return True
        return False

    def _snapshot_strategy_members(self) -> None:
        """
        抓取 Strategy 的所有"数据型"成员变量（排除可调用与双下划线）。
        TODO: 这样能够将 Strategy 在 init 方法中的变量都缓存，但是需要考虑有一些变量是在 start() 和 prepare_symbols() 方法中初始化的，这些变量也需要缓存
        """
        if self._strategy is None:
            return
        result: Dict[str, Any] = {}
        for name in dir(self._strategy):
            if name.startswith("__"):
                continue
            try:
                value = getattr(self._strategy, name)
            except Exception:
                continue
            if callable(value):
                continue
            result[name] = value
        self.cached_attrs = result


def risk_managed(
    abnormal_spread_threshold: float = 0.2,
    abnormal_bbo_latency_threshold: int = 5000,
    abnormal_order_slippage_threshold: float = 30.0,
    abnormal_order_latency_threshold: int = 600,
    max_account_leverage: float = 8.0,
    max_symbol_leverage: float = 1.0,
    abnormal_position_exposure_threshold: float = 0.05,
    available_balance_warning_threshold: float = 0.2,
    available_balance_unbalance_threshold: float = 1.2,
    total_drawdown_threshold: float = 0.95,
    intraday_loss_threshold: float = 1000.0,
    liquidation_price_warning_threshold: float = 0.01,
    on_prefix: str = "on_",
) -> Callable[[type], type]:
    """
    类装饰器：为 Strategy 自动注入 RiskManager，并包装所有以 on_ 开头的方法。
    - 在每次 on_ 方法调用前：同步 bbo/fundings/pm，执行 risk_check
    - 在实例上注入 self.risk_manager 以供直接访问 get_risk_signal()
    """
    def decorator(cls: type) -> type:
        # 包装 __init__：创建并绑定 RiskManager
        orig_init = getattr(cls, "__init__", None)

        @functools.wraps(orig_init)
        def __init__(self, *args, **kwargs):
            if orig_init is not None:
                orig_init(self, *args, **kwargs)
            else:
                super(cls, self).__init__(*args, **kwargs)  # 如果没有触发初始化，理论兜底再进行初始化
            rm = RiskManager(
                abnormal_spread_threshold=abnormal_spread_threshold,
                abnormal_bbo_latency_threshold=abnormal_bbo_latency_threshold,
                abnormal_order_slippage_threshold=abnormal_order_slippage_threshold,
                abnormal_order_latency_threshold=abnormal_order_latency_threshold,
                max_account_leverage=max_account_leverage,
                max_symbol_leverage=max_symbol_leverage,
                abnormal_position_exposure_threshold=abnormal_position_exposure_threshold,
                available_balance_warning_threshold=available_balance_warning_threshold,
                available_balance_unbalance_threshold=available_balance_unbalance_threshold,
                total_drawdown_threshold=total_drawdown_threshold,
                intraday_loss_threshold=intraday_loss_threshold,
                liquidation_price_warning_threshold=liquidation_price_warning_threshold,
            )
            setattr(self, "risk_manager", rm)
            rm.bind_strategy(self)

        setattr(cls, "__init__", __init__)

        # 包装所有 on_ 前缀的方法
        for name, attr in list(vars(cls).items()):
            if not name.startswith(on_prefix):
                continue
            if not callable(attr):
                continue

            def make_wrapper(method: Callable[..., Any]) -> Callable[..., Any]:
                method_name = method.__name__
                @functools.wraps(method)
                def wrapped(self, *args, **kwargs):
                    rm: Optional[RiskManager] = getattr(self, "risk_manager", None)
                    if rm is None:
                        rm = RiskManager(
                            abnormal_spread_threshold=abnormal_spread_threshold,
                            abnormal_bbo_latency_threshold=abnormal_bbo_latency_threshold,
                            abnormal_order_slippage_threshold=abnormal_order_slippage_threshold,
                            abnormal_order_latency_threshold=abnormal_order_latency_threshold,
                            max_account_leverage=max_account_leverage,
                            max_symbol_leverage=max_symbol_leverage,
                            abnormal_position_exposure_threshold=abnormal_position_exposure_threshold,
                            available_balance_warning_threshold=available_balance_warning_threshold,
                            available_balance_unbalance_threshold=available_balance_unbalance_threshold,
                            total_drawdown_threshold=total_drawdown_threshold,
                            intraday_loss_threshold=intraday_loss_threshold,
                            liquidation_price_warning_threshold=liquidation_price_warning_threshold,
                        )
                        setattr(self, "risk_manager", rm)
                        rm.bind_strategy(self)
                    # 仅针对指定 on_* 方法进行本地参数缓存
                    if method_name in {"on_bbo", "on_depth", "on_order", "on_strategy", "on_balance", "on_funding"}:
                        rm._cache_on_event(method_name, args, kwargs)
                    # 执行数据更新
                    rm.update_from_strategy()
                    return method(self, *args, **kwargs)
                return wrapped

            setattr(cls, name, make_wrapper(attr))

        return cls

    return decorator

if __name__ == "__main__":
    # 新创建一个 Mock Strategy 类用于仿真
    # 最小可运行与功能测试
    @risk_managed()                                           # 对策略类进行装饰，自动注入 RiskManager，并包装所有以 on_ 开头的方法，这种方法可以减少对策略类代码的注入
    class Strategy:
        def __init__(self):
            # 模拟策略的成员变量
            self.bbo = [{'BTC_USDT':{'bid_price':100, 'bid_qty':100, 'ask_price':101, 'ask_qty':100, 'timestamp':1715769600}}, {'BTC_USDT':{'bid_price':99, 'bid_qty':200, 'ask_price':102, 'ask_qty':200, 'timestamp':1715769600}}]
            self.symbols = [["BTC_USDT"], ["BTC_USDT"]]
            self.fundings = [
                {symbol: {"funding_rate": 0, "funding_interval": 8,
                            "next_funding_at": 0} for symbol in self.symbols[idx]}
                for idx in range(len(self.symbols))
            ]
            self.ex_map = {'BinanceSwap': 0, 'OkxSwap': 1, 0: 'BinanceSwap', 1: 'OkxSwap'}
            self.balances = [{}, {}]
            self.pm = HedgePositionManager()
            self.statistics = Statistics()
            self.signal_manager = SignalManager()
            self.name = "MockStrategy"

        def on_bbo(self, exchange, bbo):
            print("on_bbo: 业务逻辑执行")
            index = 1   # 模拟通过 exchange 转为 index 的逻辑
            symbol = bbo.get('symbol', '')
            self.bbo[index][symbol] = {
                'bid_price': bbo.get('bid_price', 0),
                'bid_qty': bbo.get('bid_qty', 0),
                'ask_price': bbo.get('ask_price', 0),
                'ask_qty': bbo.get('ask_qty', 0),
                'timestamp': bbo.get('timestamp', 0)
            }

        def on_depth(self, exchange, depth):
            print("on_depth: 业务逻辑执行")
            index = 1   # 模拟通过 exchange 转为 index 的逻辑
            symbol = depth.get('symbol', '')
            self.bbo[index][symbol] = {
                'bid_price': depth['bids'][0][0],
                'bid_qty': depth['bids'][0][1],
                'ask_price': depth['asks'][0][0],
                'ask_qty': depth['asks'][0][1],
                'timestamp': depth['timestamp']
            }

        def on_balance(self, account_id, balance):
            print("on_balance: 业务逻辑执行")
            self.balances[account_id] = balance

        def on_order(self, account_id, order):
            print("on_order: 业务逻辑执行")

        def on_funding(self, exchange, funding):
            print("on_funding: 业务逻辑执行")

        def on_strategy(self, index, symbol):
            print("on_strategy: 业务逻辑执行")

        def not_triggered(self):
            print(f"{self.__class__.__name__} 由于该方法不以 on_ 开头，该方法不会触发风控")


    # ==================================== 以下是模拟真实场景，对 strategy 进行调用 ==================================
    s = Strategy()
    print("策略初始化后, RiskManager 风控的参数变量更新：")
    print("=== 测试循环更新 self.bbo 数据, 模拟真实场景收到 bbo 数据风控功能是否能正常运行 ===")
    
    # 模拟循环接收到 bbo 数据的真实场景，检查 RiskManager 是否正确同步
    for i in range(5):
        # 更新 Strategy 的 bbo 数据
        print(f"-------------------------------- 第 {i+1} 次更新 bbo 数据, 模拟真实场景收到 bbo 数据 --------------------------------")

        # 调用 on_ 开头的函数触发数据更新
        s.on_bbo('BinanceSwap', {'symbol': 'BTC_USDT', 'bid_price': 100 + i * 1, 'bid_qty': 100 + i * 1, 'ask_price': 101 + i * 1, 'ask_qty': 100 + i * 1, 'timestamp': 1715769600})
    
    print(f"-------------------------------- 开始执行策略 on_strategy 方法 --------------------------------")
    s.on_strategy(0, 'BTC_USDT')
    print(f"-------------------------------- 策略执行完成 --------------------------------")
