"""
彩色日志系统包
提供分类化、彩色化的日志记录功能
"""

from log.api.logger import setup, Log

# 创建全局实例
log = Log()

# 导出公共接口
__all__ = [
    'setup',
    'log',
    'Log'
]

# 包版本
__version__ = '1.0.0'


# 安装后提示
def _print_install_info():
    import os
    import inspect
    from pathlib import Path
    
    # 获取项目根目录
    frame = inspect.currentframe()
    project_root = None
    while frame:
        filename = frame.f_code.co_filename
        if 'site-packages' not in filename and 'dist-packages' not in filename:
            project_root = Path(filename).parent
            break
        frame = frame.f_back
    
    if not project_root:
        project_root = Path.cwd()
    
    config_path = project_root / "logging_config.yaml"
    
    print("🌈 Lili Logger 安装成功!")
    print("📝 首次使用时会自动在项目根目录创建配置文件模板")
    print(f"📁 项目目录: {project_root}")
    print(f"⚙️  配置文件: {config_path} (首次使用时自动创建)")
    print("💡 修改配置文件后无需重新安装包")


# 只在第一次导入时显示
if not hasattr(_print_install_info, '_shown'):
    _print_install_info()
    _print_install_info._shown = True