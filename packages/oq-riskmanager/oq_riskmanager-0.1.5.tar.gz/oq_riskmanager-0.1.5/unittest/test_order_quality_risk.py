import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from typing import Any, Dict

from risk_manager import RiskManager


class TestOrderQualityRisk(unittest.TestCase):
    def setUp(self):
        self.rm = RiskManager()
        self.base = 1_000_000_000_000
        self.now = self.base
        self.rm._now_ms = lambda: self.now
        self.rm.ex_map = {0: "BinanceSwap", 1: "OkxSwap", "BinanceSwap": 0, "OkxSwap": 1}
        self.symbol = "BTC_USDT"
        self.exchange = "BINANCE"

    def make_order(self, ts_offset_ms: int, price: float, filled_avg_price: float) -> Dict[str, Any]:
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timestamp": self.base + ts_offset_ms,
            "price": price,
            "filled": 10.0,
            "filled_avg_price": filled_avg_price,
        }

    def test_slippage_window_trigger(self):
        # 10秒内滑点>15bps累计5次后触发
        for i in range(4):
            self.rm.latest_order = self.make_order(0, 100.0, 100.3)  # 30 bps
            rs = self.rm.check_order_risk()
            self.assertTrue(rs.is_empty())
            self.now += 1000
        self.rm.latest_order = self.make_order(0, 100.0, 100.3)
        rs = self.rm.check_order_risk()
        self.assertFalse(rs.is_empty())

    def test_latency_window_trigger(self):
        # 10秒内延迟>800ms累计5次后触发
        for i in range(4):
            self.rm.latest_order = {
                "exchange": self.exchange,
                "symbol": self.symbol,
                "timestamp": self.base - 2000,  # 让延迟>800ms
                "price": 100.0,
                "filled": 0.0,
            }
            rs = self.rm.check_order_risk()
            self.assertTrue(rs.is_empty())
            self.now += 1000
        self.rm.latest_order = {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timestamp": self.base - 2000,
            "price": 100.0,
            "filled": 0.0,
        }
        rs = self.rm.check_order_risk()
        self.assertFalse(rs.is_empty())


if __name__ == "__main__":
    unittest.main()


