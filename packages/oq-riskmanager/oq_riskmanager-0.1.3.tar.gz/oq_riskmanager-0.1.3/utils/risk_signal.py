

import json
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

from enums.risk_signal_types import RiskScope, RiskAction


class RiskSignal:
    """
    风控信号容器。
    - 支持按层级记录风控事件：tick / order / global / symbol
    - 每个事件包含：action, message, timestamp, target_id, context
    - 空对象代表"无风控问题"
    """

    def __init__(self) -> None:
        self._signals: Dict[RiskScope, List[Dict[str, Any]]] = {
            RiskScope.TICK: [],
            RiskScope.ORDER: [],
            RiskScope.GLOBAL: [],
            RiskScope.SYMBOL: [],
        }

    def add(
        self,
        scope: RiskScope,
        action: RiskAction = RiskAction.NONE,
        message: str = "",
        target_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        新增风控事件，返回事件唯一 ID。
        """
        event_id = uuid.uuid4().hex
        event = {
            "id": event_id,
            "action": action,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "target_id": target_id,
            "context": context or {},
        }
        self._signals[scope].append(event)
        return event_id

    def remove_event(self, scope: RiskScope, event_id: str) -> bool:
        """
        根据事件 ID 删除指定层级的事件。返回是否删除成功。
        """
        events = self._signals.get(scope, [])
        original_len = len(events)
        self._signals[scope] = [e for e in events if e.get("id") != event_id]
        return len(self._signals[scope]) != original_len

    def resolve(
        self,
        scope: Optional[RiskScope] = None,
        target_id: Optional[str] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> int:
        """
        通过条件删除事件，返回删除数量。
        - scope 为 None 时表示所有层级
        - target_id 匹配事件 target_id
        - predicate 为自定义匹配函数，返回 True 表示删除
        """
        scopes = [scope] if scope is not None else list(self._signals.keys())
        removed = 0
        for sc in scopes:
            kept: List[Dict[str, Any]] = []
            for e in self._signals[sc]:
                match_target = (target_id is None or e.get("target_id") == target_id)
                match_pred = (predicate(e) if predicate is not None else True)
                if match_target and match_pred:
                    removed += 1
                else:
                    kept.append(e)
            self._signals[sc] = kept
        return removed

    def clear_scope(self, scope: RiskScope) -> None:
        """
        清空某个层级的所有事件。
        """
        self._signals[scope] = []

    def clear_all(self) -> None:
        """
        清空所有层级事件。
        """
        for sc in self._signals.keys():
            self._signals[sc] = []

    def is_empty(self) -> bool:
        return all(len(v) == 0 for v in self._signals.values())

    def __bool__(self) -> bool:
        return not self.is_empty()

    def latest_per_scope(self) -> Dict[RiskScope, Optional[Dict[str, Any]]]:
        out: Dict[RiskScope, Optional[Dict[str, Any]]] = {}
        for scope, events in self._signals.items():
            out[scope] = events[-1] if events else None
        return out

    def to_dict(self) -> Dict[str, Any]:
        def ser_event(e: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "id": e["id"],
                "action": e["action"].name,
                "message": e["message"],
                "timestamp": e["timestamp"],
                "target_id": e["target_id"],
                "context": e["context"],
            }

        return {
            "signals": {
                scope.name.lower(): [ser_event(e) for e in events]
                for scope, events in self._signals.items()
            },
        }

    @classmethod
    def ok(cls) -> "RiskSignal":
        return cls()


if __name__ == "__main__":
    # TODO: 这个地方的问题在于，生成了 eid，但是 risk_mananger.py 中不好管理。
    # 需要设计一个方法，用于管理 eid，并且能够将 eid 和对应的风控事件对应，当对应的风控事件发生并解除的时候，能够通过 eid 删除对应的事件。

    # 使用示例：创建 RiskSignal，添加/删除多个事件并输出摘要
    rs = RiskSignal()

    # 添加 TICK 层多个事件
    eid1 = rs.add(
        scope=RiskScope.TICK,
        action=RiskAction.STOP_OPEN,
        message="价差异常，暂停开仓",
        target_id="BTC_USDT",
        context={"spread": 0.005},
    )
    eid2 = rs.add(
        scope=RiskScope.TICK,
        action=RiskAction.STOP_ALL,
        message="延迟过高，停止所有交易",
        target_id="BTC_USDT",
        context={"delay": 1000},
    )

    # 添加 ORDER 层事件
    eid3 = rs.add(
        scope=RiskScope.ORDER,
        action=RiskAction.STOP_ALL,
        message="订单发送失败，停止所有交易",
        target_id="BTC_USDT",
        context={"err": "EXCHANGE_ERROR"},
    )

    # 添加 global 层 OK 事件
    eid4 = rs.add(
        scope=RiskScope.GLOBAL,
        action=RiskAction.STOP_ALL,
        message="账户杠杆过高，停止开仓",
        target_id="ALL",
        context={"leverage": 8},
    )

    print("是否为空信号:", rs.is_empty())

    # 按层级查看最新事件
    latest = rs.latest_per_scope()
    print("各层级最新事件:")
    for scope, event in latest.items():
        if event is None:
            print(f"  {scope.name.lower()}: None")
        else:
            print(
                f"  {scope.name.lower()}: "
                f"action={event['action'].name}, "
                f"message={event['message']}, target_id={event['target_id']}"
            )

    # 序列化输出
    print("序列化字典:")
    print(json.dumps(rs.to_dict(), ensure_ascii=False, indent=2))

    # 按 ID 删除一个 symbol 事件
    print("按 ID 删除一个 symbol 事件:", eid1)
    rs.remove_event(RiskScope.TICK, eid1)
    print(json.dumps(rs.to_dict(), ensure_ascii=False, indent=2))

    # 按条件删除剩余的 symbol 事件（例如同一 target_id）
    print("删除 target_id=BTC_USDT 的剩余 symbol 事件")
    removed = rs.resolve(scope=RiskScope.TICK, target_id="BTC_USDT")
    print("删除数量:", removed)
    print(json.dumps(rs.to_dict(), ensure_ascii=False, indent=2))

    # 清空 account 层
    print("清空 ORDER 层")
    rs.clear_scope(RiskScope.ORDER)
    print(json.dumps(rs.to_dict(), ensure_ascii=False, indent=2))

    # 清空所有层级
    print("清空所有层级")
    rs.clear_all()
    print(json.dumps(rs.to_dict(), ensure_ascii=False, indent=2))

