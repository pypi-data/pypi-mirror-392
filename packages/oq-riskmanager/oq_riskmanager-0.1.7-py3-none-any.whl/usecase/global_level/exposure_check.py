import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from utils.position_manager import HedgePositionManager


def symbol_exposure_check(
    symbols: List[str],
    position_manager: HedgePositionManager,
    abnormal_position_exposure_threshold: float = 0.05,
) -> bool:
    """
    检查 symbol 的敞口是否正常
    如果检查 symbol 的仓位发生了较大敞口，则应该将 symbol 加到 result 中返回
    """
    result = {'exposure': list()}
    if not symbols or len(symbols) <= 0:
        return result
    
    for symbol in symbols:
        pos_0, pos_1 = position_manager.get_hedge_positions(symbol)
        pos_0_size = pos_0.amount
        pos_1_size = pos_1.amount

        pos_size_delta = abs(pos_0_size - pos_1_size)

        if pos_1_size != 0 and pos_size_delta / pos_1_size > abnormal_position_exposure_threshold:
            result['exposure'].append(symbol)
        elif (pos_1_size == 0 and pos_0_size != 0) or (pos_1_size != 0 and pos_0_size == 0):
            result['exposure'].append(symbol)
        
    return result

def symbol_notional_exposure_check(
    symbols: List[str],
    bbo: List[Dict[str, Any]],
    position_manager: HedgePositionManager,
    abnormal_position_exposure_threshold: float = 0.05,
) -> bool:
    """
    检查 symbol 的名义市值敞口是否正常
    如果检查 symbol 的仓位发生了较大敞口，则应该将 symbol 加到 result 中返回
    """
    result = {'exposure': list()}
    if not symbols or not position_manager:
        return result
    
    for symbol in symbols:
        if symbol not in bbo[0] or symbol not in bbo[1]:
            continue
        pos_0, pos_1 = position_manager.get_hedge_positions(symbol)
        taker_notional = pos_0.amount * (bbo[0][symbol][2] + bbo[0][symbol][0]) * 0.5
        maker_notional = pos_1.amount * (bbo[1][symbol][2] + bbo[1][symbol][0]) * 0.5

        if (maker_notional != 0 and taker_notional / maker_notional - 1 > abnormal_position_exposure_threshold) \
            or (taker_notional != 0 and maker_notional / taker_notional - 1 > abnormal_position_exposure_threshold):
            result['exposure'].append(symbol)
        elif (maker_notional == 0 and taker_notional != 0) or (taker_notional == 0 and maker_notional != 0):
            result['exposure'].append(symbol)
    
    return result
    

def symbol_single_leg_check(symbols: List[str], position_manager: HedgePositionManager) -> bool:
    """
    检查 symbol 的单腿是否正常
    如果检查 symbol 发生了单腿，则应该将该 symbol 加到 result 中返回
    """
    result = {'single_leg': list()}
    if not symbols or len(symbols) <= 0:
        return result

    for symbol in symbols:
        pos_0, pos_1 = position_manager.get_hedge_positions(symbol)
        pos_0_size = pos_0.amount
        pos_1_size = pos_1.amount

        if (pos_0_size != 0 and pos_1_size == 0) or (pos_0_size == 0 and pos_1_size != 0):
            result['single_leg'].append(symbol)
    
    return result