"""
小舟智能客服平台 - 主应用入口
"""
import streamlit as st

# 配置页面
st.set_page_config(
    page_title="小舟智能客服平台",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 侧边栏导航
with st.sidebar:
    st.title("🚢 小舟智能客服平台")
    st.markdown("---")
    
    page = st.selectbox(
        "选择功能模块",
        [
            "任务一：智能客服助手",
            "任务二：知识库问答 (RAG)",
            "任务三：多模态智能"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📚 项目信息")
    st.info("""
    **小舟** - 新一代AI智能客服平台
    
    - 任务一：基础框架搭建
    - 任务二：知识库集成（RAG）
    - 任务三：多模态能力扩展
    """)

# 根据选择加载对应页面
if page == "任务一：智能客服助手":
    import page_1_streaming
    page_1_streaming.render_page()
elif page == "任务二：知识库问答 (RAG)":
    import page_2_rag
    page_2_rag.render_page()
elif page == "任务三：多模态智能":
    import page_3_image
    page_3_image.render_page()

