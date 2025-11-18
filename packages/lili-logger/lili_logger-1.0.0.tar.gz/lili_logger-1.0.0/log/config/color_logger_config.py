# logs/config/color_logger_config.py
import logging
import logging.config
from pathlib import Path
from datetime import datetime
import time
from contextlib import contextmanager

# 全局logger实例 - 完整分类
net_logger = None
train_logger = None
grad_logger = None
data_logger = None
model_logger = None
opt_logger = None
eval_logger = None
io_logger = None
sys_logger = None
web_logger = None
db_logger = None
api_logger = None
test_logger = None
security_logger = None
cache_logger = None
com_logger = None
_initialized = False


class EnhancedColorFormatter(logging.Formatter):
    """增强版彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',  # 青色
        'INFO': '\033[92m',  # 亮绿色
        'SUCCESS': '\033[32m',  # 绿色
        'WARNING': '\033[93m',  # 亮黄色
        'ERROR': '\033[91m',  # 亮红色
        'CRITICAL': '\033[95m',  # 亮紫色
        'FIND': '\033[93m',  # 黄色
        'TRACE': '\033[90m',  # 灰色
        'RESET': '\033[0m',  # 重置颜色
    }
    
    ICONS = {
        'DEBUG': '🔧',
        'INFO': 'ℹ️ ',
        'SUCCESS': '✅',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '💀',
        'FIND': '🔍',
        'TRACE': '📋',
    }
    
    def format(self, record):
        # 新的颜色分类方案
        logger_colors = {
            # 核心AI模块 (蓝色系)
            'NET': '\033[94m',  # 亮蓝色 - 神经网络
            'MODEL': '\033[96m',  # 亮青色 - 模型
            'TRAIN': '\033[95m',  # 亮紫色 - 训练
            'GRAD': '\033[93m',  # 黄色 - 梯度
            'OPT': '\033[92m',  # 绿色 - 优化器
            'EVAL': '\033[97m',  # 白色 - 评估
            
            # 数据模块 (绿色系)
            'DATA': '\033[32m',  # 深绿色 - 数据
            'IO': '\033[36m',  # 青色 - 输入输出
            'CACHE': '\033[90m',  # 灰色 - 缓存
            
            # 系统模块 (橙色/红色系)
            'SYS': '\033[33m',  # 橙色 - 系统
            'SECURITY': '\033[91m',  # 红色 - 安全
            'TEST': '\033[35m',  # 粉紫色 - 测试
            
            # 服务模块 (紫色系)
            'WEB': '\033[95m',  # 亮紫色 - 网络服务
            'API': '\033[94m',  # 蓝色 - API
            'DB': '\033[34m',  # 深蓝色 - 数据库
            
            # 通用
            'COM': '\033[37m',  # 亮灰色 - 通用
        }
        
        level_color = self.COLORS.get(record.levelname, '')
        logger_color = logger_colors.get(record.name, '\033[97m')
        icon = self.ICONS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        colored_level = f"{level_color}{record.levelname:8s}{reset}"
        colored_logger = f"{logger_color}{record.name:8s}{reset}"
        colored_message = f"{level_color}{icon} {record.msg}{reset}"
        
        record.levelname = colored_level
        record.name = colored_logger
        record.msg = colored_message
        
        return super().format(record)


def setup_colored_logging(run_name=None):
    """初始化彩色日志系统"""
    global net_logger, train_logger, grad_logger, data_logger, model_logger
    global opt_logger, eval_logger, io_logger, sys_logger, web_logger
    global db_logger, api_logger, test_logger, security_logger, cache_logger
    global com_logger, _initialized
    
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / "log" / "his"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if run_name is None:
        run_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"log_{run_name}.log"
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'color_enhanced': {
                '()': EnhancedColorFormatter,
                'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'file_plain': {
                'format': '%(asctime)s | %(name)-8s | %(levelname)-8s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(log_file),
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'file_plain',
                'level': 'DEBUG',
                'encoding': 'utf-8'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'color_enhanced',
                'level': 'DEBUG',
            }
        },
        'loggers': {
            # 核心AI模块
            'NET': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
            'MODEL': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
            'TRAIN': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'GRAD': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
            'OPT': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'EVAL': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            
            # 数据模块
            'DATA': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'IO': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'CACHE': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
            
            # 系统模块
            'SYS': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'SECURITY': {'handlers': ['file', 'console'], 'level': 'WARNING', 'propagate': False},
            'TEST': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
            
            # 服务模块
            'WEB': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'API': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'DB': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            
            # 通用
            'COM': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': False},
        }
    }
    
    logging.config.dictConfig(config)
    
    # 添加自定义日志级别
    def log_success(self, message, *args, **kwargs):
        if self.isEnabledFor(25):
            self._log(25, message, args, **kwargs)
    
    def log_find(self, message, *args, **kwargs):
        if self.isEnabledFor(15):
            self._log(15, message, args, **kwargs)
    
    def log_trace(self, message, *args, **kwargs):
        if self.isEnabledFor(5):
            self._log(5, message, args, **kwargs)
    
    logging.addLevelName(25, 'SUCCESS')
    logging.addLevelName(15, 'FIND')
    logging.addLevelName(5, 'TRACE')
    logging.Logger.success = log_success
    logging.Logger.find = log_find
    logging.Logger.trace = log_trace
    
    # 初始化所有logger实例
    net_logger = logging.getLogger('NET')
    model_logger = logging.getLogger('MODEL')
    train_logger = logging.getLogger('TRAIN')
    grad_logger = logging.getLogger('GRAD')
    opt_logger = logging.getLogger('OPT')
    eval_logger = logging.getLogger('EVAL')
    data_logger = logging.getLogger('DATA')
    io_logger = logging.getLogger('IO')
    cache_logger = logging.getLogger('CACHE')
    sys_logger = logging.getLogger('SYS')
    security_logger = logging.getLogger('SECURITY')
    test_logger = logging.getLogger('TEST')
    web_logger = logging.getLogger('WEB')
    api_logger = logging.getLogger('API')
    db_logger = logging.getLogger('DB')
    com_logger = logging.getLogger('COM')
    
    _initialized = True
    
    com_logger.success("🌈 彩色日志系统初始化完成！")
    com_logger.info(f"📁 日志文件: {log_file}")
    
    return str(log_file)


class LoggerProxy:
    """Logger代理类"""
    
    def __init__(self, logger):
        self._logger = logger
    
    def __getattr__(self, name):
        return getattr(self._logger, name)


# 创建所有代理实例
net_logger = LoggerProxy(logging.getLogger('NET'))
model_logger = LoggerProxy(logging.getLogger('MODEL'))
train_logger = LoggerProxy(logging.getLogger('TRAIN'))
grad_logger = LoggerProxy(logging.getLogger('GRAD'))
opt_logger = LoggerProxy(logging.getLogger('OPT'))
eval_logger = LoggerProxy(logging.getLogger('EVAL'))
data_logger = LoggerProxy(logging.getLogger('DATA'))
io_logger = LoggerProxy(logging.getLogger('IO'))
cache_logger = LoggerProxy(logging.getLogger('CACHE'))
sys_logger = LoggerProxy(logging.getLogger('SYS'))
security_logger = LoggerProxy(logging.getLogger('SECURITY'))
test_logger = LoggerProxy(logging.getLogger('TEST'))
web_logger = LoggerProxy(logging.getLogger('WEB'))
api_logger = LoggerProxy(logging.getLogger('API'))
db_logger = LoggerProxy(logging.getLogger('DB'))
com_logger = LoggerProxy(logging.getLogger('COM'))


class log:
    """
    统一日志接口 - 完整分类版本
    """
    
    # ===== COM Logger (通用) =====
    @staticmethod
    def com_info(message):
        com_logger.info(message)
    
    @staticmethod
    def com_debug(message):
        com_logger.debug(message)
    
    @staticmethod
    def com_warning(message):
        com_logger.warning(message)
    
    @staticmethod
    def com_error(message):
        com_logger.error(message)
    
    @staticmethod
    def com_success(message):
        com_logger.success(message)
    
    @staticmethod
    def com_find(message):
        com_logger.find(message)
    
    @staticmethod
    def com_trace(message):
        com_logger.trace(message)
    
    # ===== NET Logger (神经网络) =====
    @staticmethod
    def net_info(message):
        net_logger.info(message)
    
    @staticmethod
    def net_debug(message):
        net_logger.debug(message)
    
    @staticmethod
    def net_warning(message):
        net_logger.warning(message)
    
    @staticmethod
    def net_error(message):
        net_logger.error(message)
    
    @staticmethod
    def net_success(message):
        net_logger.success(message)
    
    @staticmethod
    def net_find(message):
        net_logger.find(message)
    
    @staticmethod
    def net_trace(message):
        net_logger.trace(message)
    
    # ===== MODEL Logger (模型) =====
    @staticmethod
    def model_info(message):
        model_logger.info(message)
    
    @staticmethod
    def model_debug(message):
        model_logger.debug(message)
    
    @staticmethod
    def model_warning(message):
        model_logger.warning(message)
    
    @staticmethod
    def model_error(message):
        model_logger.error(message)
    
    @staticmethod
    def model_success(message):
        model_logger.success(message)
    
    @staticmethod
    def model_find(message):
        model_logger.find(message)
    
    @staticmethod
    def model_trace(message):
        model_logger.trace(message)
    
    # ===== TRAIN Logger (训练) =====
    @staticmethod
    def train_info(message):
        train_logger.info(message)
    
    @staticmethod
    def train_debug(message):
        train_logger.debug(message)
    
    @staticmethod
    def train_warning(message):
        train_logger.warning(message)
    
    @staticmethod
    def train_error(message):
        train_logger.error(message)
    
    @staticmethod
    def train_success(message):
        train_logger.success(message)
    
    @staticmethod
    def train_find(message):
        train_logger.find(message)
    
    @staticmethod
    def train_trace(message):
        train_logger.trace(message)
    
    # ===== GRAD Logger (梯度) =====
    @staticmethod
    def grad_info(message):
        grad_logger.info(message)
    
    @staticmethod
    def grad_debug(message):
        grad_logger.debug(message)
    
    @staticmethod
    def grad_warning(message):
        grad_logger.warning(message)
    
    @staticmethod
    def grad_error(message):
        grad_logger.error(message)
    
    @staticmethod
    def grad_success(message):
        grad_logger.success(message)
    
    @staticmethod
    def grad_find(message):
        grad_logger.find(message)
    
    @staticmethod
    def grad_trace(message):
        grad_logger.trace(message)
    
    # ===== OPT Logger (优化器) =====
    @staticmethod
    def opt_info(message):
        opt_logger.info(message)
    
    @staticmethod
    def opt_debug(message):
        opt_logger.debug(message)
    
    @staticmethod
    def opt_warning(message):
        opt_logger.warning(message)
    
    @staticmethod
    def opt_error(message):
        opt_logger.error(message)
    
    @staticmethod
    def opt_success(message):
        opt_logger.success(message)
    
    @staticmethod
    def opt_find(message):
        opt_logger.find(message)
    
    @staticmethod
    def opt_trace(message):
        opt_logger.trace(message)
    
    # ===== EVAL Logger (评估) =====
    @staticmethod
    def eval_info(message):
        eval_logger.info(message)
    
    @staticmethod
    def eval_debug(message):
        eval_logger.debug(message)
    
    @staticmethod
    def eval_warning(message):
        eval_logger.warning(message)
    
    @staticmethod
    def eval_error(message):
        eval_logger.error(message)
    
    @staticmethod
    def eval_success(message):
        eval_logger.success(message)
    
    @staticmethod
    def eval_find(message):
        eval_logger.find(message)
    
    @staticmethod
    def eval_trace(message):
        eval_logger.trace(message)
    
    # ===== DATA Logger (数据) =====
    @staticmethod
    def data_info(message):
        data_logger.info(message)
    
    @staticmethod
    def data_debug(message):
        data_logger.debug(message)
    
    @staticmethod
    def data_warning(message):
        data_logger.warning(message)
    
    @staticmethod
    def data_error(message):
        data_logger.error(message)
    
    @staticmethod
    def data_success(message):
        data_logger.success(message)
    
    @staticmethod
    def data_find(message):
        data_logger.find(message)
    
    @staticmethod
    def data_trace(message):
        data_logger.trace(message)
    
    # ===== IO Logger (输入输出) =====
    @staticmethod
    def io_info(message):
        io_logger.info(message)
    
    @staticmethod
    def io_debug(message):
        io_logger.debug(message)
    
    @staticmethod
    def io_warning(message):
        io_logger.warning(message)
    
    @staticmethod
    def io_error(message):
        io_logger.error(message)
    
    @staticmethod
    def io_success(message):
        io_logger.success(message)
    
    @staticmethod
    def io_find(message):
        io_logger.find(message)
    
    @staticmethod
    def io_trace(message):
        io_logger.trace(message)
    
    # ===== CACHE Logger (缓存) =====
    @staticmethod
    def cache_info(message):
        cache_logger.info(message)
    
    @staticmethod
    def cache_debug(message):
        cache_logger.debug(message)
    
    @staticmethod
    def cache_warning(message):
        cache_logger.warning(message)
    
    @staticmethod
    def cache_error(message):
        cache_logger.error(message)
    
    @staticmethod
    def cache_success(message):
        cache_logger.success(message)
    
    @staticmethod
    def cache_find(message):
        cache_logger.find(message)
    
    @staticmethod
    def cache_trace(message):
        cache_logger.trace(message)
    
    # ===== SYS Logger (系统) =====
    @staticmethod
    def sys_info(message):
        sys_logger.info(message)
    
    @staticmethod
    def sys_debug(message):
        sys_logger.debug(message)
    
    @staticmethod
    def sys_warning(message):
        sys_logger.warning(message)
    
    @staticmethod
    def sys_error(message):
        sys_logger.error(message)
    
    @staticmethod
    def sys_success(message):
        sys_logger.success(message)
    
    @staticmethod
    def sys_find(message):
        sys_logger.find(message)
    
    @staticmethod
    def sys_trace(message):
        sys_logger.trace(message)
    
    # ===== SECURITY Logger (安全) =====
    @staticmethod
    def security_info(message):
        security_logger.info(message)
    
    @staticmethod
    def security_debug(message):
        security_logger.debug(message)
    
    @staticmethod
    def security_warning(message):
        security_logger.warning(message)
    
    @staticmethod
    def security_error(message):
        security_logger.error(message)
    
    @staticmethod
    def security_success(message):
        security_logger.success(message)
    
    @staticmethod
    def security_find(message):
        security_logger.find(message)
    
    @staticmethod
    def security_trace(message):
        security_logger.trace(message)
    
    # ===== TEST Logger (测试) =====
    @staticmethod
    def test_info(message):
        test_logger.info(message)
    
    @staticmethod
    def test_debug(message):
        test_logger.debug(message)
    
    @staticmethod
    def test_warning(message):
        test_logger.warning(message)
    
    @staticmethod
    def test_error(message):
        test_logger.error(message)
    
    @staticmethod
    def test_success(message):
        test_logger.success(message)
    
    @staticmethod
    def test_find(message):
        test_logger.find(message)
    
    @staticmethod
    def test_trace(message):
        test_logger.trace(message)
    
    # ===== WEB Logger (网络服务) =====
    @staticmethod
    def web_info(message):
        web_logger.info(message)
    
    @staticmethod
    def web_debug(message):
        web_logger.debug(message)
    
    @staticmethod
    def web_warning(message):
        web_logger.warning(message)
    
    @staticmethod
    def web_error(message):
        web_logger.error(message)
    
    @staticmethod
    def web_success(message):
        web_logger.success(message)
    
    @staticmethod
    def web_find(message):
        web_logger.find(message)
    
    @staticmethod
    def web_trace(message):
        web_logger.trace(message)
    
    # ===== API Logger (API) =====
    @staticmethod
    def api_info(message):
        api_logger.info(message)
    
    @staticmethod
    def api_debug(message):
        api_logger.debug(message)
    
    @staticmethod
    def api_warning(message):
        api_logger.warning(message)
    
    @staticmethod
    def api_error(message):
        api_logger.error(message)
    
    @staticmethod
    def api_success(message):
        api_logger.success(message)
    
    @staticmethod
    def api_find(message):
        api_logger.find(message)
    
    @staticmethod
    def api_trace(message):
        api_logger.trace(message)
    
    # ===== DB Logger (数据库) =====
    @staticmethod
    def db_info(message):
        db_logger.info(message)
    
    @staticmethod
    def db_debug(message):
        db_logger.debug(message)
    
    @staticmethod
    def db_warning(message):
        db_logger.warning(message)
    
    @staticmethod
    def db_error(message):
        db_logger.error(message)
    
    @staticmethod
    def db_success(message):
        db_logger.success(message)
    
    @staticmethod
    def db_find(message):
        db_logger.find(message)
    
    @staticmethod
    def db_trace(message):
        db_logger.trace(message)
    
    # ===== 快捷方法 (保持向后兼容) =====
    @staticmethod
    def info(message):
        com_logger.info(message)
    
    @staticmethod
    def debug(message):
        com_logger.debug(message)
    
    @staticmethod
    def warning(message):
        com_logger.warning(message)
    
    @staticmethod
    def error(message):
        com_logger.error(message)
    
    @staticmethod
    def success(message):
        com_logger.success(message)
    
    @staticmethod
    def find(message):
        com_logger.find(message)
    
    @staticmethod
    def trace(message):
        com_logger.trace(message)
    
    # 常用模块的快捷方式
    @staticmethod
    def net(message):
        net_logger.info(message)
    
    @staticmethod
    def model(message):
        model_logger.info(message)
    
    @staticmethod
    def train(message):
        train_logger.info(message)
    
    @staticmethod
    def grad(message):
        grad_logger.info(message)
    
    @staticmethod
    def data(message):
        data_logger.info(message)
    
    @staticmethod
    def sys(message):
        sys_logger.info(message)
    
    # ===== 工具函数 =====
    @staticmethod
    @contextmanager
    def timer(operation_name):
        """计时器"""
        start_time = time.time()
        com_logger.info(f"⏱️  开始: {operation_name}")
        try:
            yield
        finally:
            end_time = time.time()
            com_logger.info(f"⏱️  完成: {operation_name} - 耗时: {end_time - start_time:.2f}秒")
    
    @staticmethod
    def memory():
        """内存使用"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            com_logger.debug(f"💾 内存使用: {memory_info.rss / 1024 / 1024:.1f} MB")
        except ImportError:
            com_logger.debug("💾 内存监控需要安装 psutil 库")
    
    @staticmethod
    def set_level(logger_name, level):
        """设置日志级别"""
        levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if level.upper() in levels:
            logger = getattr(log, f"{logger_name.lower()}_logger", None)
            if logger:
                logger.setLevel(getattr(logging, level.upper()))
    
    @staticmethod
    def status():
        """系统状态"""
        com_logger.info("📊 系统状态检查")
        return True


__all__ = ['setup_colored_logging', 'log']