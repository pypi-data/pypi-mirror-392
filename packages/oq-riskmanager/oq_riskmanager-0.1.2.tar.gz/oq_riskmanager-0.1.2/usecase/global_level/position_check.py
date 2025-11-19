from typing import List, Dict, Any


def position_liquidation_price_check(
    positions: List[List[Dict[str, Any]]],
    bbo: List[Dict[str, Any]],
    liquidation_price_warning_threshold: float = 0.01,
) -> bool:
    """
    检查所有 position 当前 symbol 的价格是否接近强制平仓价格。
    position 是 [[{}] [{}]] 来存储全部交易所的 全部 position
    需要先遍历交易所，再遍历 position，再获取 bbo 数据
    """
    result = {'Info': dict()}

    exchange_count = len(positions)

    for exchange in range(exchange_count):
        for position in positions[exchange]:
            symbol = position['symbol']
            mid_price = (bbo[exchange][symbol]['bid_price'] + bbo[exchange][symbol]['ask_price']) / 2
            if (
                abs(position['liquidation_price'] - mid_price) / position['liquidation_price']
                > liquidation_price_warning_threshold
            ):
                result['Info'][symbol] = {
                    'liquidation_price': position['liquidation_price'],
                    'mid_price': mid_price,
                }

    return result