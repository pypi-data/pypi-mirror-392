import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from utils.position_manager import HedgePositionManager


def leverage_check(
    symbols: List[str],
    bbo: List[Dict[str, Any]],
    balances: List[Dict[str, Any]],
    position_manager: HedgePositionManager,
    max_symbol_leverage: float = 1.0,
    max_account_leverage: float = 8.0,
) -> bool:
    """
    同时检查 symbol 和 账户杠杆是否正常
    """
    result = {'account_leverage': False, 'symbol_leverage': {}}
    if not symbols or not balances or len(balances) < 2:
        return result
    
    # 检查数据完整性
    if not balances[0] or 'balance' not in balances[0]:
        return result
    if not balances[1] or 'balance' not in balances[1]:
        return result
    
    taker_balance = balances[0]['balance']
    maker_balance = balances[1]['balance']
    
    # 检查余额是否为0，避免除零错误
    if taker_balance == 0 and maker_balance == 0:
        return result
    
    total_notional = 0

    for symbol in symbols:
        if symbol not in bbo[0] or symbol not in bbo[1]:
            continue

        taker_bbo = bbo[0][symbol]
        maker_bbo = bbo[1][symbol]

        taker_mid_price = (taker_bbo[0] + taker_bbo[2]) / 2
        maker_mid_price = (maker_bbo[0] + maker_bbo[2]) / 2
        
        pos_0, pos_1 = position_manager.get_hedge_positions(symbol)
        pos_0_size = pos_0.amount
        pos_1_size = pos_1.amount

        if pos_0_size == 0 or pos_1_size == 0:
            continue

        taker_notional = pos_0_size * taker_mid_price
        maker_notional = pos_1_size * maker_mid_price
        total_notional += taker_notional + maker_notional

        if (taker_notional + maker_notional) / (taker_balance + maker_balance) >= max_symbol_leverage:
            # 当 symbol 的持仓名义市值超过阈值，则添加到风控结果。
            result['symbol_leverage'][symbol] = True
        
        if total_notional / (taker_balance + maker_balance) >= max_account_leverage:
            result['account_leverage'] = True

    return result

