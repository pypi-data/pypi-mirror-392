import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any

from example.datafeed import DataFeed
from example.strategy import Strategy
from risk_manager import risk_managed


def run() -> None:
    # 初始化策略
    strategy = Strategy()
    strategy.prepare_symbols()
    # 配置 ex_map 映射：名称<->index
    strategy.ex_map = {
        "BinanceSwap": 0,
        "OkxSwap": 1,
        0: "BinanceSwap",
        1: "OkxSwap",
    }

    # 初始化数据源
    df = DataFeed()
    df.load()

    # 控制 RiskManager 窗口时间：使用可控时钟（基础时间 1_000_000_000_000）
    current_ms = 1_000_000_000_000
    strategy.risk_manager._now_ms = lambda: current_ms

    # 依次喂数据并触发 on_ 方法或风控调用
    for event, args, meta in df.stream():
        # 推进时间（每条事件+1s）
        current_ms += 1000

        if event == "order_receipt":
            index, symbol, receipt = args
            rs = strategy.risk_manager.check_order_receipt_risk(index, symbol, receipt)
            if rs and not rs.is_empty():
                print("订单回执 RiskSignal:", rs.to_dict())
                print(f"---------------------------------------------------------")
            continue

        # 常规 on_ 调用由装饰器接管风控数据同步
        getattr(strategy, event)(*args)

        # 针对订单，额外调用一次订单质量风控
        if event == "on_order":
            rs = strategy.risk_manager.check_order_risk()
            if rs and not rs.is_empty():
                print("订单质量 RiskSignal:", rs.to_dict())
                print(f"---------------------------------------------------------")

    print("Done.")


if __name__ == "__main__":
    run()


