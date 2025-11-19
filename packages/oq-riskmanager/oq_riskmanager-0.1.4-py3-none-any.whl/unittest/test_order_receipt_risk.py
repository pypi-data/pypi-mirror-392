import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from typing import Any, Dict

from risk_manager import RiskManager


class TestOrderReceiptRisk(unittest.TestCase):
    def setUp(self):
        self.rm = RiskManager()
        self.rm.ex_map = {0: "BinanceSwap", 1: "OkxSwap", "BinanceSwap": 0, "OkxSwap": 1}
        self.base = 1_000_000_000_000
        self.now = self.base
        self.rm._now_ms = lambda: self.now
        self.symbol = "BTC_USDT"
        self.err_receipt: Dict[str, Any] = {"Err": {"code": 2000, "error": "mock"}}

    def test_trigger_after_5_within_10s(self):
        # 前4次不触发，第5次触发
        for i in range(4):
            rs = self.rm.check_order_receipt_risk(0, self.symbol, self.err_receipt)
            self.assertTrue(rs.is_empty())
            self.now += 1000
        rs = self.rm.check_order_receipt_risk(0, self.symbol, self.err_receipt)
        self.assertFalse(rs.is_empty())
        out = rs.to_dict()
        self.assertIn("signals", out)
        self.assertTrue(out["signals"]["order"])

    def test_expire_if_not_enough_hits(self):
        # 4次，每次+4s，超过10s窗口累计不足5次， 超过窗口时间且未达阈值，销毁旧窗口，重新从1开始，不触发
        for i in range(4):
            rs = self.rm.check_order_receipt_risk(0, self.symbol, self.err_receipt)
            self.assertTrue(rs.is_empty())
            self.now += 4000
        # 窗口应当已过期，再次开始累计，从1开始，不触发
        rs = self.rm.check_order_receipt_risk(0, self.symbol, self.err_receipt)
        self.assertTrue(rs.is_empty())


if __name__ == "__main__":
    unittest.main()


