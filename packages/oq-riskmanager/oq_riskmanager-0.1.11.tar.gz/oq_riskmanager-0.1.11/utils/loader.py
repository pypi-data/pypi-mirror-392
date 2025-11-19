import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import tomllib  # Python 3.11+
    _USE_STDLIB_TOML = True
except ImportError:
    try:
        import toml as tomllib  # 使用 toml 库作为后备
        _USE_STDLIB_TOML = False
    except ImportError:
        raise ImportError("需要安装 toml 库: pip install toml")

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ConfigLoader:
    """
    配置加载器，用于读取和管理 config.toml 配置文件。
    支持文件更新检测和自动重新加载。
    """
    
    _instance: Optional['ConfigLoader'] = None
    _config: Dict[str, Any] = {}
    _config_path: Optional[str] = None
    _last_modified: float = 0.0
    
    def __new__(cls, config_path: Optional[str] = None):
        """
        单例模式，确保全局只有一个配置加载器实例。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器。
        
        Args:
            config_path: 配置文件路径，如果为 None，则使用默认路径 config/config.toml
        """
        if self._initialized:
            return
        
        if config_path is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent
            config_path = str(project_root / "config" / "config.toml")
        
        self._config_path = config_path
        self._load_config()
        self._initialized = True
    
    def _load_config(self) -> None:
        """
        从配置文件加载配置，并更新最后修改时间。
        """
        if not os.path.exists(self._config_path):
            raise FileNotFoundError(f"配置文件不存在: {self._config_path}")
        
        try:
            # 根据使用的库选择不同的读取方式
            if _USE_STDLIB_TOML:
                # Python 3.11+ 的 tomllib（标准库）
                with open(self._config_path, 'rb') as f:
                    self._config = tomllib.load(f)
            else:
                # toml 库（第三方库）
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = tomllib.loads(f.read())
            
            # 更新最后修改时间
            self._last_modified = os.path.getmtime(self._config_path)
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}")
    
    def _check_and_reload(self) -> None:
        """
        检查配置文件是否有更新，如果有则重新加载。
        """
        if not os.path.exists(self._config_path):
            return
        
        current_modified = os.path.getmtime(self._config_path)
        if current_modified > self._last_modified:
            self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，如果不存在则返回默认值。
        每次获取时都会检查文件是否有更新。
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        self._check_and_reload()
        return self._config.get(key, default)
    
    def get_tick_config(self) -> Dict[str, Any]:
        """
        获取 TICK 级别的配置。
        
        Returns:
            TICK 级别配置字典
        """
        self._check_and_reload()
        return {
            'abnormal_spread_threshold': self._config.get('abnormal_spread_threshold', 0.2),
            'abnormal_bbo_latency_threshold': self._config.get('abnormal_bbo_latency_threshold', 5000),
        }
    
    def get_order_config(self) -> Dict[str, Any]:
        """
        获取 ORDER 级别的配置。
        
        Returns:
            ORDER 级别配置字典
        """
        self._check_and_reload()
        return {
            'abnormal_order_slippage_threshold': self._config.get('abnormal_order_slippage_threshold', 30.0),
            'abnormal_order_latency_threshold': self._config.get('abnormal_order_latency_threshold', 600),
        }
    
    def get_global_config(self) -> Dict[str, Any]:
        """
        获取 GLOBAL 级别的配置。
        
        Returns:
            GLOBAL 级别配置字典
        """
        self._check_and_reload()
        return {
            'max_account_leverage': self._config.get('max_account_leverage', 8.0),
            'max_symbol_leverage': self._config.get('max_symbol_leverage', 1.0),
            'abnormal_position_exposure_threshold': self._config.get('abnormal_position_exposure_threshold', 0.05),
            'available_balance_warning_threshold': self._config.get('available_balance_warning_threshold', 0.2),
            'available_balance_unbalance_threshold': self._config.get('available_balance_unbalance_threshold', 1.2),
            'total_drawdown_threshold': self._config.get('total_drawdown_threshold', 0.95),
            'intraday_loss_threshold': self._config.get('intraday_loss_threshold', 1000.0),
            'liquidation_price_warning_threshold': self._config.get('liquidation_price_warning_threshold', 0.01),
        }
    
    def reload(self) -> None:
        """
        强制重新加载配置文件。
        """
        self._load_config()


# 全局配置加载器实例
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """
    获取全局配置加载器实例。
    
    Args:
        config_path: 配置文件路径，仅在首次调用时生效
        
    Returns:
        配置加载器实例
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader

