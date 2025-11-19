from typing import List, Dict, Any
import time


def bbo_latency_check(
    bbo: List[Dict[str, Any]],
    abnormal_bbo_latency_threshold: int = 5000,
) -> bool:
    """
    检查相同 symbol 的行情延迟是否异常
    """
    if not bbo or len(bbo) != 2 or not bbo[0] or not bbo[1]:
        return False
    
    taker_bbo = bbo[0]
    maker_bbo = bbo[1]
    
    taker_timestamp = taker_bbo.get('timestamp', 0)
    maker_timestamp = maker_bbo.get('timestamp', 0)

    current_timestamp = int(time.time() * 1000)

    if (
        abs(taker_timestamp - current_timestamp) > abnormal_bbo_latency_threshold
        or abs(maker_timestamp - current_timestamp) > abnormal_bbo_latency_threshold
    ):
        return False

    return True
