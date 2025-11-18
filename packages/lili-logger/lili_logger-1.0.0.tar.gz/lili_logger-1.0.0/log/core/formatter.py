"""
颜色格式化器实现 - 简化版本
"""

import logging
import os
from .loader import ConfigLoader


class EnhancedColorFormatter(logging.Formatter):
    """
    增强版彩色日志格式化器 - 简化版本
    """
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        
        config = ConfigLoader.get_config()
        self.colors = config['colors']
        self.icons = config['icons']
        
        # 直接使用正确的ANSI转义序列
        self.color_codes = {
            'DEBUG': '\033[36m',
            'INFO': '\033[92m',
            'SUCCESS': '\033[32m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'CRITICAL': '\033[95m',
            'FIND': '\033[93m',
            'TRACE': '\033[90m',
            'RESET': '\033[0m'
        }
        
        self.logger_colors = {
            'NET': '\033[94m',
            'MODEL': '\033[96m',
            'TRAIN': '\033[95m',
            'GRAD': '\033[93m',
            'OPT': '\033[92m',
            'EVAL': '\033[97m',
            'DATA': '\033[32m',
            'IO': '\033[36m',
            'CACHE': '\033[90m',
            'SYS': '\033[33m',
            'SECURITY': '\033[91m',
            'TEST': '\033[35m',
            'WEB': '\033[95m',
            'API': '\033[94m',
            'DB': '\033[34m',
            'COM': '\033[37m'
        }
    
    def format(self, record):
        level_color = self.color_codes.get(record.levelname, '')
        logger_color = self.logger_colors.get(record.name, '\033[97m')
        icon = self.icons['level_icons'].get(record.levelname, '')
        reset = self.color_codes['RESET']
        
        icon = f"{icon} " if icon else ''
        
        colored_level = f"{level_color}{record.levelname:8s}{reset}"
        colored_logger = f"{logger_color}{record.name:8s}{reset}"
        colored_message = f"{level_color}{icon}{record.msg}{reset}"
        
        record.levelname = colored_level
        record.name = colored_logger
        record.msg = colored_message
        
        return super().format(record)
    
   