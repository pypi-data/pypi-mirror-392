"""
UI配置文件
包含项目特定的UI样式配置
"""

# 渐变背景CSS
GRADIENT_BACKGROUND_CSS = """
<style>
.stApp {
    background: linear-gradient(-45deg, #FF6B6B, #FFD166, #06D6A0, #118AB2, #073B4C);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
"""

