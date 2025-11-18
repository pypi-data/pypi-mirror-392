"""
日志系统API接口
提供简洁易用的对外接口
"""

import time
from contextlib import contextmanager
from ..core.manager import LogManager
from ..core.loader import ConfigLoader

# 日志分类定义
_LOG_CATEGORIES = [
    'NET', 'MODEL', 'TRAIN', 'GRAD', 'OPT', 'EVAL', 'DATA', 'IO',
    'CACHE', 'SYS', 'SECURITY', 'TEST', 'WEB', 'API', 'DB', 'COM'
]

# 日志级别方法定义
_LOG_METHODS = ['info', 'debug', 'warning', 'error', 'success', 'find', 'trace']

# 全局日志器实例存储
_loggers = {category: None for category in _LOG_CATEGORIES}
_initialized = False


def setup(run_name=None, config_path=None, project_root=None):
    """
    初始化日志系统

    Args:
        run_name: 运行名称，用于日志文件名
        config_path: 自定义配置文件路径
        project_root: 项目根目录，用于日志输出
    """
    global _loggers, _initialized
    
    # 如果指定了项目根目录，设置环境变量
    if project_root:
        import os
        os.environ['LILI_LOGGER_PROJECT_ROOT'] = str(project_root)
    
    log_file = LogManager.initialize(run_name, config_path)
    
    # 初始化所有日志器实例
    for category in _LOG_CATEGORIES:
        _loggers[category] = LogManager.get_logger(category)
    
    _initialized = True
    
    return log_file

def _create_log_method(category, level):
    """创建日志方法的工厂函数"""
    
    def log_method(self, message):
        self._ensure_initialized()
        getattr(_loggers[category], level)(message)
    
    return log_method


