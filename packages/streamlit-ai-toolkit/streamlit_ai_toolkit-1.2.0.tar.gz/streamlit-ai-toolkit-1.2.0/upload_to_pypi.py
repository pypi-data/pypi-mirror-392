#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接使用Python上传到PyPI（不依赖twine）
"""

import os
import sys
import hashlib
import requests
from pathlib import Path

def get_file_hash(filepath, algorithm='sha256'):
    """计算文件哈希值"""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def upload_to_pypi(package_file, username, password, repository='https://upload.pypi.org/legacy/'):
    """
    上传包到PyPI
    
    Args:
        package_file: 包文件路径
        username: PyPI用户名
        password: PyPI密码
        repository: PyPI仓库地址
    """
    
    if not os.path.exists(package_file):
        print(f"❌ 文件不存在: {package_file}")
        return False
    
    # 获取文件信息
    filename = os.path.basename(package_file)
    filesize = os.path.getsize(package_file)
    md5_hash = get_file_hash(package_file, 'md5')
    sha256_hash = get_file_hash(package_file, 'sha256')
    
    print(f"📦 准备上传: {filename}")
    print(f"   大小: {filesize / 1024:.2f} KB")
    print(f"   MD5: {md5_hash}")
    print(f"   SHA256: {sha256_hash}")
    print()
    
    # 准备上传数据
    with open(package_file, 'rb') as f:
        file_content = f.read()
    
    # 构建multipart/form-data
    data = {
        ':action': 'file_upload',
        'protocol_version': '1',
        'name': 'streamlit-ai-toolkit',
        'version': '1.0.0',
        'metadata_version': '2.1',
        'summary': 'A comprehensive AI toolkit for Streamlit applications with RAG and multimodal capabilities',
        'author': 'Xiaozhou Team',
        'author_email': 'xiaozhou@example.com',
        'license': 'MIT Licence',
        'description': 'A comprehensive AI toolkit for Streamlit applications',
        'keywords': 'streamlit,ai,rag,multimodal,nlp,computer-vision',
        'platform': 'any',
        'classifiers': [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
        ],
        'md5_digest': md5_hash,
        'sha256_digest': sha256_hash,
        'filetype': 'sdist',
        'pyversion': 'source',
    }
    
    files = {
        'content': (filename, file_content, 'application/gzip')
    }
    
    print(f"🚀 正在上传到 {repository}")
    print(f"   用户名: {username}")
    print()
    
    try:
        # 创建session并禁用代理
        session = requests.Session()
        session.trust_env = False  # 禁用环境变量中的代理
        session.proxies = {
            'http': None,
            'https': None,
        }

        # 发送请求
        response = session.post(
            repository,
            data=data,
            files=files,
            auth=(username, password),
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ 上传成功！")
            print()
            print("查看项目:")
            print(f"   https://pypi.org/project/streamlit-ai-toolkit/1.0.0/")
            print()
            print("安装命令:")
            print("   pip install streamlit-ai-toolkit")
            return True
        else:
            print(f"❌ 上传失败！")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("  上传 streamlit-ai-toolkit 到 PyPI")
    print("=" * 60)
    print()
    
    # 查找dist目录下的包文件
    dist_dir = Path(__file__).parent / 'dist'
    if not dist_dir.exists():
        print("❌ dist 目录不存在！请先运行 python setup.py sdist")
        return 1
    
    # 查找.tar.gz文件
    package_files = list(dist_dir.glob('*.tar.gz'))
    if not package_files:
        print("❌ 未找到包文件！请先运行 python setup.py sdist")
        return 1
    
    package_file = package_files[0]
    
    # PyPI认证信息
    username = 'loserc'
    password = 'na4nK_NhUcDJ943'
    
    # 上传
    success = upload_to_pypi(str(package_file), username, password)
    
    if success:
        print()
        print("=" * 60)
        print("  🎉 发布成功！")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("  ❌ 发布失败")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())

