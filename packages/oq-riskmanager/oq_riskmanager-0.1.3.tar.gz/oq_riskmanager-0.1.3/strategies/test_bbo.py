# =============================================
# 2025-09-18 10:00:00
# =============================================

# =============================================
import base64
import decimal
import json
import time
import hmac
import hashlib
from threading import Lock
import pytz
import requests
# import traderv2  # type: ignore
import base_strategy
import datetime
import traceback
import sys
import os
import csv
import numpy as np

from risk_manager import risk_managed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.test_utils.order_manager import OrderManager, Order
from strategies.test_utils.position_manager import HedgePositionManager
from strategies.test_utils.statistics import Statistics, Stats

from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class SlippageEstimate:
    avg_price: float | None
    slippage_pct: float | None
    filled: float
    note: str | None = None

# =====================
# 该脚本实现以下需求
# 1. 修改 abnormal_bbo_latency_threshold 为 20ms，来检测异常的行情延迟
# 2. 相同 symbol 的有效价差异常检测。
# =====================
@risk_managed(
abnormal_spread_threshold = 0.0003,                     # 相同 symbol 的行情价差异常的阈值
abnormal_bbo_latency_threshold = 20,                      # 相同 symbol 的行情延迟异常的阈值
abnormal_order_slippage_threshold = 30.0,               # 订单滑点异常的阈值，单位是 bps，即 0.01%
abnormal_order_latency_threshold = 600,                   # 订单下单延迟异常检查的阈值，单位是 ms
max_account_leverage = 8.0,                             # 全部账户最大持仓杠杆约束
max_symbol_leverage = 1.0,                              # symbol 最大持仓杠杆约束
abnormal_position_exposure_threshold = 0.05,            # 持仓数量的敞口暴露异常阈值, 0.05 表示 5% 
available_balance_warning_threshold = 0.2,              # 可用资金的告警阈值，0.2 表示 20% 的阈值
available_balance_unbalance_threshold = 1.2,            # 可用资金不平衡的阈值， 1.2 表示两个两个交易所的可用资金相除比例超过 1.2 认为显著不平衡
total_drawdown_threshold = 0.95,                        # 资金回撤的阈值，0.95 表示资金回撤超过 5% 认为显著回撤
intraday_loss_threshold = 1000.0,                       # 日内亏损停止交易的阈值，-1000.0 表示日内亏损超过 1000U 认为显著亏损
liquidation_price_warning_threshold = 0.01,             # symbol 价格距离强平价格的报警阈值，0.01 表示价格距离强平价格超过 1% 认为显著异常
)
class Strategy(base_strategy.BaseStrategy):
    
    def __init__(self, cex_configs, dex_configs, config, trader):
        self.cex_configs = cex_configs
        self.has_account = len(cex_configs) > 0
        self.base_index = len(self.cex_configs)
        self.config = config
        self.trader = trader
        self.local_start_time = int(time.time()*1000)
        self.symbols = [config["symbols"] for _ in range(self.base_index)]
        self.leverage = 10

        ###################################################################
        # 完成初始化变量创建与声明
        ###################################################################
        # 功能性变量 
        self.instruments = [{} for _ in range(self.base_index)]
        self.exchange_timestamp = [
            {symbol: 0 for symbol in self.symbols[0]} for _ in range(self.base_index)]
        self.ex_map = {}
        for i, cex in enumerate(self.cex_configs):
            self.ex_map[cex["exchange"]] = i
            self.ex_map[i] = cex["exchange"]

        # 交易对行情存储
        self.bbo = [{} for _ in range(self.base_index)]

        # 账户变量
        self.balances = [{} for _ in range(self.base_index)]
        self.pm = HedgePositionManager(self.symbols[0], self.base_index)
        self.statistics = Statistics()

    def prepare_symbols(self):
        try:
            exchanges_insts = []
            for i in range(self.base_index):
                res = self.trader.get_instruments(i)
                exchanges_insts.append(
                    {inst["symbol"]: inst for inst in res["Ok"] if inst["state"] == "Normal"})

            binance_symbols = list(exchanges_insts[0].keys())

            if not self.symbols[0]:
                split = split_symbols(
                    binance_symbols, self.node_nums, self.node_index)
                split = [x for x in split if x not in self.banned_symbols]

                hedge_symbols = []
                for idx in range(1, self.base_index):
                    common = set(split) & set(exchanges_insts[idx].keys())
                    hedge_symbols.append(list(common))

                binance_symbols_new = list(set().union(*hedge_symbols))

                self.symbols = []
                # symbols[0] = Binance
                self.symbols.append(binance_symbols_new)
                self.symbols.extend(hedge_symbols)

            self.local_symbol_order = {symbol: {}
                                       for symbol in self.symbols[0]}
            self.trader.log(f"订阅以下 symbol: {self.symbols[0]}")

            self.instruments = []
            for idx in range(self.base_index):
                inst = {
                    symbol: exchanges_insts[idx].get(symbol)
                    for symbol in self.symbols[idx]
                    if symbol in exchanges_insts[idx]
                }
                self.instruments.append(inst)
                self.trader.log(
                    f"交易对初始化 exchange-{idx} 交易对数量 {len(inst)}",
                    level="INFO",
                    color="blue",
                )

            self.order_lock = {symbol: False for symbol in self.symbols[0]}
            self.lock_times = {symbol: 0 for symbol in self.symbols[0]}
            self.max_position = [
                {symbol: 1000 for symbol in self.symbols[idx]} for idx in range(self.base_index)]
            self.fundings = [
                {symbol: {"funding_rate": 0, "funding_interval": 8,
                          "next_funding_at": 0} for symbol in self.symbols[idx]}
                for idx in range(self.base_index)
            ]

            self.pm = HedgePositionManager(self.symbols[0], self.base_index)

        except Exception:
            self.trader.log(f"{traceback.format_exc()}",
                            level="ERROR", color="red")

    def start(self):
        try:
            self.trader.log("策略启动中...", level="INFO", color="blue")
            self.prepare_symbols()  # 准备交易对信息

            self.fee_rates = []
            for idx in range(self.base_index):
                fee_rate = self.trader.get_fee_rate(idx, "BTC_USDT")
                if "Ok" in fee_rate:
                    self.fee_rates.append(fee_rate["Ok"])
                    self.trader.log(
                        f"交易所 {self.ex_map[idx]} 手续费率: {fee_rate['Ok']}",
                        level="INFO",
                        color="blue",
                    )
                else:
                    raise Exception(
                        f"获取交易所 {self.ex_map[idx]} 手续费率失败: {fee_rate}")

            for i in range(self.base_index):
                balance = self.trader.get_usdt_balance(i)
                self.trader.log(
                    f"交易所 {self.ex_map[i]} 账户余额: {balance}",
                    level="INFO",
                    color="blue",
                )
                self.balances[i] = balance.get("Ok", {})

            # 查询是否双向持仓
            for i in range(0, self.base_index):
                is_dual = self.trader.is_dual_side(i)
                if "Ok" in is_dual:
                    # 如果当前是双向持仓，改为单向持仓
                    if is_dual["Ok"]:
                        # 设置单向持仓
                        res = self.trader.set_dual_side(i, False)

            # 获取仓位信息
            self.trader.log("获取遗留仓位", level="INFO", color="blue")
            for i in range(self.base_index):
                res = self.trader.get_positions(i)
                if "Ok" in res:
                    self.pm.update_positions(i, res["Ok"], init_pos=True)
                    for pos in res['Ok']:
                        if pos["amount"] != 0 and pos["symbol"] not in self.symbols[0]:
                            self.symbols[i].append(pos["symbol"])
                            # 同时更新 self.instruments，避免 KeyError
                            if pos["symbol"] not in self.instruments[i]:
                                # 尝试从交易所获取该symbol的instrument信息
                                try:
                                    symbol_info = self.trader.get_instrument_info(
                                        i, pos["symbol"])
                                    if "Ok" in symbol_info:
                                        self.instruments[i][pos["symbol"]
                                                            ] = symbol_info["Ok"]
                                    else:
                                        self.trader.log(
                                            f"无法获取遗留仓位symbol的instrument信息: {pos['symbol']}", level="WARN", color="yellow")
                                except Exception as e:
                                    self.trader.log(
                                        f"获取遗留仓位symbol的instrument信息失败: {pos['symbol']} - {e}", level="WARN", color="yellow")

            # 配置 self.statistics 的余额
            if not self.statistics.start_balance:
                init_available_balance, init_balance = self.get_total_init_balance()
                self.statistics.start_balance = init_balance
                self.statistics.max_balance = init_balance
                self.statistics.now_balance = init_balance
                self.statistics.today_balance = init_balance

            # 设置杠杆 和 全仓模式
            self.trader.log(f"设置杠杆倍数: {self.leverage}x",
                            level="INFO", color="blue")
            for i, symbols in enumerate(self.symbols):
                for symbol in symbols:
                    if self.ex_map[i] != 'BitgetSwap' and self.ex_map[i] != 'OkxSwap' and self.ex_map[i] != 'GateSwap':
                        self.trader.set_margin_mode(i, symbol, 'USDT', "Cross")
                    leverage = self.leverage
                    res = self.trader.get_max_leverage(0, symbol)
                    max_leverage = res.get("Ok", self.leverage)
                    if max_leverage and max_leverage < self.leverage:
                        leverage = max_leverage

                    res = self.trader.get_max_leverage(i, symbol)
                    max_leverage = res.get("Ok", self.leverage)
                    if max_leverage and max_leverage < self.leverage:
                        leverage = max_leverage
                    self.trader.set_leverage(i, symbol, leverage)
                    time.sleep(0.5)

                    if i:
                        continue
                    res = self.trader.get_max_position(0, symbol)
                    if "Ok" in res:
                        self.trader.log(
                            f"设置杠杆和全仓模式: {res}", level="INFO", color="blue")
        except Exception as e:
            self.trader.log(
                f"策略启动失败: {traceback.format_exc()}", level="ERROR", color="red")

    def subscribes(self):
        subs = []

        for i in range(self.base_index):
            # Binance 订阅 BBO，不订阅 Depth；Bitget 订阅 Depth 1 不订阅 BBO
            pub_channels = [
                {"Bbo": self.symbols[i]},
                {"Depth": {"symbols": self.symbols[i], "levels": 3}},
            ]
            pri_channels = [
                {"Position": self.symbols[i]},  # 订阅持仓更新
                {"FundingFee": self.symbols[i]},  # 订阅资金费结算
                {"Order": self.symbols[i]},
            ]
            subs.append({"account_id": i, "sub": {
                        "SubscribeWs": pub_channels}})
            subs.append({"account_id": i, "sub": {
                        "SubscribeWs": pri_channels}})
            subs.append(
                {
                    "account_id": i,
                    "sub": {
                        "SubscribeRest": {
                            "update_interval": {"secs": 30, "nanos": 0},
                            "rest_type": "Funding",
                        }
                    },
                }
            )
        subs.append(
            {
                "sub": {
                    "SubscribeTimer": {
                        "update_interval": {"secs": 60, "nanos": 0},
                        "name": "update_web_timer",  # 每 60 秒进行一次 WEB 页面更新
                    }
                }
            },
        )

        return subs
    
    def on_bbo(self, exchange, bbo):
        index = self.ex_map[exchange]
        symbol = bbo["symbol"]
        if bbo['timestamp'] <= self.exchange_timestamp[index][symbol]:
            return
        
        self.bbo[index][symbol] = [
            bbo['bid_price'],
            bbo['bid_qty'],
            bbo['ask_price'],
            bbo['ask_qty'],
            bbo['timestamp'],
            int(time.time()*1000),
        ]

        risk_signal = self.risk_manager.check_tick_risk()
        if risk_signal and not risk_signal.is_empty():
            print(f"行情延迟异常: {risk_signal.to_dict()}")
            print(f"---------------------------------------------------------")

    def on_depth(self, exchange, depth):
        index = self.ex_map[exchange]
        symbol = depth["symbol"]
        self.bbo[index][symbol] = [
            depth["bids"][0][0],
            depth["bids"][0][1],
            depth["asks"][0][0],
            depth["asks"][0][1],
            depth["timestamp"],
            int(time.time()*1000),
        ]
        self.exchange_timestamp[index][symbol] = depth["timestamp"]

    def on_balance(self, account_id, balances):
        usdt = next((x for x in balances if x["asset"] == "USDT"), None)
        self.balances[account_id].update(usdt)

    def on_funding(self, exchange, fundings):
        pass

    def on_order(self, account_id, order):
        pass

    def on_strategy(self, index, symbol):
        pass

    def on_timer_subscribe(self, timer_name):
        pass

