import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from utils.statistics import Statistics


def available_balance_ratio_check(
    balances: List[Dict[str, Any]],
    available_balance_warning_threshold: float = 0.2,
) -> bool:
    """
    检查可用资金是否正常
    """
    if not balances or len(balances) < 2:
        return False
    
    # 检查数据完整性
    if not balances[0] or 'balance' not in balances[0] or 'available_balance' not in balances[0]:
        return False
    if not balances[1] or 'balance' not in balances[1] or 'available_balance' not in balances[1]:
        return False
    
    taker_balance = balances[0]['balance']
    taker_available_balance = balances[0]['available_balance']
    maker_balance = balances[1]['balance']
    maker_available_balance = balances[1]['available_balance']
    
    # 检查余额是否为0，避免除零错误
    if taker_balance == 0 or maker_balance == 0:
        return False

    if (
        taker_available_balance / taker_balance <= available_balance_warning_threshold
        or maker_available_balance / maker_balance <= available_balance_warning_threshold
    ):
        return False

    return True

def balance_zero_check(balances: List[Dict[str, Any]]) -> bool:
    """
    检查可用资金或全部资金是否为 0 
    """
    if not balances or len(balances) < 2:
        return False

    # 检查数据完整性
    if not balances[0] or 'available_balance' not in balances[0]:
        return False
    if not balances[1] or 'available_balance' not in balances[1]:
        return False

    taker_available_balance = balances[0]['available_balance']
    maker_available_balance = balances[1]['available_balance']

    if taker_available_balance == 0 or maker_available_balance == 0:
        return False
    
    return True

def balance_unbalance_check(
    balances: List[Dict[str, Any]],
    available_balance_unbalance_threshold: float = 1.2,
) -> bool:
    """
    检查可用资金或全部资金是否不平衡
    """
    if not balances or len(balances) < 2:
        return False

    # 检查数据完整性
    if not balances[0] or 'available_balance' not in balances[0]:
        return False
    if not balances[1] or 'available_balance' not in balances[1]:
        return False

    taker_available_balance = balances[0]['available_balance']
    maker_available_balance = balances[1]['available_balance']
    
    # 检查余额是否为0，避免除零错误
    if taker_available_balance == 0 or maker_available_balance == 0:
        return False

    # 两个交易所的可用资金查了 20% 以上，认为可用资金不平衡
    if (
        taker_available_balance / maker_available_balance > available_balance_unbalance_threshold
        or maker_available_balance / taker_available_balance > available_balance_unbalance_threshold
    ):
        return False
    
    return True

def balance_drawdown_check(
    statistics: Statistics,
    total_drawdown_threshold: float = 0.95,
) -> bool:
    """
    检查资金是否回撤达到阈值
    """
    if not statistics:
        return False

    if statistics.now_balance / statistics.max_balance <= total_drawdown_threshold:
        return False
    
    return True


def intraday_profit_threshold_check(
    statistics: Statistics,
    intraday_loss_threshold: float = 1000.0,
) -> bool:
    """
    检查当日收益是否超过阈值
    """
    if not statistics:
        return False

    today_pnl = statistics.now_balance - statistics.today_start_balance
    
    if today_pnl <= -intraday_loss_threshold:
        return False
    
    return True
    
    