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
# 本策略试实现以下功能的测试：
# 1. 单腿识别，因为只在一个交易所发单，所以一旦成交，就是单腿仓位。
# 2. 修改 max_account_leverage 和 max_symbol_leverage 为 0.05，来检测异常的杠杆使用
# 3. 敞口过大。
# 4. symbol 强平价格。修改 liquidation_price_warning_threshold 为 1，来检测异常的强平价格。
# =====================
@risk_managed(
abnormal_spread_threshold = 0.2,                        # 相同 symbol 的行情价差异常的阈值
abnormal_bbo_latency_threshold = 5000,                    # 相同 symbol 的行情延迟异常的阈值
abnormal_order_slippage_threshold = 30.0,               # 订单滑点异常的阈值，单位是 bps，即 0.01%
abnormal_order_latency_threshold = 600,                   # 订单下单延迟异常检查的阈值，单位是 ms
max_account_leverage = 0.05,                            # 全部账户最大持仓杠杆约束
max_symbol_leverage = 0.05,                             # symbol 最大持仓杠杆约束
abnormal_position_exposure_threshold = 0.05,            # 持仓数量的敞口暴露异常阈值, 0.05 表示 5% 
available_balance_warning_threshold = 0.2,              # 可用资金的告警阈值，0.2 表示 20% 的阈值
available_balance_unbalance_threshold = 1.2,            # 可用资金不平衡的阈值， 1.2 表示两个两个交易所的可用资金相除比例超过 1.2 认为显著不平衡
total_drawdown_threshold = 0.95,                        # 资金回撤的阈值，0.95 表示资金回撤超过 5% 认为显著回撤
intraday_loss_threshold = 1000.0,                       # 日内亏损停止交易的阈值，-1000.0 表示日内亏损超过 1000U 认为显著亏损
liquidation_price_warning_threshold = 1,                # symbol 价格距离强平价格的报警阈值，1 表示价格距离强平价格超过 100% 认为显著异常
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
        self.fundings = [
            {symbol: {"funding_rate": 0, "funding_interval": 8,
                        "next_funding_at": 0} for symbol in self.symbols[idx]}
            for idx in range(self.base_index)
        ]

        # 账户变量
        self.balances = [{} for _ in range(self.base_index)]
        self.pm = HedgePositionManager(self.symbols[0], self.base_index)
        self.statistics = Statistics()
        self.order_manager = OrderManager()

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

            init_available_balance, init_balance = self.get_total_init_balance()
            self.statistics.start_balance = init_balance
            self.statistics.today_start_balance = init_balance
            self.statistics.max_balance = init_balance
            self.statistics.now_balance = init_balance

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
        subs.append(
            {
                "sub": {
                    "SubscribeTimer": {
                        "update_interval": {"secs": 5, "nanos": 0},
                        "name": "global_risk_check",  # 每 5 秒进行一次全局风控检查
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

        if not self.has_pos:
            self.create_position(index, symbol)

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
        if timer_name == "global_risk_check":
            self.trader.log(f"账户的资金：{self.balances}", level="INFO", color="blue")
            risk_signal = self.risk_manager.check_global_risk()
            if risk_signal and not risk_signal.is_empty():
                print(f"global_risk_check 风控告警: {risk_signal.to_dict()}")
                print(f"---------------------------------------------------------")

    def get_total_init_balance(self):
        total_available_balance = 0
        total_balance = 0
        for i in self.balances:
            total_available_balance += i['available_balance']
            total_balance += i['balance']
        return (total_available_balance, total_balance)

# ============================= 创建仓位函数 ====================================
    def create_position(self, index, symbol):
        cid = order_cid = self.trader.create_cid(self.ex_map[index])
        symbol = self.symbols[index][0]
        side = "Buy"
        pos_side = "Long"
        price = self.bbo[index][symbol][0]
        amount = 5 / price
        reduce_only = False
        order = {
            "cid": cid,  # 客户端订单ID
            "symbol": symbol,
            "order_type": "Market",  # 市价单
            "side": side,  # Buy/Sell
            "pos_side": pos_side,  # 单向持仓模式
            "time_in_force": "IOC",  # 立即成交或全部取消
            "price": price,
            "amount": amount,
            "reduce_only": reduce_only,
        }
        params = {'is_dual_side': False, 
                  "market_order_mode": "Normal",
                  "process_amount": "Round",
                  "process_price": "Round"
                  }
        result = self.trader.place_order(index, order, params=params)
        if 'Ok' in result:
            self.trader.log(f"创建仓位成功: {symbol}", level="INFO", color="blue")
            self.has_pos = True
            self.trader.log(f"---------------------------------------------------------")
            return True
        return False