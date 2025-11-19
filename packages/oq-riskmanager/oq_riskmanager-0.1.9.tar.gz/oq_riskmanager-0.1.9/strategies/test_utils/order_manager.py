class Order:
    __slots__ = (
        "account_id",
        "symbol",
        "side",
        "pos_side",
        "price",
        "amount",
        "status",
        "is_market",
        "filled_avg_price",
        "filled_qty",
        "reduce_only",
        "fee",
        "send_time",
        "ack_time",
        "open_price",
        "is_single_leg",
        "is_twap",
    )

    def __init__(
        self,
        account_id,
        symbol,
        side,
        pos_side,
        price,
        amount,
        send_time=0,
        reduce_only=False,
        is_market=False,
        status="New",
        filled_avg_price=0.0,
        filled_qty=0.0,
        fee=0.0,
        ack_time=0,
        open_price=0.0,
        is_single_leg=False,
        is_twap=False,
    ):
        self.account_id = account_id
        self.symbol = symbol
        self.side = side
        self.pos_side = pos_side
        self.price = price
        self.amount = amount
        self.status: str = status
        self.is_market = is_market
        self.filled_avg_price = filled_avg_price
        self.filled_qty = filled_qty
        self.reduce_only = reduce_only
        self.fee: float = fee
        self.send_time = send_time
        self.ack_time: int = ack_time
        self.open_price = open_price
        self.is_single_leg = is_single_leg
        self.is_twap = is_twap

    def update(self, order, entry_price):
        self.open_price = entry_price
        self.status = order["status"]
        self.filled_avg_price = order["filled_avg_price"]
        self.filled_qty = order["filled"]
        self.ack_time = order["timestamp"]
        self.pos_side = order["pos_side"]
        self.side = order["side"]

    def to_dict(self):
        """返回包含所有属性的字典"""
        return {
            "account_id": self.account_id,
            "symbol": self.symbol,
            "side": self.side,
            "pos_side": self.pos_side,
            "price": self.price,
            "amount": self.amount,
            "status": self.status,
            "is_market": self.is_market,
            "filled_avg_price": self.filled_avg_price,
            "filled_qty": self.filled_qty,
            "reduce_only": self.reduce_only,
            "fee": self.fee,
            "send_time": self.send_time,
            "ack_time": self.ack_time,
            "open_price": self.open_price,
            "is_single_leg": self.is_single_leg,
            "is_twap": self.is_twap,
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典恢复 Order 实例"""
        order = cls(
            account_id=data["account_id"],
            symbol=data["symbol"],
            side=data["side"],
            pos_side=data["pos_side"],
            price=data["price"],
            amount=data["amount"],
            send_time=data["send_time"],
            reduce_only=data["reduce_only"],
            is_market=data["is_market"]
        )
        order.status = data["status"]
        order.filled_avg_price = data["filled_avg_price"]
        order.filled_qty = data["filled_qty"]
        order.fee = data["fee"]
        order.ack_time = data["ack_time"]
        order.open_price = data["open_price"]
        order.is_single_leg = data.get("is_single_leg", False)
        order.is_twap = data.get("is_twap", False)
        return order


class OrderManager:
    def __init__(self):
        # current_order 存储挂单的 symbol 和 order_id
        # local_orders 存储挂单的 order_id 和 local_order
        self.local_orders: dict[str, Order] = {}
        self.current_order: dict[str, str] = {}

    def update_current_order(self, symbol: str, order_id: str):
        self.current_order[symbol] = order_id

    def remove_current_order(self, symbol: str):
        if symbol in self.current_order:
            del self.current_order[symbol]

    def get_current_order_id(self, symbol: str) -> str:
        return self.current_order.get(symbol, None)

    def add_order(self, order_id: str, order: Order):
        self.local_orders[order_id] = order

    def update_order(self, order_id: str, update_data: dict, entry_price: float):
        order = self.local_orders.get(order_id)
        if order:
            order.update(update_data, entry_price)

    def remove_order(self, order_id: str):
        self.local_orders.pop(order_id, None)

    def get_order(self, order_id: str) -> Order:
        return self.local_orders.get(order_id)

    def clear_finished_orders(self):
        to_delete = [oid for oid, o in self.local_orders.items() if o.status in ("FILLED", "CANCELED")]
        for oid in to_delete:
            del self.local_orders[oid]

    def to_dict(self):
        """将 OrderManager 状态转换为 JSON 兼容的字典"""
        return {
            "local_orders": {order_id: order.to_dict() for order_id, order in self.local_orders.items()}
        }

    @classmethod
    def from_dict(cls, data):
        """从字典恢复 OrderManager 实例"""
        manager = cls()
        if "local_orders" in data:
            for order_id, order_data in data["local_orders"].items():
                order = Order.from_dict(order_data)
                manager.add_order(order_id, order)
        return manager
