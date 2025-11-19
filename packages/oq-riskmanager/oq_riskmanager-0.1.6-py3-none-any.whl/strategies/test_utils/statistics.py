import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

class Stats:
    __slots__ = (
        "volume",
        "count",
        "profit_count",
        "loss_count",
        "win_rate",
        "profit_value",
        "loss_value",
        "net_pnl",  # 价差净收益
        "base_funding_fee",
        "hedge_funding_fee",
        "funding_pnl",
        "leg_count",
        "leg_volume",
        "leg_pnl",
        "total_pnl",  # net_pnl + funding_pnl + leg_pnl
        "fee",
        "rebate",
    )

    def __init__(self):
        self.volume = 0.0
        self.count = 0
        self.profit_count = 0
        self.loss_count = 0
        self.win_rate = 0.0
        self.profit_value = 0.0
        self.loss_value = 0.0
        self.net_pnl = 0.0
        self.base_funding_fee = 0.0
        self.hedge_funding_fee = 0.0
        self.funding_pnl = 0.0
        self.leg_count = 0
        self.leg_volume = 0.0
        self.leg_pnl = 0.0
        self.total_pnl = 0.0
        self.fee = 0.0
        self.rebate = 0.0


class Statistics:
    def __init__(self, symbols=['BTC_USDT'], balance=10000, fee_rate=0.0006, exchange_len=3):
        self.now_balance = balance
        self.max_balance = balance
        self.today_start_balance = balance

        self.start_balance = balance
        self.start_time = int(time.time() * 1000)

        self.fee_rate = fee_rate

        self.symbol_stats = {symbol: Stats() for symbol in symbols}

        self.total_stats = Stats()

        if exchange_len:
            self.exchange_info = {account_id: {"init_balance":0, "max_balance":0, "now_balance":0, "available_balance":0, "total_pnl":0} for account_id in range(exchange_len)}
        

    def update_today_balance(self, balance):
        self.today_start_balance = balance

    def update_exchange_info(self, account_id, balance):
        if account_id not in self.exchange_info:
            self.exchange_info[account_id] = {"init_balance":0, "max_balance":0, "now_balance":0, "available_balance":0, "total_pnl":0}
        if self.exchange_info[account_id]["init_balance"] == 0:
            self.exchange_info[account_id]["init_balance"] = balance["balance"]
        self.exchange_info[account_id]["now_balance"] = balance["balance"]
        self.exchange_info[account_id]["available_balance"] = balance["available_balance"]
        if balance["balance"] >= self.exchange_info[account_id]["max_balance"]:
            self.exchange_info[account_id]["max_balance"] = balance["balance"]
        self.exchange_info[account_id]["total_pnl"] = self.exchange_info[account_id]["now_balance"] - self.exchange_info[account_id]["init_balance"]

    def update_balance(self, now_balance):
        self.now_balance = now_balance
        if self.max_balance < now_balance:
            self.max_balance = now_balance

    
