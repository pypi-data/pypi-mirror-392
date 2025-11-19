import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from typing import Any, Dict
from risk_manager import RiskManager


def simulate_order_quality() -> None:
    rm = RiskManager()
    base = 1_000_000_000_000
    now = base
    rm._now_ms = lambda: now

    symbol = "BTC_USDT"
    exchange = "BinanceSwap"

    # 首次超过阈值（滑点>15bps），触发窗口创建
    def make_order(ts_offset_ms: int, price: float, filled_avg_price: float) -> Dict[str, Any]:
        return {
            "exchange": exchange,
            "symbol": symbol,
            "timestamp": base + ts_offset_ms,
            "price": price,
            "filled": 10.0,
            "filled_avg_price": filled_avg_price,
        }

    print("场景：10秒内滑点超阈值累计5次, 触发 RiskSignal")
    for i in range(5):
        rm.latest_order = make_order(ts_offset_ms=0, price=100.0, filled_avg_price=100.3)  # 30bps
        rs = rm.check_order_risk()
        print(f"第{i+1}次, signal={rs.to_dict() if rs else {}}")
        now += 1000

    print("场景：延迟超阈值累计5次, 触发 RiskSignal")
    now = base
    for i in range(5):
        rm.latest_order = {
            "exchange": exchange,
            "symbol": symbol,
            "timestamp": base - 2000,  # 人为拉大延迟>800ms
            "price": 100.0,
            "filled": 0.0,
        }
        rs = rm.check_order_risk()
        print(f"第{i+1}次, signal={rs.to_dict() if rs else {}}")
        now += 1000


if __name__ == "__main__":
    simulate_order_quality()


