# ====================  这是一个 DataFeed 的代码，用于生成模拟数据，来模拟真实场景下 OpenQuant 给到 Strategy 的数据 ====================

import json
import os
from typing import Any, Dict, List, Iterable, Tuple


class DataFeed:
	"""
	DataFeed 负责从 example/fake_data 中加载假数据，并按事件类型输出，驱动 Strategy 的 on_ 方法。
	支持的数据文件（JSON Lines，每行一个 JSON 对象）：
	- bbo.jsonl: {"exchange": "BinanceSwap", "data": {...}}
	- depth.jsonl: {"exchange": "BinanceSwap", "data": {...}}
	- orders_slippage.jsonl: {"account_id": 0, "order": {...}}
	- orders_latency.jsonl: {"account_id": 0, "order": {...}}
	- receipts.jsonl: {"index": 0, "symbol": "BTC_USDT", "receipt": {...}}
	- balances.jsonl: {"account_id": 0, "balances": [{...}, ...]}
	- fundings.jsonl: {"exchange": "BinanceSwap", "funding": {...}}
	"""

	def __init__(self, base_path: str = None):
		self.base_path = base_path or os.path.join(os.path.dirname(__file__), "fake_data")
		self.bbo: List[Dict[str, Any]] = []
		self.depth: List[Dict[str, Any]] = []
		self.orders_slippage: List[Dict[str, Any]] = []
		self.orders_latency: List[Dict[str, Any]] = []
		self.receipts: List[Dict[str, Any]] = []
		self.balances: List[Dict[str, Any]] = []
		self.fundings: List[Dict[str, Any]] = []

	def _load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
		path = os.path.join(self.base_path, filename)
		if not os.path.exists(path):
			return []
		out: List[Dict[str, Any]] = []
		with open(path, "r", encoding="utf-8") as f:
			for line in f:
				line = line.strip()
				if not line:
					continue
				try:
					out.append(json.loads(line))
				except Exception:
					continue
		return out

	def load(self) -> None:
		self.bbo = self._load_jsonl("bbo.jsonl")
		self.depth = self._load_jsonl("depth.jsonl")
		self.orders_slippage = self._load_jsonl("orders_slippage.jsonl")
		self.orders_latency = self._load_jsonl("orders_latency.jsonl")
		self.receipts = self._load_jsonl("receipts.jsonl")
		self.balances = self._load_jsonl("balances.jsonl")
		self.fundings = self._load_jsonl("fundings.jsonl")

	def stream(self) -> Iterable[Tuple[str, tuple, dict]]:
		"""
		按顺序输出事件。每个事件为 (method_name, args_tuple, meta_dict)
		- on_bbo: (exchange, data)
		- on_depth: (exchange, data)
		- on_order: (account_id, order)
		- on_balance: (account_id, balances)
		- on_funding: (exchange, funding)
		- receipt（非 on_）：("order_receipt", (index, symbol, receipt), {})
		"""
		for item in self.bbo:
			yield ("on_bbo", (item.get("exchange"), item.get("data")), {})
		for item in self.depth:
			yield ("on_depth", (item.get("exchange"), item.get("data")), {})
		for item in self.orders_slippage:
			yield ("on_order", (item.get("account_id"), item.get("order")), {"kind": "slippage"})
		for item in self.orders_latency:
			yield ("on_order", (item.get("account_id"), item.get("order")), {"kind": "latency"})
		for item in self.balances:
			yield ("on_balance", (item.get("account_id"), item.get("balances")), {})
		for item in self.fundings:
			yield ("on_funding", (item.get("exchange"), item.get("funding")), {})
		for item in self.receipts:
			yield ("order_receipt", (item.get("index"), item.get("symbol"), item.get("receipt")), {})