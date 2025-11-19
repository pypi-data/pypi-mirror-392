import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.order_manager import Order
from typing import Tuple

class Position:
    def __init__(self):
        self.amount = 10
        self.avg_price = 0
        self.side = ''
        self.hedge_index = 0
        self.update_time = 0

    def __repr__(self):
        return f"Position(amount={self.amount}, avg_price={self.avg_price}, side={self.side}, hedge_index={self.hedge_index})"

class HedgePositionManager:
    def __init__(self, symbols: list[str] = ['BTC_USDT'], base_index: int = 2):
        print(f"Mock HedgePositionManager class 初始化")

        self.symbols = symbols
        self.base_index = 2
        self.positions = [{symbol: Position() for symbol in self.symbols} for _ in range(self.base_index)]
        self.amount_mismatch_counts = [{symbol: 0 for symbol in symbols} for _ in range(base_index)]

    def update_positions(self, index, positions, init_pos=False):
        """
        更新交易所 index 的持仓列表。
        - init_pos=True: 直接按原逻辑更新（用于初始化），不做连续误差判断。
        - init_pos=False: 当 pos['amount'] 与本地值不相等时，累计误差次数；仅当连续2次不相等时才进行更新；
                          如果上次不相等这次相等，则将误差次数归 0。
        """
        for pos in positions:
            symbol = pos["symbol"]
            # 方案B：过滤未订阅且 amount 为 0 的 symbol（跳过无效条目）
            if symbol not in self.symbols:
                continue

            # 确保当前 index 的 symbol 初始化
            if symbol not in self.positions[index]:
                # 初始化未知 symbol
                self.positions[index][symbol] = Position()
            if symbol not in self.amount_mismatch_counts[index]:
                self.amount_mismatch_counts[index][symbol] = 0

            local_pos: LocalPosition = self.positions[index][symbol]

            if init_pos:
                # 原始更新逻辑（不启用误差门控）
                local_pos.amount = pos["amount"]
                if pos["amount"] != 0:
                    local_pos.avg_price = pos["entry_price"]
                    local_pos.side = pos["side"]
                local_pos.hedge_index = 0
                if index:
                    self.positions[0][symbol].hedge_index = index
                if "timestamp" in pos:
                    local_pos.update_time = pos["timestamp"]
                elif 'utime' in pos:
                    local_pos.update_time = pos['utime']
                local_pos.unrealized_pnl = pos['unrealized_pnl']
                local_pos.return_ratio = local_pos.unrealized_pnl / (local_pos.avg_price * local_pos.amount) if local_pos.amount != 0 and local_pos.avg_price != 0 else 0.0
                self.positions[index][symbol] = local_pos
                # 初始化路径下重置计数
                self.amount_mismatch_counts[index][symbol] = 0
                continue

            # 误差门控逻辑
            incoming_amount = pos["amount"]
            current_amount = local_pos.amount
            incoming_entry_price = pos["entry_price"]
            current_entry_price = local_pos.avg_price
            mismatch = (incoming_amount != current_amount) or (incoming_entry_price != current_entry_price)

            if mismatch:
                # 累计误差
                self.amount_mismatch_counts[index][symbol] = self.amount_mismatch_counts[index].get(symbol, 0) + 1
                if self.amount_mismatch_counts[index][symbol] >= 2:
                    # 连续两次不相等，执行更新并清零计数
                    local_pos.amount = incoming_amount
                    if incoming_amount != 0:
                        local_pos.avg_price = pos["entry_price"]
                        local_pos.side = pos["side"]
                    # 其他字段仍然更新
                    local_pos.hedge_index = 0
                    if index:
                        self.positions[0][symbol].hedge_index = index
                    if "timestamp" in pos:
                        local_pos.update_time = pos["timestamp"]
                    elif 'utime' in pos:
                        local_pos.update_time = pos['utime']
                    local_pos.unrealized_pnl = pos['unrealized_pnl']
                    local_pos.return_ratio = local_pos.unrealized_pnl / (local_pos.avg_price * local_pos.amount) if local_pos.amount != 0 and local_pos.avg_price != 0 else 0.0
                    self.positions[index][symbol] = local_pos
                    # 清零计数
                    self.amount_mismatch_counts[index][symbol] = 0
                else:
                    # 未达到阈值，仅计数，不更新
                    continue
            else:
                # 相等时，如之前有误差计数则归 0，并继续按正常逻辑更新非金额字段
                if self.amount_mismatch_counts[index].get(symbol, 0) != 0:
                    self.amount_mismatch_counts[index][symbol] = 0
                # 相等情况下，更新除 amount/avg_price/side 的其余字段（保持原有规则）
                if "timestamp" in pos:
                    local_pos.update_time = pos["timestamp"]
                elif 'utime' in pos:
                    local_pos.update_time = pos['utime']
                local_pos.unrealized_pnl = pos['unrealized_pnl']
                local_pos.return_ratio = local_pos.unrealized_pnl / (local_pos.avg_price * local_pos.amount) if local_pos.amount != 0 and local_pos.avg_price != 0 else 0.0
                local_pos.hedge_index = 0
                if index:
                    self.positions[0][symbol].hedge_index = index
                self.positions[index][symbol] = local_pos

    def update_position_by_order(self, index, local_order: Order, trader=None):
        # 改进时间戳检查逻辑，确保持仓成本价更新不会失败
        local_position = self.positions[index][local_order.symbol]
        
        # 如果订单时间戳比持仓更新时间早，但有成交数据，仍然允许更新
        # 这是因为订单回调可能比持仓回调先到达
        if local_position.update_time >= local_order.ack_time and local_order.filled_qty == 0:
            # 只有当订单没有成交且时间戳更早时才跳过更新
            return 0.0

        # 记录更新前的状态
        old_amount = local_position.amount
        old_avg_price = local_position.avg_price
        old_side = local_position.side

        if not local_position.side:
            # 第一笔开仓单
            local_position.amount = local_order.filled_qty
            local_position.avg_price = local_order.filled_avg_price
            # 避免用 None 覆盖已有值
            if local_order.pos_side is not None:
                local_position.side = local_order.pos_side
            local_position.update_time = local_order.ack_time
            self.positions[index][local_order.symbol] = local_position
            
            # 打印开仓日志
            log_msg = f"[持仓更新] 开仓 - 交易所{index} {local_order.symbol}: 数量={local_order.filled_qty:.6f}, 成本价={local_order.filled_avg_price:.6f}, 方向={local_order.pos_side}"
            trader.log(f"index: {index}, 更新仓位:[{index}], 订单方向:{local_order.pos_side}, 仓位方向:{local_position.side}", level="INFO", web=False)
            if trader:
                trader.log(log_msg, level="INFO", color="blue", web=False)
            else:
                print(log_msg)
            
            return 0.0
            
        elif local_order.reduce_only:
            # 平仓单
            if trader:
                trader.log(
                    f"[持仓更新][平仓前] 交易所{index} {local_order.symbol}: old_amount={old_amount:.6f}, filled_qty={local_order.filled_qty:.6f}, side={old_side}",
                    level="INFO", color="blue", web=False
                )
            # 扣减数量
            new_amount = max(0.0, old_amount - local_order.filled_qty)
            local_position.amount = new_amount
            local_position.update_time = local_order.ack_time
            self.positions[index][local_order.symbol] = local_position
            
            # 计算平仓价差PnL
            if old_avg_price > 0:
                if old_side == "Long":
                    pnl = (local_order.filled_avg_price - old_avg_price) * local_order.filled_qty
                else:  # Short
                    pnl = (old_avg_price - local_order.filled_avg_price) * local_order.filled_qty
            else:
                pnl = 0
                
            # 打印平仓日志
            log_msg = f"[持仓更新] 平仓 - 交易所{index} {local_order.symbol}: 平仓数量={local_order.filled_qty:.6f}, 平仓价={local_order.filled_avg_price:.6f}, 原成本价={old_avg_price:.6f}, 平仓价差PnL={pnl:.6f}, 剩余数量={local_position.amount:.6f}"
            if trader:
                trader.log(log_msg, level="INFO", color="blue", web=False)
            else:
                trader.log(log_msg, level="INFO", web=False)
            
            if local_position.amount == 0:
                local_position.avg_price = 0
                local_position.side = None
                zero_msg = f"[持仓更新] 清仓 - 交易所{index} {local_order.symbol}: 持仓已清零"
                if trader:
                    trader.log(zero_msg, level="INFO", color="blue", web=False)
                else:
                    trader.log(zero_msg, level="INFO", web=False)
            if trader:
                trader.log(
                    f"[持仓更新][平仓后] 交易所{index} {local_order.symbol}: new_amount={local_position.amount:.6f}, side={local_position.side}",
                    level="INFO", color="blue", web=False
                )
            
            return pnl
                
        elif not local_order.reduce_only:
            # 补仓单
            if trader:
                trader.log(
                    f"[持仓更新][加仓前] 交易所{index} {local_order.symbol}: old_amount={old_amount:.6f}, old_avg={old_avg_price:.6f}, filled_qty={local_order.filled_qty:.6f}, filled_avg={local_order.filled_avg_price:.6f}, side={old_side}",
                    level="INFO", color="blue", web=False
                )
            # 计算加仓后的加权成本与数量
            new_amount = old_amount + local_order.filled_qty
            if new_amount > 0:
                new_avg_price = (
                    old_amount * old_avg_price + local_order.filled_qty * local_order.filled_avg_price
                ) / new_amount
            else:
                new_avg_price = 0.0
            local_position.avg_price = new_avg_price
            local_position.amount = new_amount
            # 避免用 None 覆盖已有值
            if local_order.pos_side is not None:
                local_position.side = local_order.pos_side
            local_position.update_time = local_order.ack_time
            self.positions[index][local_order.symbol] = local_position
            
            # 打印补仓日志
            log_msg = (
                f"[持仓更新] 补仓 - 交易所{index} {local_order.symbol}: 补仓数量={local_order.filled_qty:.6f}, 补仓价={local_order.filled_avg_price:.6f}, "
                f"原成本价={old_avg_price:.6f}, 新成本价={new_avg_price:.6f}, 总数量={local_position.amount:.6f}"
            )
            if trader:
                trader.log(log_msg, level="INFO", color="blue", web=False)
                trader.log(
                    f"[持仓更新][加仓后] 交易所{index} {local_order.symbol}: new_amount={local_position.amount:.6f}, new_avg={local_position.avg_price:.6f}, side={local_position.side}",
                    level="INFO", color="blue", web=False
                )
            else:
                print(log_msg)
            
            return 0.0

    def get_positions(self, index, symbol):
        return self.positions[index].get(symbol, Position())

    def get_hedge_positions(self, symbol: str) -> Tuple[Position, Position]:
        base_pos = self.positions[0][symbol]
        hedge_pos = self.positions[1][symbol]
        return [base_pos, hedge_pos]

