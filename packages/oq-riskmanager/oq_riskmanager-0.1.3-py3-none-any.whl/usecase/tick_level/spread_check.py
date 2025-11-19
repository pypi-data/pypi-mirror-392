from typing import List, Dict, Any
import time


def spread_threshold_check(
    bbo: List[Dict[str, Any]],
    abnormal_spread_threshold: float = 0.2,
) -> bool:
    """
    检查相同 symbol 的行情价差是否超过阈值
    """
    if not bbo or len(bbo) != 2 or not bbo[0] or not bbo[1]:
        return False
    
    taker_bbo = bbo[0]
    maker_bbo = bbo[1]

    taker_bid_price = taker_bbo.get('bid_price', 0)
    taker_ask_price = taker_bbo.get('ask_price', 0)
    maker_bid_price = maker_bbo.get('bid_price', 0)
    maker_ask_price = maker_bbo.get('ask_price', 0)

    long_spread = abs(taker_bid_price - maker_ask_price) / maker_ask_price
    short_spread = abs(taker_ask_price - maker_bid_price) / maker_bid_price
    if long_spread <= abnormal_spread_threshold or short_spread <= abnormal_spread_threshold:
        return True
    return False

def spread_price_amount_abnormal_check(bbo: List[Dict[str, Any]]) -> bool:
    """
    检查相同 symbol 的行情价格和数量是否异常
    """
    if not bbo or len(bbo) != 2 or not bbo[0] or not bbo[1]:
        return False
    
    taker_bbo = bbo[0]
    maker_bbo = bbo[1]
    
    taker_bid_price = taker_bbo.get('bid_price', 0)
    taker_ask_price = taker_bbo.get('ask_price', 0)
    maker_bid_price = maker_bbo.get('bid_price', 0)
    maker_ask_price = maker_bbo.get('ask_price', 0)

    taker_bid_qty = taker_bbo.get('bid_qty', 0)
    taker_ask_qty = taker_bbo.get('ask_qty', 0)
    maker_bid_qty = maker_bbo.get('bid_qty', 0)
    maker_ask_qty = maker_bbo.get('ask_qty', 0)

    if taker_bid_price <= 0 or taker_ask_price <= 0 or maker_bid_price <= 0 or maker_ask_price <= 0:
        return False

    if taker_bid_qty <= 0 or taker_ask_qty <= 0 or maker_bid_qty <= 0 or maker_ask_qty <= 0:
        return False
    
    if taker_bid_price >= taker_ask_price or maker_bid_price >= maker_ask_price:
        return False
    
    return True


