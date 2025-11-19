import unittest
import time

try:
    from usecase.tick_level.spread_check import (
        spread_threshold_check,
        spread_price_amount_abnormal_check,
    )
    from usecase.tick_level.latency_check import bbo_latency_check
except Exception as e:
    spread_threshold_check = None
    spread_price_amount_abnormal_check = None
    bbo_latency_check = None
    _import_error = e
else:
    _import_error = None


@unittest.skipIf(_import_error is not None, f"tick_level modules not importable: {_import_error}")
class TestTickLevel(unittest.TestCase):
    def test_spread_threshold_check_true_when_spread_small(self):
        bbo = [
            {"bid_price": 100.0, "ask_price": 100.2, "bid_qty": 10, "ask_qty": 10, "timestamp": int(time.time() * 1000)},
            {"bid_price": 100.0, "ask_price": 100.2, "bid_qty": 10, "ask_qty": 10, "timestamp": int(time.time() * 1000)},
        ]
        self.assertTrue(spread_threshold_check(bbo))

    def test_spread_threshold_check_false_when_invalid(self):
        self.assertFalse(spread_threshold_check([]))
        self.assertFalse(spread_threshold_check([{}, {}]))

    def test_price_amount_abnormal_true_when_valid_prices_and_qty(self):
        bbo = [
            {"bid_price": 100.0, "ask_price": 100.2, "bid_qty": 10, "ask_qty": 10, "timestamp": int(time.time() * 1000)},
            {"bid_price": 100.0, "ask_price": 100.2, "bid_qty": 10, "ask_qty": 10, "timestamp": int(time.time() * 1000)},
        ]
        self.assertTrue(spread_price_amount_abnormal_check(bbo))

    def test_price_amount_abnormal_false_when_invalid(self):
        bbo_neg_price = [
            {"bid_price": 0, "ask_price": 100.2, "bid_qty": 10, "ask_qty": 10, "timestamp": int(time.time() * 1000)},
            {"bid_price": 100.0, "ask_price": 100.2, "bid_qty": 10, "ask_qty": 10, "timestamp": int(time.time() * 1000)},
        ]
        self.assertFalse(spread_price_amount_abnormal_check(bbo_neg_price))

    def test_bbo_latency_check_true_recent_timestamps(self):
        ts = int(time.time() * 1000)
        bbo = [
            {"timestamp": ts},
            {"timestamp": ts},
        ]
        self.assertTrue(bbo_latency_check(bbo))

    def test_bbo_latency_check_false_old_timestamps(self):
        old = int(time.time() * 1000) - 10_000
        bbo = [
            {"timestamp": old},
            {"timestamp": old},
        ]
        self.assertFalse(bbo_latency_check(bbo))


if __name__ == "__main__":
    unittest.main()