# ============================= 下单函数 ====================================

    def place_market_order(self, cid, local_order):
        """
        市价下单，用于创建 Market 订单。
        """
        # 检查 symbol 是否在 instruments 中
        if local_order.symbol not in self.instruments[local_order.account_id]:
            self.trader.log(
                f"Symbol {local_order.symbol} 不在 instruments 中，跳过市价下单", level="WARN", color="yellow", web=False)
            return False

        if (local_order.amount * self.instruments[local_order.account_id][local_order.symbol]['amount_multiplier'] < self.instruments[local_order.account_id][local_order.symbol]['amount_tick']) or (local_order.price * self.instruments[local_order.account_id][local_order.symbol]['price_multiplier'] < self.instruments[local_order.account_id][local_order.symbol]['price_tick']):
            return True
        local_order.is_market = True

        order = {
            "cid": cid,  # 客户端订单ID
            "symbol": local_order.symbol,
            "order_type": "Market",  # 市价单
            "side": local_order.side,  # Buy/Sell
            "pos_side": local_order.pos_side,  # 单向持仓模式
            "time_in_force": "IOC",  # 立即成交或全部取消
            "price": local_order.price,
            "amount": local_order.amount,
            "reduce_only": local_order.reduce_only,
        }
        params = {'is_dual_side': False, 
                  "market_order_mode": "Normal",
                  "process_amount": "Round",
                  "process_price": "Round"
                  }
        self.trader.log(
            f"对冲单下单实际价格和数量: order_price:{local_order.price}; order_amount:{local_order.amount}; price_tick:{self.instruments[local_order.account_id][local_order.symbol]['price_tick']}; price_multiplier:{self.instruments[local_order.account_id][local_order.symbol]['price_multiplier']}; amount_tick:{self.instruments[local_order.account_id][local_order.symbol]['amount_tick']}; amount_multiplier:{self.instruments[local_order.account_id][local_order.symbol]['amount_multiplier']}", level="INFO", color="blue", web=False)
        self.trader.log(f"对冲单具体数据: {order}", level="INFO", color="blue", web=False)
        if local_order.price and local_order.amount:
            result = self.trader.place_order(
                local_order.account_id, order, params=params)
            self.trader.log(f"对冲单下单结果: {result}",
                            level="INFO", color="blue", web=False)
            if 'Ok' in result:
                return True
        return False

    def place_limit_order(self, cid, local_order, time_in_force="GTC"):
        """
        限价下单，用于创建 Maker 订单。Maker 订单在 Bitget 交易所成交。
        """
        # 检查 symbol 是否在 instruments 中
        if local_order.symbol not in self.instruments[local_order.account_id]:
            self.trader.log(
                f"Symbol {local_order.symbol} 不在 instruments 中，跳过限价下单", level="WARN", color="yellow", web=False)
            return False

        # 添加调试信息
        self.trader.log(
            f"place_limit_order 开始: symbol={local_order.symbol}, side={local_order.side}, pos_side={local_order.pos_side}, price={local_order.price}, amount={local_order.amount}, time_in_force={time_in_force}", level="INFO", color="blue", web=False)

        self.trader.log(
            f"place_limit_order 调整后: price={local_order.price}, amount={local_order.amount}", level="INFO", color="blue", web=False)
        order = {
            "cid": cid,  # 客户端订单ID
            "symbol": local_order.symbol,
            "order_type": "Limit",  # 限价单
            "side": local_order.side,  # Buy/Sell
            "pos_side": local_order.pos_side,  # 单向持仓模式
            "time_in_force": time_in_force,  # 一直有效直到取消
            "price": local_order.price,
            "amount": local_order.amount,
            "reduce_only": local_order.reduce_only,
        }
        params = {'is_dual_side': False,
                  "process_amount": "Round",
                  "process_price": "Round"
                  }
        if abs(local_order.price * local_order.amount) < 5 and not local_order.reduce_only:
            return False
        self.trader.log(
            f"place_limit_order 发单: {order}", level="INFO", color="blue", web=False)
        result = self.trader.place_order(local_order.account_id, order, params=params)
        self.trader.log(
            f"place_limit_order 发单结果: {result}", level="INFO", color="blue", web=False)
        if 'Ok' in result:
            self.trader.log(
                f"place_limit_order 发单成功: {order}, cid: {cid}", level="INFO", color="blue", web=False)
            return True
        return False
