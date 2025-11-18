"""
日志器代理类
提供懒加载和透明的日志器访问
"""

import logging


class LoggerProxy:
    """
    日志器代理类
    提供懒加载和透明的日志器访问，支持所有标准日志方法
    """
    
    def __init__(self, logger_name):
        """
        初始化代理

        Args:
            logger_name: 日志器名称
        """
        self._logger_name = logger_name
        self._logger = None
    
    def __getattr__(self, name):
        """
        透明代理所有日志方法

        Args:
            name: 方法名或属性名

        Returns:
            请求的方法或属性
        """
        if self._logger is None:
            self._logger = logging.getLogger(self._logger_name)
        return getattr(self._logger, name)
    
    def __repr__(self):
        """
        代理对象的字符串表示

        Returns:
            str: 代理对象描述
        """
        if self._logger is None:
            return f"LoggerProxy('{self._logger_name}') [未初始化]"
        else:
            return f"LoggerProxy('{self._logger_name}') [已初始化]"