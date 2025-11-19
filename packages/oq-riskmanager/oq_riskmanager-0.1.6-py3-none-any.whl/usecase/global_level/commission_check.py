from typing import Dict, Any

def commission_check(previous_commission: Dict[str, Any], current_commission: Dict[str, Any]) -> bool:
    """
    检查交易所手续费是否发生变化，交易所手续费变高了。
    openquant 返回的手续费率的格式是：{'buyer': 0.0, 'maker': 0.0002, 'seller': 0.0, 'taker': 0.0005} 
    """
    if not previous_commission or not current_commission:
        return False
    
    current_maker_commission = current_commission['maker']
    current_taker_commission = current_commission['taker']

    previous_maker_commission = previous_commission['maker']
    previous_taker_commission = previous_commission['taker']

    if current_maker_commission > previous_maker_commission or current_taker_commission > previous_taker_commission:
        return False
    
    return True

