#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
上传streamlit-ai-toolkit到PyPI（使用API Token）

使用方法：
    python upload_with_token.py

或者直接提供Token：
    python upload_with_token.py pypi-你的Token
"""

import os
import sys
import hashlib
import requests
from pathlib import Path
import getpass


def calculate_file_hash(filepath):
    """计算文件的MD5和SHA256哈希值"""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return md5_hash.hexdigest(), sha256_hash.hexdigest()


def upload_to_pypi(package_file, api_token, repository='https://upload.pypi.org/legacy/'):
    """
    上传包到PyPI
    
    Args:
        package_file: 包文件路径
        api_token: PyPI API Token
        repository: PyPI仓库地址
    
    Returns:
        bool: 上传是否成功
    """
    # 获取文件信息
    file_size = os.path.getsize(package_file)
    md5_digest, sha256_digest = calculate_file_hash(package_file)

    # 从文件名中提取版本号
    filename = Path(package_file).name
    # 例如: streamlit_ai_toolkit-1.1.0.tar.gz -> 1.1.0
    version = filename.replace('streamlit_ai_toolkit-', '').replace('.tar.gz', '')

    print(f"📦 准备上传: {filename}")
    print(f"   版本: {version}")
    print(f"   大小: {file_size / 1024:.2f} KB")
    print(f"   MD5: {md5_digest}")
    print(f"   SHA256: {sha256_digest}")
    print()

    # 准备上传数据
    with open(package_file, 'rb') as f:
        file_content = f.read()

    # 构建multipart/form-data（包含完整的包元数据）
    data = {
        ':action': 'file_upload',
        'protocol_version': '1',
        'name': 'streamlit_ai_toolkit',  # 使用下划线
        'version': version,  # 从文件名自动提取
        'md5_digest': md5_digest,
        'sha256_digest': sha256_digest,
        'filetype': 'sdist',
        'pyversion': 'source',
        'metadata_version': '2.1',
        'summary': 'AI toolkit for Streamlit applications with RAG and multimodal capabilities',
        'author': 'Xiaozhou Team',
        'author_email': 'loserc@example.com',
        'license': 'MIT',
        'description': 'Streamlit AI Toolkit - RAG and Multimodal AI Services',
        'description_content_type': 'text/markdown',
        'keywords': 'streamlit,ai,rag,multimodal,nlp',
        'classifiers': [
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
    }
    
    files = {
        'content': (Path(package_file).name, file_content, 'application/gzip')
    }
    
    print(f"🚀 正在上传到 {repository}")
    print(f"   认证: API Token")
    print()
    
    try:
        # 创建session并禁用代理
        session = requests.Session()
        session.trust_env = False  # 禁用环境变量中的代理
        session.proxies = {
            'http': None,
            'https': None,
        }
        
        # 发送请求（使用API Token认证）
        response = session.post(
            repository,
            data=data,
            files=files,
            auth=('__token__', api_token),  # 使用Token认证
            timeout=60
        )
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 上传成功！")
            print()
            print("查看项目:")
            print("   https://pypi.org/project/streamlit-ai-toolkit/")
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


def get_api_token():
    """获取API Token（从命令行参数或用户输入）"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        token = sys.argv[1]
        if token.startswith('pypi-'):
            print("✅ 使用命令行提供的API Token")
            return token
        else:
            print("❌ Token格式错误！Token应该以 'pypi-' 开头")
            return None
    
    # 提示用户输入
    print("⚠️  PyPI不再支持用户名/密码认证！")
    print("   必须使用API Token")
    print()
    print("📝 获取Token步骤：")
    print("   1. 访问: https://pypi.org/account/login/")
    print("      用户名: loserc")
    print("      密码: na4nK_NhUcDJ943")
    print()
    print("   2. 登录后访问: https://pypi.org/manage/account/#api-tokens")
    print("   3. 点击 'Add API token'")
    print("   4. Token name: streamlit-ai-toolkit-upload")
    print("   5. Scope: Entire account (首次上传必须选这个)")
    print("   6. 点击 'Add token'")
    print("   7. 复制生成的Token（只显示一次！）")
    print()
    
    # 提示用户输入Token
    token_input = getpass.getpass("请输入你的PyPI API Token（包括pypi-前缀）: ")
    
    if not token_input:
        print("❌ 未输入Token")
        return None
    
    if not token_input.startswith('pypi-'):
        print("❌ Token格式错误！Token应该以 'pypi-' 开头")
        return None
    
    return token_input


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
    
    # 获取API Token
    api_token = get_api_token()
    if not api_token:
        return 1
    
    print()
    
    # 上传
    success = upload_to_pypi(str(package_file), api_token)
    
    if success:
        print()
        print("=" * 60)
        print("  🎉 发布成功！")
        print("=" * 60)
        print()
        print("📚 下一步：")
        print("   1. 访问: https://pypi.org/project/streamlit-ai-toolkit/")
        print("   2. 测试安装: pip install streamlit-ai-toolkit")
        print("   3. 测试导入: python -c \"from streamlit_ai_toolkit import RAGService\"")
        return 0
    else:
        print()
        print("=" * 60)
        print("  ❌ 发布失败")
        print("=" * 60)
        print()
        print("💡 常见问题：")
        print("   1. Token是否正确（包括pypi-前缀）？")
        print("   2. Token是否已过期？")
        print("   3. 包名是否已存在且版本号重复？")
        print()
        print("📖 查看详细指南: 官方上传指南.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())

