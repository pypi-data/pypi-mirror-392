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
    
    print("🚀 开始初始化小舟智能客服平台项目...")
    print(f"📁 目标目录: {target_path}")
    print()
    
    # 要复制的文件列表
    files_to_copy = [
        "app.py",
        "page_1_streaming.py",
        "page_2_rag.py",
        "page_3_image.py",
        "ui_config.py",
        "utils.py",
        "products.json",
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
    print("📊 初始化完成！")
    print(f"✅ 成功复制: {len(copied_files)} 个文件")
    if skipped_files:
        print(f"⏭️  跳过: {len(skipped_files)} 个文件（已存在）")
    print("=" * 60)
    print()
    
    if copied_files:
        print("📝 下一步操作：")
        print()
        print("1. 配置API密钥")
        print("   编辑 utils.py 文件，替换 'your-api-key-here' 为您的通义千问API密钥")
        print()
        print("2. 安装依赖")
        print("   pip install streamlit openai sentence-transformers faiss-cpu numpy")
        print()
        print("3. 运行应用")
        print("   streamlit run app.py")
        print()
        print("🎉 祝您使用愉快！")
    else:
        print("💡 提示：所有文件都已存在，无需重新初始化")
    
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
🚢 streamlit-ai-toolkit CLI工具

用法:
    streamlit-ai-toolkit init [目标目录]    初始化项目（复制模板文件）
    streamlit-ai-toolkit help              显示帮助信息

示例:
    # 在当前目录初始化项目
    streamlit-ai-toolkit init
    
    # 在指定目录初始化项目
    streamlit-ai-toolkit init ./my_project

说明:
    init命令会将以下文件复制到目标目录：
    - app.py                  主应用入口
    - page_1_streaming.py     任务一：智能客服助手
    - page_2_rag.py          任务二：知识库问答
    - page_3_image.py        任务三：多模态智能
    - ui_config.py           UI配置文件
    - utils.py               工具函数
    - products.json          知识库数据
    - README.md              项目说明文档

    如果文件已存在，将自动跳过，不会覆盖。
""")


if __name__ == "__main__":
    main()

