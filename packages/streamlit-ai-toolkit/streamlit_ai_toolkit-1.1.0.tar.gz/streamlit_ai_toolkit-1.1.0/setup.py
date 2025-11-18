#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="streamlit_ai_toolkit",      # pip项目发布的名称（使用下划线）
    version="1.1.0",                   # 版本号，数值大的会优先被pip
    keywords=["streamlit", "ai", "rag", "multimodal", "nlp", "computer-vision"],  # 关键字
    description="A comprehensive AI toolkit for Streamlit applications with RAG and multimodal capabilities",  # 描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",             # 许可证

    url="https://github.com/xiaozhou/streamlit-ai-toolkit",  # 项目相关文件地址
    author="Xiaozhou Team",            # 作者
    author_email="xiaozhou@example.com",

    # 只打包当前目录的.py文件，不使用find_packages
    py_modules=["__init__", "ai_services", "ui_components"],
    include_package_data=True,
    platforms="any",
    python_requires=">=3.8",

    install_requires=[                 # 这个项目依赖的第三方库
        "streamlit>=1.28.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.4",
        "diffusers>=0.21.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "Pillow>=9.0.0",
        "numpy>=1.24.0",
        "requests>=2.28.0",
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)