class Log:
    """
    统一日志接口类
    """
    
    def __init__(self):
        """初始化日志接口"""
        pass
    
    def _ensure_initialized(self):
        """确保日志系统已初始化"""
        global _initialized
        if not _initialized and not LogManager.is_initialized():
            setup()
    
    # ===== COM Logger (通用) =====
    def com_info(self, message):
        """通用信息日志"""
        self._ensure_initialized()
        _loggers['COM'].info(message)
    
    def com_debug(self, message):
        """通用调试日志"""
        self._ensure_initialized()
        _loggers['COM'].debug(message)
    
    def com_warning(self, message):
        """通用警告日志"""
        self._ensure_initialized()
        _loggers['COM'].warning(message)
    
    def com_error(self, message):
        """通用错误日志"""
        self._ensure_initialized()
        _loggers['COM'].error(message)
    
    def com_success(self, message):
        """通用成功日志"""
        self._ensure_initialized()
        _loggers['COM'].success(message)
    
    def com_find(self, message):
        """通用查找日志"""
        self._ensure_initialized()
        _loggers['COM'].find(message)
    
    def com_trace(self, message):
        """通用跟踪日志"""
        self._ensure_initialized()
        _loggers['COM'].trace(message)
    
    # ===== NET Logger (神经网络) =====
    def net_info(self, message):
        """神经网络信息日志"""
        self._ensure_initialized()
        _loggers['NET'].info(message)
    
    def net_debug(self, message):
        """神经网络调试日志"""
        self._ensure_initialized()
        _loggers['NET'].debug(message)
    
    def net_warning(self, message):
        """神经网络警告日志"""
        self._ensure_initialized()
        _loggers['NET'].warning(message)
    
    def net_error(self, message):
        """神经网络错误日志"""
        self._ensure_initialized()
        _loggers['NET'].error(message)
    
    def net_success(self, message):
        """神经网络成功日志"""
        self._ensure_initialized()
        _loggers['NET'].success(message)
    
    def net_find(self, message):
        """神经网络查找日志"""
        self._ensure_initialized()
        _loggers['NET'].find(message)
    
    def net_trace(self, message):
        """神经网络跟踪日志"""
        self._ensure_initialized()
        _loggers['NET'].trace(message)
    
    # ===== MODEL Logger (模型) =====
    def model_info(self, message):
        """模型信息日志"""
        self._ensure_initialized()
        _loggers['MODEL'].info(message)
    
    def model_debug(self, message):
        """模型调试日志"""
        self._ensure_initialized()
        _loggers['MODEL'].debug(message)
    
    def model_warning(self, message):
        """模型警告日志"""
        self._ensure_initialized()
        _loggers['MODEL'].warning(message)
    
    def model_error(self, message):
        """模型错误日志"""
        self._ensure_initialized()
        _loggers['MODEL'].error(message)
    
    def model_success(self, message):
        """模型成功日志"""
        self._ensure_initialized()
        _loggers['MODEL'].success(message)
    
    def model_find(self, message):
        """模型查找日志"""
        self._ensure_initialized()
        _loggers['MODEL'].find(message)
    
    def model_trace(self, message):
        """模型跟踪日志"""
        self._ensure_initialized()
        _loggers['MODEL'].trace(message)
    
    # ===== TRAIN Logger (训练) =====
    def train_info(self, message):
        """训练信息日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].info(message)
    
    def train_debug(self, message):
        """训练调试日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].debug(message)
    
    def train_warning(self, message):
        """训练警告日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].warning(message)
    
    def train_error(self, message):
        """训练错误日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].error(message)
    
    def train_success(self, message):
        """训练成功日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].success(message)
    
    def train_find(self, message):
        """训练查找日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].find(message)
    
    def train_trace(self, message):
        """训练跟踪日志"""
        self._ensure_initialized()
        _loggers['TRAIN'].trace(message)
    
    # ===== GRAD Logger (梯度) =====
    def grad_info(self, message):
        """梯度信息日志"""
        self._ensure_initialized()
        _loggers['GRAD'].info(message)
    
    def grad_debug(self, message):
        """梯度调试日志"""
        self._ensure_initialized()
        _loggers['GRAD'].debug(message)
    
    def grad_warning(self, message):
        """梯度警告日志"""
        self._ensure_initialized()
        _loggers['GRAD'].warning(message)
    
    def grad_error(self, message):
        """梯度错误日志"""
        self._ensure_initialized()
        _loggers['GRAD'].error(message)
    
    def grad_success(self, message):
        """梯度成功日志"""
        self._ensure_initialized()
        _loggers['GRAD'].success(message)
    
    def grad_find(self, message):
        """梯度查找日志"""
        self._ensure_initialized()
        _loggers['GRAD'].find(message)
    
    def grad_trace(self, message):
        """梯度跟踪日志"""
        self._ensure_initialized()
        _loggers['GRAD'].trace(message)
    
    # ===== OPT Logger (优化器) =====
    def opt_info(self, message):
        """优化器信息日志"""
        self._ensure_initialized()
        _loggers['OPT'].info(message)
    
    def opt_debug(self, message):
        """优化器调试日志"""
        self._ensure_initialized()
        _loggers['OPT'].debug(message)
    
    def opt_warning(self, message):
        """优化器警告日志"""
        self._ensure_initialized()
        _loggers['OPT'].warning(message)
    
    def opt_error(self, message):
        """优化器错误日志"""
        self._ensure_initialized()
        _loggers['OPT'].error(message)
    
    def opt_success(self, message):
        """优化器成功日志"""
        self._ensure_initialized()
        _loggers['OPT'].success(message)
    
    def opt_find(self, message):
        """优化器查找日志"""
        self._ensure_initialized()
        _loggers['OPT'].find(message)
    
    def opt_trace(self, message):
        """优化器跟踪日志"""
        self._ensure_initialized()
        _loggers['OPT'].trace(message)
    
    # ===== EVAL Logger (评估) =====
    def eval_info(self, message):
        """评估信息日志"""
        self._ensure_initialized()
        _loggers['EVAL'].info(message)
    
    def eval_debug(self, message):
        """评估调试日志"""
        self._ensure_initialized()
        _loggers['EVAL'].debug(message)
    
    def eval_warning(self, message):
        """评估警告日志"""
        self._ensure_initialized()
        _loggers['EVAL'].warning(message)
    
    def eval_error(self, message):
        """评估错误日志"""
        self._ensure_initialized()
        _loggers['EVAL'].error(message)
    
    def eval_success(self, message):
        """评估成功日志"""
        self._ensure_initialized()
        _loggers['EVAL'].success(message)
    
    def eval_find(self, message):
        """评估查找日志"""
        self._ensure_initialized()
        _loggers['EVAL'].find(message)
    
    def eval_trace(self, message):
        """评估跟踪日志"""
        self._ensure_initialized()
        _loggers['EVAL'].trace(message)
    
    # ===== DATA Logger (数据) =====
    def data_info(self, message):
        """数据信息日志"""
        self._ensure_initialized()
        _loggers['DATA'].info(message)
    
    def data_debug(self, message):
        """数据调试日志"""
        self._ensure_initialized()
        _loggers['DATA'].debug(message)
    
    def data_warning(self, message):
        """数据警告日志"""
        self._ensure_initialized()
        _loggers['DATA'].warning(message)
    
    def data_error(self, message):
        """数据错误日志"""
        self._ensure_initialized()
        _loggers['DATA'].error(message)
    
    def data_success(self, message):
        """数据成功日志"""
        self._ensure_initialized()
        _loggers['DATA'].success(message)
    
    def data_find(self, message):
        """数据查找日志"""
        self._ensure_initialized()
        _loggers['DATA'].find(message)
    
    def data_trace(self, message):
        """数据跟踪日志"""
        self._ensure_initialized()
        _loggers['DATA'].trace(message)
    
    # ===== IO Logger (输入输出) =====
    def io_info(self, message):
        """IO信息日志"""
        self._ensure_initialized()
        _loggers['IO'].info(message)
    
    def io_debug(self, message):
        """IO调试日志"""
        self._ensure_initialized()
        _loggers['IO'].debug(message)
    
    def io_warning(self, message):
        """IO警告日志"""
        self._ensure_initialized()
        _loggers['IO'].warning(message)
    
    def io_error(self, message):
        """IO错误日志"""
        self._ensure_initialized()
        _loggers['IO'].error(message)
    
    def io_success(self, message):
        """IO成功日志"""
        self._ensure_initialized()
        _loggers['IO'].success(message)
    
    def io_find(self, message):
        """IO查找日志"""
        self._ensure_initialized()
        _loggers['IO'].find(message)
    
    def io_trace(self, message):
        """IO跟踪日志"""
        self._ensure_initialized()
        _loggers['IO'].trace(message)
    
    # ===== CACHE Logger (缓存) =====
    def cache_info(self, message):
        """缓存信息日志"""
        self._ensure_initialized()
        _loggers['CACHE'].info(message)
    
    def cache_debug(self, message):
        """缓存调试日志"""
        self._ensure_initialized()
        _loggers['CACHE'].debug(message)
    
    def cache_warning(self, message):
        """缓存警告日志"""
        self._ensure_initialized()
        _loggers['CACHE'].warning(message)
    
    def cache_error(self, message):
        """缓存错误日志"""
        self._ensure_initialized()
        _loggers['CACHE'].error(message)
    
    def cache_success(self, message):
        """缓存成功日志"""
        self._ensure_initialized()
        _loggers['CACHE'].success(message)
    
    def cache_find(self, message):
        """缓存查找日志"""
        self._ensure_initialized()
        _loggers['CACHE'].find(message)
    
    def cache_trace(self, message):
        """缓存跟踪日志"""
        self._ensure_initialized()
        _loggers['CACHE'].trace(message)
    
    # ===== SYS Logger (系统) =====
    def sys_info(self, message):
        """系统信息日志"""
        self._ensure_initialized()
        _loggers['SYS'].info(message)
    
    def sys_debug(self, message):
        """系统调试日志"""
        self._ensure_initialized()
        _loggers['SYS'].debug(message)
    
    def sys_warning(self, message):
        """系统警告日志"""
        self._ensure_initialized()
        _loggers['SYS'].warning(message)
    
    def sys_error(self, message):
        """系统错误日志"""
        self._ensure_initialized()
        _loggers['SYS'].error(message)
    
    def sys_success(self, message):
        """系统成功日志"""
        self._ensure_initialized()
        _loggers['SYS'].success(message)
    
    def sys_find(self, message):
        """系统查找日志"""
        self._ensure_initialized()
        _loggers['SYS'].find(message)
    
    def sys_trace(self, message):
        """系统跟踪日志"""
        self._ensure_initialized()
        _loggers['SYS'].trace(message)
    
    # ===== SECURITY Logger (安全) =====
    def security_info(self, message):
        """安全信息日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].info(message)
    
    def security_debug(self, message):
        """安全调试日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].debug(message)
    
    def security_warning(self, message):
        """安全警告日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].warning(message)
    
    def security_error(self, message):
        """安全错误日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].error(message)
    
    def security_success(self, message):
        """安全成功日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].success(message)
    
    def security_find(self, message):
        """安全查找日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].find(message)
    
    def security_trace(self, message):
        """安全跟踪日志"""
        self._ensure_initialized()
        _loggers['SECURITY'].trace(message)
    
    # ===== TEST Logger (测试) =====
    def test_info(self, message):
        """测试信息日志"""
        self._ensure_initialized()
        _loggers['TEST'].info(message)
    
    def test_debug(self, message):
        """测试调试日志"""
        self._ensure_initialized()
        _loggers['TEST'].debug(message)
    
    def test_warning(self, message):
        """测试警告日志"""
        self._ensure_initialized()
        _loggers['TEST'].warning(message)
    
    def test_error(self, message):
        """测试错误日志"""
        self._ensure_initialized()
        _loggers['TEST'].error(message)
    
    def test_success(self, message):
        """测试成功日志"""
        self._ensure_initialized()
        _loggers['TEST'].success(message)
    
    def test_find(self, message):
        """测试查找日志"""
        self._ensure_initialized()
        _loggers['TEST'].find(message)
    
    def test_trace(self, message):
        """测试跟踪日志"""
        self._ensure_initialized()
        _loggers['TEST'].trace(message)
    
    # ===== WEB Logger (网络服务) =====
    def web_info(self, message):
        """Web信息日志"""
        self._ensure_initialized()
        _loggers['WEB'].info(message)
    
    def web_debug(self, message):
        """Web调试日志"""
        self._ensure_initialized()
        _loggers['WEB'].debug(message)
    
    def web_warning(self, message):
        """Web警告日志"""
        self._ensure_initialized()
        _loggers['WEB'].warning(message)
    
    def web_error(self, message):
        """Web错误日志"""
        self._ensure_initialized()
        _loggers['WEB'].error(message)
    
    def web_success(self, message):
        """Web成功日志"""
        self._ensure_initialized()
        _loggers['WEB'].success(message)
    
    def web_find(self, message):
        """Web查找日志"""
        self._ensure_initialized()
        _loggers['WEB'].find(message)
    
    def web_trace(self, message):
        """Web跟踪日志"""
        self._ensure_initialized()
        _loggers['WEB'].trace(message)
    
    # ===== API Logger (API) =====
    def api_info(self, message):
        """API信息日志"""
        self._ensure_initialized()
        _loggers['API'].info(message)
    
    def api_debug(self, message):
        """API调试日志"""
        self._ensure_initialized()
        _loggers['API'].debug(message)
    
    def api_warning(self, message):
        """API警告日志"""
        self._ensure_initialized()
        _loggers['API'].warning(message)
    
    def api_error(self, message):
        """API错误日志"""
        self._ensure_initialized()
        _loggers['API'].error(message)
    
    def api_success(self, message):
        """API成功日志"""
        self._ensure_initialized()
        _loggers['API'].success(message)
    
    def api_find(self, message):
        """API查找日志"""
        self._ensure_initialized()
        _loggers['API'].find(message)
    
    def api_trace(self, message):
        """API跟踪日志"""
        self._ensure_initialized()
        _loggers['API'].trace(message)
    
    # ===== DB Logger (数据库) =====
    def db_info(self, message):
        """数据库信息日志"""
        self._ensure_initialized()
        _loggers['DB'].info(message)
    
    def db_debug(self, message):
        """数据库调试日志"""
        self._ensure_initialized()
        _loggers['DB'].debug(message)
    
    def db_warning(self, message):
        """数据库警告日志"""
        self._ensure_initialized()
        _loggers['DB'].warning(message)
    
    def db_error(self, message):
        """数据库错误日志"""
        self._ensure_initialized()
        _loggers['DB'].error(message)
    
    def db_success(self, message):
        """数据库成功日志"""
        self._ensure_initialized()
        _loggers['DB'].success(message)
    
    def db_find(self, message):
        """数据库查找日志"""
        self._ensure_initialized()
        _loggers['DB'].find(message)
    
    def db_trace(self, message):
        """数据库跟踪日志"""
        self._ensure_initialized()
        _loggers['DB'].trace(message)
    
    # ===== 快捷方法 =====
    def info(self, message):
        """通用信息日志 (COM分类快捷方式)"""
        self.com_info(message)
    
    def debug(self, message):
        """通用调试日志 (COM分类快捷方式)"""
        self.com_debug(message)
    
    def warning(self, message):
        """通用警告日志 (COM分类快捷方式)"""
        self.com_warning(message)
    
    def error(self, message):
        """通用错误日志 (COM分类快捷方式)"""
        self.com_error(message)
    
    def success(self, message):
        """通用成功日志 (COM分类快捷方式)"""
        self.com_success(message)
    
    def find(self, message):
        """通用查找日志 (COM分类快捷方式)"""
        self.com_find(message)
    
    def trace(self, message):
        """通用跟踪日志 (COM分类快捷方式)"""
        self.com_trace(message)
    
    # ===== 工具方法 =====
    @contextmanager
    def timer(self, operation_name, logger_name='COM'):
        """
        计时器上下文管理器
        """
        self._ensure_initialized()
        with LogManager.timer(operation_name, logger_name):
            yield
    
    def memory(self, logger_name='COM'):
        """记录内存使用情况"""
        self._ensure_initialized()
        LogManager.log_memory_usage(logger_name)
    
    def status(self):
        """显示系统状态"""
        self._ensure_initialized()
        status_info = LogManager.get_status()
        _loggers['COM'].info("📊 系统状态检查")
        _loggers['COM'].info(f"📁 日志文件: {status_info['log_file']}")
        _loggers['COM'].info(f"⚙️  配置文件: {status_info['config_file']}")
        _loggers['COM'].info(f"🔧 日志分类: {status_info['loggers_count']} 个")
        return status_info
    
    def set_level(self, logger_name, level):
        """
        设置日志级别
        """
        self._ensure_initialized()
        LogManager.set_level(logger_name, level)
    
    def reload_config(self):
        """重新加载配置"""
        self._ensure_initialized()
        ConfigLoader.reload_config()
        _loggers['COM'].success("配置重新加载完成")
    
    def get_logger(self, category):
        """
        获取指定分类的日志器
        """
        self._ensure_initialized()
        if category not in _LOG_CATEGORIES:
            raise ValueError(f"未知的日志分类: {category}")
        return _loggers[category]


# 创建全局实例
log = Log()

__all__ = ['setup', 'Log', 'log']