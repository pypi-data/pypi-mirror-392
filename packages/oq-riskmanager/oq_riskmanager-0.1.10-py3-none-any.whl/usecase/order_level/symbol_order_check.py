

from typing import Any, Dict, Optional, Tuple
import time

# 代码用于检测 symbol 的订单异常情况（单笔视角）


def symbol_order_failure_check(symbol: str, order_receipt: Dict[str, Any]) -> bool:
    """
    检查 symbol 的订单回执是否失败
    """
    if not isinstance(order_receipt, dict):
        return False
    return "Ok" in order_receipt
    

def symbol_order_slippage_check(
    symbol: str,
    order: Dict[str, Any],
    threshold_bps: float = 30.0,
) -> Tuple[bool, Optional[float], float]:
    """
    Symbol 层面滑点检查（单笔视角）
    - 使用下单价与成交均价计算滑点（bps）
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
    

def symbol_order_latency_check(
    symbol: str,
    order: Dict[str, Any],
    threshold_ms: int = 600,
) -> Tuple[bool, Optional[int], int]:
    """
    Symbol 层面下单延迟检查（单笔视角）
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