import unittest
import time

try:
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
except Exception as e:
    exchange_order_slippage_check = None
    exchange_order_latency_check = None
    exchange_order_failure_check = None
    symbol_order_slippage_check = None
    symbol_order_latency_check = None
    symbol_order_failure_check = None
    _import_error = e
else:
    _import_error = None


@unittest.skipIf(_import_error is not None, f"order_level modules not importable: {_import_error}")
class TestOrderLevelChecks(unittest.TestCase):
    def test_exchange_slippage_exceeds(self):
        order = {"price": 100.0, "filled": 10.0, "filled_avg_price": 100.3}
        bad, bps, thr = exchange_order_slippage_check(order, threshold_bps=15.0)
        self.assertTrue(bad)
        self.assertGreater(bps, thr)

    def test_exchange_latency_exceeds(self):
        old = int(time.time() * 1000) - 2000
        order = {"timestamp": old}
        bad, ms, thr = exchange_order_latency_check(order, threshold_ms=800)
        self.assertTrue(bad)
        self.assertGreater(ms, thr)

    def test_symbol_slippage_exceeds(self):
        order = {"price": 100.0, "filled": 10.0, "filled_avg_price": 100.3}
        bad, bps, thr = symbol_order_slippage_check("BTC_USDT", order, threshold_bps=15.0)
        self.assertTrue(bad)
        self.assertGreater(bps, thr)

    def test_symbol_latency_exceeds(self):
        old = int(time.time() * 1000) - 2000
        order = {"timestamp": old}
        bad, ms, thr = symbol_order_latency_check("BTC_USDT", order, threshold_ms=800)
        self.assertTrue(bad)
        self.assertGreater(ms, thr)

    def test_failure_checks_receipt(self):
        ok_receipt = {"Ok": {}}
        err_receipt = {"Err": {}}
        self.assertTrue(exchange_order_failure_check(0, ok_receipt))
        self.assertTrue(symbol_order_failure_check("BTC_USDT", ok_receipt))
        self.assertFalse(exchange_order_failure_check(0, err_receipt))
        self.assertFalse(symbol_order_failure_check("BTC_USDT", err_receipt))


if __name__ == "__main__":
    unittest.main()


