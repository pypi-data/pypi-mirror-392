import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from typing import Any, Dict
from risk_manager import RiskManager


def simulate_receipt_failures() -> None:
    rm = RiskManager()
    # 映射 index->exchange 名称，便于测试输出
    rm.ex_map = {0: "BinanceSwap", 1: "OkxSwap", "BinanceSwap": 0, "OkxSwap": 1}

    base = 1_000_000_000_000  # 虚拟时间基准（ms）
    now = base
    rm._now_ms = lambda: now  # 覆盖时间函数，便于场景控制

    symbol = "BTC_USDT"
    err_receipt: Dict[str, Any] = {"Err": {"code": 2000, "error": "mock"}}

    print("场景：10秒内连续5次失败, 触发 RiskSignal")
    for i in range(5):
        rs = rm.check_order_receipt_risk(0, symbol, err_receipt)
        print(f"第{i+1}次, signal={rs.to_dict() if rs else {}}")
        now += 1000  # 每次+1s，10秒内累计

    print("场景：超出10秒窗口但不足5次, 不触发")
    now = base
    for i in range(4):
        rs = rm.check_order_receipt_risk(0, symbol, err_receipt)
        print(f"第{i+1}次, signal={rs.to_dict() if rs else {}}")
        now += 4000  # 每次+4s，超过窗口累计不足5次


if __name__ == "__main__":
    simulate_receipt_failures()


