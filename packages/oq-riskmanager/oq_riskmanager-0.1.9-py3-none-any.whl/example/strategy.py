from utils.trader import Trader
from utils.statistics import Statistics
from utils.position_manager import HedgePositionManager
from utils.signal_manager import SignalManager
from risk_manager import risk_managed                      # 导入库


##############################################################################
# 以下是 Mock Strategy 的类，用于模拟真实交易场景中的策略使用。
##############################################################################
@risk_managed()               # 使用装饰器
class Strategy:
    
    def __init__(self, cex_configs={}, dex_configs={}, config=None, trader=Trader()):
        self.has_account = True
        self.base_index = 2
        self.config = config
        self.trader = trader

        self.local_symbol_order = {}
        self.force_stop = False  # 强制停止标志，用于最大回撤时的强制停止
        self.total_account_stat = Statistics()

        self.instruments = [{} for _ in range(self.base_index)]
        self.ex_map = {'BinanceSwap': 0, 'OkxSwap': 1, 0: 'BinanceSwap', 1: 'OkxSwap'}
        self.bbo = [{} for _ in range(self.base_index)]
        self.balances = [{} for _ in range(self.base_index)]


    def prepare_symbols(self):
        self.symbols = [["BTC_USDT"], ["BTC_USDT"]]

        self.fundings = [
            {symbol: {"funding_rate": 0, "funding_interval": 8,
                        "next_funding_at": 0} for symbol in self.symbols[idx]}
            for idx in range(self.base_index)
        ]

        self.pm = HedgePositionManager()
        self.signal_manager = SignalManager()

    def start(self):
        print(f"这是策略启动的逻辑")

    def subscribes(self):
        print(f"这是订阅逻辑")
    
    def on_bbo(self, exchange, bbo):
        risk_signal = self.risk_manager.check_tick_risk()                 # 检查 tick 级别风控
        if risk_signal and not risk_signal.is_empty():
            print(f"bbo 风控告警: {risk_signal.to_dict()}")
            print(f"---------------------------------------------------------")

    def on_depth(self, exchange, depth):
        risk_signal = self.risk_manager.check_tick_risk()                 # 检查 tick 级别风控
        if risk_signal and not risk_signal.is_empty():
            print(f"depth 风控告警: {risk_signal.to_dict()}")
            print(f"---------------------------------------------------------")

    def on_funding(self, exchange, fundings):
        return

    def on_funding_fee(self):
        return

    def on_order(self, account_id, order):
        err_receipt = {'Err': {'code': 2000, 'error': 'mock'}}
        for _ in range(5):
            rs = self.risk_manager.check_order_receipt_risk(0, 'BTC_USDT', err_receipt)                 # 检查订单回执风控
        if rs and not rs.is_empty():
            print(f"order 回执风控告警: {rs.to_dict()}")
            print(f"---------------------------------------------------------")
        rs_quality = self.risk_manager.check_order_risk()                 # 检查订单质量风控
        if rs_quality and not rs_quality.is_empty():
            print(f"order 质量风控告警: {rs_quality.to_dict()}")
            print(f"---------------------------------------------------------")
            
    def on_strategy(self, index, symbol):
        return

    def on_balance(self, account_id, balance):
        risk_signal = self.risk_manager.check_global_risk()                 # 检查全局风控
        if risk_signal and not risk_signal.is_empty():
            print(f"balance 风控告警: {risk_signal.to_dict()}")
            print(f"---------------------------------------------------------")
        return

    def on_stop(self):
        return

    def on_trade(self, exchange, trade):
        return

    def on_timer_subscribe(self, timer_name):
        risk_signal = self.risk_manager.check_global_risk()                 # 检查全局风控
        if risk_signal and not risk_signal.is_empty():
            print(f"global 风控告警: {risk_signal.to_dict()}")
            print(f"---------------------------------------------------------")


if __name__ == "__main__":
    mock_strategy = Strategy()
    strategy_methods = sorted([method for method in dir(Strategy) if not method.startswith('_')])  # 按照字母顺序排序
    print(f"Strategy 类的方法: {strategy_methods}")
    print(f"--------------------------------")
    for method in strategy_methods:
        print(f"执行 {method} 方法")
        getattr(mock_strategy, method)()
        print(f"--------------------------------")
        
        
    