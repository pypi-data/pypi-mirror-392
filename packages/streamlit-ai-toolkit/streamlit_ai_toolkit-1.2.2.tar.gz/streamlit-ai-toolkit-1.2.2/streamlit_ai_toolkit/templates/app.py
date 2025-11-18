"""
AI Toolkit - Streamlit Application
A comprehensive AI application framework with multiple AI capabilities.

TODO: Customize this application for your needs:
1. Change the app title and icon
2. Add or remove pages based on your requirements
3. Customize the sidebar navigation
4. Add authentication if needed
"""

import streamlit as st

# TODO: Customize page configuration
st.set_page_config(
    page_title="AI Toolkit",  # TODO: Change to your app name
    page_icon="🤖",  # TODO: Change to your preferred icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
with st.sidebar:
    st.title("🤖 AI Toolkit")  # TODO: Customize title
    st.markdown("*Powered by Streamlit AI Toolkit*")
    st.markdown("---")

    # TODO: Customize navigation options
    page = st.selectbox(
        "Select Module",
        [
            "💬 AI Chat",
            "📚 Knowledge Base Q&A",
            "🎨 Multimodal AI"
        ]
    )

    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    st.info("Make sure to configure your API keys in `config.py` or `.env` file before using.")


# Load corresponding page based on selection
if page == "💬 AI Chat":
    import ai_chat
    ai_chat.render_page()
elif page == "📚 Knowledge Base Q&A":
    import knowledge_base
    knowledge_base.render_page()
elif page == "🎨 Multimodal AI":
    import multimodal
    multimodal.render_page()
