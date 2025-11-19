

from typing import Any, Dict, Optional, Tuple
import time

# 代码用于计算交易所的订单异常情况，例如订单连续失败，订单连续产生较大下单延迟等。


def exchange_order_failure_check(index: int, order_receipt: Dict[str, Any]) -> bool:
    """
    检查交易所订单回执是否失败
    """
    if not isinstance(order_receipt, dict):
        return False
    return "Ok" in order_receipt
    

def exchange_order_slippage_check(
    order: Dict[str, Any],
    threshold_bps: float = 30.0,
) -> Tuple[bool, Optional[float], float]:
    """
    交易所层面滑点检查
    - 以下单 price 与成交均价 filled_avg_price 计算滑点（bps）
    - threshold_bps 为滑点告警阈值（单位：bps）
    """
    try:
        price = float(order.get("price"))
        filled = float(order.get("filled", 0.0) or 0.0)
        filled_avg_price = float(order.get("filled_avg_price")) if filled > 0 else None
    except Exception:
        return False, None, threshold_bps

    if not price or filled_avg_price is None or price <= 0:
        return False, None, threshold_bps
    slippage_bps = abs(filled_avg_price - price) / price * 10000.0
    return slippage_bps > threshold_bps, slippage_bps, threshold_bps
    

def exchange_order_latency_check(
    order: Dict[str, Any],
    threshold_ms: int = 600,
) -> Tuple[bool, Optional[int], int]:
    """
    交易所层面下单延迟检查
    - 以当前时间与 order['timestamp'] 相差计算下单延迟
    - threshold_ms 为延迟告警阈值（单位：毫秒）
    """
    try:
        ts = int(order.get("timestamp"))
    except Exception:
        return False, None, threshold_ms
    now_ms = int(time.time() * 1000)
    latency = max(0, now_ms - ts)
    return latency > threshold_ms, latency, threshold_ms

