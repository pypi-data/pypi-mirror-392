from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lili-logger",
    version="1.0.0",
    author="Lili",
    author_email="tkin.l@qq.com",
    description="一个帅气专业的彩色日志系统，为AI和深度学习项目提供强大的日志记录功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['log', 'log.*']),
    package_data={
        'log': ['config/*.yaml'],
    },
    include_package_data=True,
    install_requires=[
        "PyYAML>=5.4",
        "psutil>=5.8; platform_system != 'Windows'",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="logging, color, ai, deep learning, machine learning",
)