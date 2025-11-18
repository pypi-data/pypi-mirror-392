"""
日志管理器
负责日志系统的初始化和核心管理功能
"""

import logging
import logging.config
import time
import os
import inspect
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from .loader import ConfigLoader
from .proxy import LoggerProxy


class LogManager:
    """
    日志管理器
    提供日志系统的初始化和核心管理功能
    """
    
    # 类变量存储状态
    _initialized = False
    _log_file_path = None
    
    # 日志器实例字典
    _loggers = {}
    
    @classmethod
    def _get_project_root(cls):
        """
        获取项目根目录（包外层）

        Returns:
            Path: 项目根目录路径
        """
        # 方法1: 通过环境变量获取（用户显式指定）
        env_root = os.environ.get('LILI_LOGGER_PROJECT_ROOT')
        if env_root:
            return Path(env_root)
        
        # 方法2: 通过调用栈找到最外层项目目录
        frame = inspect.currentframe()
        project_root = None
        
        # 向上遍历调用栈，找到第一个不在site-packages中的文件
        while frame:
            filename = frame.f_code.co_filename
            # 排除包内文件、Python标准库、第三方包
            if ('site-packages' not in filename and
                    'dist-packages' not in filename and
                    'lib/python' not in filename):
                # 获取该文件所在目录作为候选项目根目录
                candidate = Path(filename).parent
                # 检查是否是合理的项目目录（包含常见项目文件）
                if (candidate / 'main.py').exists() or (candidate / 'app.py').exists() or \
                        (candidate / 'requirements.txt').exists() or (candidate / 'setup.py').exists() or \
                        (candidate / '.git').exists():
                    project_root = candidate
                    break
            frame = frame.f_back
        
        # 方法3: 使用当前工作目录作为备选
        if not project_root:
            project_root = Path.cwd()
        
        return project_root
    
    @classmethod
    def _get_log_directory(cls):
        """
        获取日志目录路径

        Returns:
            Path: 日志目录路径
        """
        project_root = cls._get_project_root()
        
        # 在项目根目录下创建 logs 文件夹
        log_dir = project_root / 'logs'
        
        # 确保目录存在
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir
    
    @classmethod
    def _create_project_config_if_needed(cls):
        """
        如果项目目录没有配置文件，自动创建一个简化的配置模板
        """
        project_root = cls._get_project_root()
        project_config_path = project_root / "lili_logger_config.yaml"
        
        # 如果项目目录没有配置文件，自动创建
        if not project_config_path.exists():
            config_template = '''# Lili Logger 项目级配置文件 (简化版)
    # 此文件只覆盖部分配置，其他配置使用包内默认值
    # 修改后无需重新安装包，立即生效

    # 运行名称配置 - 控制日志文件名
    system:
      default_run_name: "default_run"  # 修改这里来改变日志文件名

    # 日志级别配置 - 只修改常用的几个级别
    loggers:
      NET:
        level: "INFO"
      DATA:
        level: "INFO"
      TRAIN:
        level: "INFO"
      COM:
        level: "INFO"

    # 文件名格式说明:
    # - "default_run": log_20251116_143253.log (纯时间戳)
    # - "succ": log_succ_20251116_143253.log (名称+时间戳)
    # - "my_project": log_my_project_20251116_143253.log
    # 完整配置请参考包内的 logging.yaml 文件
    '''
            
            # 确保目录存在
            project_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入配置文件
            with open(project_config_path, 'w', encoding='utf-8') as f:
                f.write(config_template)
            
            print(f"📝 已自动创建简化版项目级配置文件: {project_config_path}")
            print("💡 你可以修改 default_run_name 来改变日志文件名格式")
        
        return project_config_path
    
    
    
    
    
    @classmethod
    def initialize(cls, run_name=None, config_path=None):
        """
        初始化日志系统

        Args:
            run_name: 运行名称，用于日志文件名
            config_path: 配置文件路径

        Returns:
            str: 日志文件路径

        Raises:
            Exception: 初始化失败时抛出
        """
        try:
            # 如果没有指定配置文件，自动创建项目级配置模板
            if config_path is None:
                cls._create_project_config_if_needed()
            
            # 加载配置
            config = ConfigLoader.initialize(config_path)
            system_config = config['system']
            paths_config = config['paths']
            
            # 获取项目级日志目录（包外层）
            log_dir = cls._get_log_directory()
            
            # 自动创建目录
            if system_config.get('auto_create_dirs', True):
                log_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成运行名称
            if run_name is None:
                run_name = system_config.get('default_run_name', 'default_run')
            
            # 处理运行名称格式
            if run_name == 'default_run':
                # 默认使用时间戳
                run_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            else:
                # 自定义名称 + 时间戳
                run_name = f"{run_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 准备日志配置
            log_config = config.copy()
            
            # 替换日志文件路径中的占位符 - 使用项目级目录
            log_file_name = f"log_{run_name}.log"
            cls._log_file_path = log_dir / log_file_name
            
            log_config['handlers']['file']['filename'] = str(cls._log_file_path)
            
            # 构建标准的logging配置
            standard_config = {
                'version': log_config['version'],
                'disable_existing_loggers': log_config['disable_existing_loggers'],
                'formatters': log_config['formatters'],
                'handlers': log_config['handlers'],
                'loggers': log_config['loggers']
            }
            
            # 配置日志系统
            logging.config.dictConfig(standard_config)
            
            # 设置自定义级别
            cls._setup_custom_levels()
            
            # 初始化所有日志器实例
            logger_names = list(log_config['loggers'].keys())
            for name in logger_names:
                cls._loggers[name] = LoggerProxy(name)
            
            cls._initialized = True
            
            # 记录初始化成功
            com_logger = cls.get_logger('COM')
            
            # 系统启动信息
            com_logger.success(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            com_logger.success(">                       LILI LOG HAS PRAPARED ALREADY                        >")
            com_logger.success("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            com_logger.info(f"📁 日志文件: {cls._log_file_path}")
            com_logger.info(f"⚙️ 配置文件: {ConfigLoader._config_path}")
            com_logger.info(f"🔧 已加载: {len(logger_names)} 个部署")
            com_logger.success(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            
            # 额外输出项目信息（调试用）
            project_root = cls._get_project_root()
            com_logger.debug(f"📂 项目根目录: {project_root}")
            com_logger.debug(f"📂 日志目录: {log_dir}")
            
            return str(cls._log_file_path)
        
        except Exception as e:
            # 如果初始化失败，使用基础logging记录错误
            logging.basicConfig(level=logging.ERROR)
            logging.error(f"日志系统初始化失败: {e}")
            raise

    
    @classmethod
    def _setup_custom_levels(cls):
        """
        设置自定义日志级别
        """
        config = ConfigLoader.get_config()
        custom_levels = config['custom_levels']
        
        # 添加自定义级别到logging系统
        for level_name, level_info in custom_levels.items():
            level_value = level_info['value']
            logging.addLevelName(level_value, level_name)
        
        # 为Logger类添加自定义级别方法
        cls._add_custom_log_methods()
    
    @classmethod
    def _add_custom_log_methods(cls):
        """添加自定义日志方法到Logger类"""
        
        def log_success(self, message, *args, **kwargs):
            """记录成功操作"""
            if self.isEnabledFor(25):
                self._log(25, message, args, **kwargs)
        
        def log_find(self, message, *args, **kwargs):
            """记录查找/发现操作"""
            if self.isEnabledFor(15):
                self._log(15, message, args, **kwargs)
        
        def log_trace(self, message, *args, **kwargs):
            """记录详细跟踪信息"""
            if self.isEnabledFor(5):
                self._log(5, message, args, **kwargs)
        
        # 将自定义方法添加到Logger类
        logging.Logger.success = log_success
        logging.Logger.find = log_find
        logging.Logger.trace = log_trace
    
    @classmethod
    def get_logger(cls, logger_name):
        """
        获取指定名称的日志器

        Args:
            logger_name: 日志器名称

        Returns:
            LoggerProxy: 日志器代理实例
        """
        if not cls._initialized:
            raise RuntimeError("日志系统未初始化，请先调用 initialize() 方法")
        
        if logger_name not in cls._loggers:
            raise ValueError(f"未知的日志器: {logger_name}")
        
        return cls._loggers[logger_name]
    
    @classmethod
    def get_all_loggers(cls):
        """
        获取所有日志器

        Returns:
            dict: 所有日志器字典
        """
        return cls._loggers.copy()
    
    @classmethod
    def set_level(cls, logger_name, level):
        """
        设置日志级别

        Args:
            logger_name: 日志器名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if level.upper() in levels:
            logger = cls.get_logger(logger_name)
            logger.setLevel(getattr(logging, level.upper()))
    
    @classmethod
    def get_status(cls):
        """
        获取系统状态信息

        Returns:
            dict: 状态信息字典
        """
        config = ConfigLoader.get_config()
        return {
            "initialized": cls._initialized,
            "log_file": str(cls._log_file_path) if cls._log_file_path else None,
            "config_file": str(ConfigLoader._config_path),
            "loggers_count": len(cls._loggers),
            "loggers": list(cls._loggers.keys()),
            "version": "1.0.0"
        }
    
    @classmethod
    def is_initialized(cls):
        """
        检查日志系统是否已初始化

        Returns:
            bool: 初始化状态
        """
        return cls._initialized
    
    @classmethod
    @contextmanager
    def timer(cls, operation_name, logger_name='COM'):
        """
        计时器上下文管理器

        Args:
            operation_name: 操作名称
            logger_name: 使用的日志器名称

        Yields:
            None
        """
        start_time = time.time()
        logger = cls.get_logger(logger_name)
        logger.info(f"⏱️ 开始: {operation_name}")
        
        try:
            yield
        except Exception as e:
            logger.error(f"❌ 操作失败: {operation_name} - {e}")
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"⏱️ 完成: {operation_name} - 耗时: {duration:.2f}秒")
    
    @classmethod
    def log_memory_usage(cls, logger_name='COM'):
        """
        记录内存使用情况

        Args:
            logger_name: 使用的日志器名称
        """
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            logger = cls.get_logger(logger_name)
            logger.debug(f"💾 内存使用: {memory_mb:.1f} MB")
        
        except ImportError:
            logger = cls.get_logger(logger_name)
            logger.debug("💾 内存监控需要安装 psutil 库")