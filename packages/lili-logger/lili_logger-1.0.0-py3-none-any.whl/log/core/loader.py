"""
配置加载器
负责加载和管理YAML配置文件
"""

import yaml
import os
import inspect
from pathlib import Path


class ConfigLoader:
    """
    配置加载器
    所有路径都从配置中读取，无硬编码路径
    """
    
    _config = None
    _config_path = None
    
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
    def _deep_merge(cls, base, update):
        """
        深度合并两个字典

        Args:
            base: 基础字典
            update: 更新字典

        Returns:
            dict: 合并后的字典
        """
        result = base.copy()
        
        for key, value in update.items():
            if (key in result and isinstance(result[key], dict)
                    and isinstance(value, dict)):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def _merge_configs(cls, project_config_path):
        """
        合并项目级配置和包内默认配置

        Args:
            project_config_path: 项目级配置文件路径
        """
        # 加载包内默认配置
        try:
            import pkg_resources
            default_config_path = pkg_resources.resource_filename('log', 'config/logging.yaml')
        except:
            import log.config as config_module
            default_config_path = Path(config_module.__file__).parent / "logging.yaml"
        
        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = yaml.safe_load(f)
        
        # 加载项目级配置
        with open(project_config_path, 'r', encoding='utf-8') as f:
            project_config = yaml.safe_load(f)
        
        # 深度合并配置（项目级配置覆盖默认配置）
        cls._config = cls._deep_merge(default_config, project_config)
        cls._config_path = Path(project_config_path)
        print(f"🔄 已合并项目级配置和默认配置")
    
    @classmethod
    def initialize(cls, config_path=None):
        """
        初始化配置加载器 - 支持配置合并

        Args:
            config_path: 配置文件路径，如果为None则使用配置中的默认路径

        Returns:
            dict: 配置字典

        Raises:
            FileNotFoundError: 配置文件不存在时抛出
        """
        # 优先查找项目级配置文件
        if config_path is None:
            project_root = cls._get_project_root()
            
            # 项目级配置文件搜索路径（按优先级排序）
            project_config_paths = [
                project_root / "lili_logger_config.yaml",  # 项目根目录
                project_root / "config" / "lili_logger_config.yaml",  # 项目config目录
                project_root / "logging_config.yaml",  # 兼容旧文件名
                Path.home() / "lili_logger_config.yaml",  # 用户目录
            ]
            
            config_path = None
            for candidate_path in project_config_paths:
                if candidate_path.exists():
                    config_path = candidate_path
                    print(f"✅ 使用项目级配置文件: {config_path}")
                    break
            
            # 如果没有找到项目级配置，使用包内默认配置
            if config_path is None:
                try:
                    import pkg_resources
                    config_path = pkg_resources.resource_filename('log', 'config/logging.yaml')
                except:
                    import log.config as config_module
                    config_path = Path(config_module.__file__).parent / "logging.yaml"
                print(f"ℹ️ 使用包内默认配置: {config_path}")
                cls._config_path = Path(config_path)
                with open(cls._config_path, 'r', encoding='utf-8') as f:
                    cls._config = yaml.safe_load(f)
            else:
                # 合并配置：项目级配置覆盖默认配置
                cls._merge_configs(config_path)
        
        else:
            # 显式指定配置文件路径
            cls._config_path = Path(config_path)
            if not cls._config_path.exists():
                raise FileNotFoundError(f"日志配置文件不存在: {cls._config_path}")
            
            with open(cls._config_path, 'r', encoding='utf-8') as f:
                cls._config = yaml.safe_load(f)
        
        # 验证配置完整性
        cls._validate_config()
        
        return cls._config
    
    @classmethod
    def _load_initial_config(cls, base_dir):
        """
        加载初始配置以获取路径信息

        Args:
            base_dir: 项目根目录

        Returns:
            dict: 初始配置
        """
        config_dir = "config"
        config_file = "logging.yaml"
        config_path = base_dir / config_dir / config_file
        
        if not config_path.exists():
            # 如果默认配置不存在，使用内置的路径配置
            return {
                'paths': {
                    'config_dir': 'config',
                    'core_dir': 'core',
                    'api_dir': 'api',
                    'his_dir': 'his',
                    'config_file': 'logging.yaml'
                }
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def _validate_config(cls):
        """
        验证配置的完整性和正确性
        """
        if cls._config is None:
            raise ValueError("配置未初始化")
        
        # 检查必需配置项
        required_sections = ['paths', 'formatters', 'handlers', 'loggers', 'colors', 'icons']
        for section in required_sections:
            if section not in cls._config:
                raise ValueError(f"配置缺少必需部分: {section}")
        
        # 检查必需的颜色定义
        required_colors = cls._config.get('validation', {}).get('required_colors', [])
        for color in required_colors:
            if color not in cls._config['colors']['level_colors']:
                raise ValueError(f"配置缺少必需的颜色定义: {color}")
    
    @classmethod
    def get_config(cls):
        """
        获取配置字典

        Returns:
            dict: 配置字典

        Raises:
            RuntimeError: 配置未初始化时抛出
        """
        if cls._config is None:
            cls.initialize()
        return cls._config
    
    @classmethod
    def get_log_directory(cls):
        """
        获取日志目录路径 - 现在返回项目级目录

        Returns:
            Path: 日志目录路径
        """
        # 不再使用包内目录，而是使用项目级目录
        project_root = cls._get_project_root()
        log_dir = project_root / 'logs'
        
        # 确保目录存在
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir
    
    @classmethod
    def get_log_file_path(cls, run_name):
        """
        获取日志文件路径 - 现在返回项目级路径

        Args:
            run_name: 运行名称

        Returns:
            Path: 日志文件路径
        """
        log_dir = cls.get_log_directory()
        return log_dir / f"log_{run_name}.log"
    
    @classmethod
    def reload_config(cls):
        """
        重新加载配置文件

        Returns:
            dict: 重新加载后的配置
        """
        cls._config = None
        return cls.initialize(cls._config_path)