"""
streamlit-ai-toolkit CLI工具
用于初始化项目和复制模板文件
"""
import os
import shutil
import sys
from pathlib import Path


def get_templates_dir():
    """获取模板文件目录"""
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates"
    return templates_dir


def init_project(target_dir="."):
    """
    初始化项目，复制所有模板文件到目标目录
    
    Args:
        target_dir: 目标目录，默认为当前目录
    """
    templates_dir = get_templates_dir()
    
    if not templates_dir.exists():
        print(f"❌ 错误：模板目录不存在: {templates_dir}")
        return False
    
    target_path = Path(target_dir).resolve()

    print(f"📁 目标目录: {target_path}")
    print()
    
    # 要复制的文件列表
    files_to_copy = [
        "app.py",
        "ai_chat.py",
        "knowledge_base.py",
        "multimodal.py",
        "web_search.py",
        "deep_thinking.py",
        "ui_config.py",
        "utils.py",
        "sample_knowledge.json",
        "config.example.py",
        ".env.example",
        ".gitignore",
        "README.md"
    ]
    
    copied_files = []
    skipped_files = []
    
    for filename in files_to_copy:
        source_file = templates_dir / filename
        target_file = target_path / filename
        
        if not source_file.exists():
            print(f"⚠️  跳过: {filename} (模板文件不存在)")
            continue
        
        if target_file.exists():
            print(f"⏭️  跳过: {filename} (文件已存在)")
            skipped_files.append(filename)
            continue
        
        try:
            shutil.copy2(source_file, target_file)
            print(f"✅ 复制: {filename}")
            copied_files.append(filename)
        except Exception as e:
            print(f"❌ 错误: 复制 {filename} 失败 - {e}")
    
    print()
    print("=" * 60)
    print("📊 Initialization Complete!")
    print(f"✅ Successfully copied: {len(copied_files)} files")
    if skipped_files:
        print(f"⏭️  Skipped: {len(skipped_files)} files (already exist)")
    print("=" * 60)
    print()
    
    if copied_files:
        print("📝 Next Steps:")
        print()
        print("1. Configure API Keys")
        print("   Edit config.example.py or .env.example and add your API keys")
        print()
        print("2. Install Dependencies")
        print("   pip install streamlit openai sentence-transformers faiss-cpu torch diffusers transformers pillow")
        print()
        print("3. Run the Application")
        print("   streamlit run app.py")
        print()
        print("🎉 Happy coding!")
    else:
        print("💡 Tip: All files already exist, no need to reinitialize")
    
    return True


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            # 获取目标目录（如果提供）
            target_dir = sys.argv[2] if len(sys.argv) > 2 else "."
            init_project(target_dir)
        elif command == "help" or command == "--help" or command == "-h":
            print_help()
        else:
            print(f"❌ 未知命令: {command}")
            print()
            print_help()
    else:
        print_help()


def print_help():
    """打印帮助信息"""
    print("""
🚀 Streamlit AI Toolkit CLI

Usage:
    streamlit-ai-toolkit init [target_dir]    Initialize project (copy template files)
    streamlit-ai-toolkit help                 Show help information

Examples:
    # Initialize project in current directory
    streamlit-ai-toolkit init

    # Initialize project in specified directory
    streamlit-ai-toolkit init ./my_ai_app

Description:
    The init command will copy the following files to the target directory:
    - app.py                    Main application entry
    - ai_chat.py               AI chat module
    - knowledge_base.py        Knowledge base Q&A module
    - multimodal.py            Multimodal AI module
    - web_search.py            Web search module
    - deep_thinking.py         Deep thinking module
    - ui_config.py             UI configuration
    - utils.py                 Utility functions
    - sample_knowledge.json    Sample knowledge base
    - config.example.py        Configuration template
    - .env.example             Environment variables template
    - .gitignore               Git ignore file
    - README.md                Project documentation

    If files already exist, they will be skipped automatically.
""")


if __name__ == "__main__":
    main()

