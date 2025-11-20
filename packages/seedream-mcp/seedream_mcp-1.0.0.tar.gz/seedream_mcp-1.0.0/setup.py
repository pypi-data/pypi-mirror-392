#!/usr/bin/env python3
"""
Seedream 4.0 MCP工具安装配置
"""

from setuptools import setup, find_packages
import os

# 获取当前脚本所在目录
here = os.path.abspath(os.path.dirname(__file__))

# 读取 README.md
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements.txt
requirements = []
try:
    with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # 如果找不到 requirements.txt，则使用默认依赖列表
    requirements = [
        "mcp>=1.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "volcengine-python-sdk[ark]>=1.0.0",
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
        "Pillow>=10.0.0"
    ]

setup(
    name="seedream-mcp",
    version="1.0.0",
    author="Seedream MCP Team",
    author_email="tengmmvp@qq.com",
    description="基于火山引擎Seedream 4.0 API的MCP工具，支持AI图像生成功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tengmmvp/seedream-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "seedream-mcp=seedream_mcp.server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)