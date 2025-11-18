#!/usr/bin/env python3
"""
本地功能测试
"""
import sys
import os
import time

import log
from log.core.loader import ConfigLoader
from log.core.manager import LogManager

# 确保使用当前目录的代码
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log import *


def main():
    print("🚀 开始 Lili Logger 本地测试...")
    
    # 1. 初始化测试
    # log_file = setup("local_test")
    # print(f"📁 日志文件: {log_file}")
    
    # 强制清理缓存
    LogManager._initialized = False
    ConfigLoader._config = None
    
    # 重新初始化
    # setup()  # 不传参数，使用配置文件
    
    # 检查日志文件路径
    status = log.status()
    print("当前日志文件:", status['log_file'])
    
    log.net_info("测试日志名称")
    
    
    # 2. 基本功能测试
    log.com_success("✅ 基本日志测试通过")
    log.com_info("ℹ️ 信息级别测试")
    log.com_warning("⚠️ 警告级别测试")
    log.com_error("❌ 错误级别测试")
    log.com_debug("🔧 调试级别测试")
    
    # 3. 分类日志测试
    log.net_info("神经网络初始化完成")
    log.model_success("模型加载成功")
    log.data_info("数据预处理完成")
    log.train_success("训练完成，准确率: 95.2%")
    
    # 4. 工具功能测试
    with log.timer("性能测试任务"):
        time.sleep(1)
        log.com_info("任务执行中...")
    
    # 5. 内存监控测试
    log.memory()
    
    # 6. 状态检查
    log.status()
    
    print("🎉 所有测试完成！检查控制台输出和日志文件。")


if __name__ == "__main__":
    main()