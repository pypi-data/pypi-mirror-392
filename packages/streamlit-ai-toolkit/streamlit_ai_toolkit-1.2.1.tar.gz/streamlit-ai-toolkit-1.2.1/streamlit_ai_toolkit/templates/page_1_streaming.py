import streamlit as st
from openai import OpenAI
import utils
from ui_config import GRADIENT_BACKGROUND_CSS

def apply_css(css_code):
    """应用自定义CSS"""
    st.markdown(css_code, unsafe_allow_html=True)

def render_page():
    st.title("测试demo")

    apply_css(GRADIENT_BACKGROUND_CSS)

    with st.sidebar:
        st.header("控制台")
        st.selectbox("选择模型", ["qwen1.5-1.8b-chat", "qwen1.5-7b-chat"], key="selected_model")
        st.slider("模型温度", min_value=0.0, max_value=2.0, value=0.7, step=0.05, key="temperature")
        if st.button("清除历史记录"):
            st.session_state.clear()
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("您好，我是小艺。"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                client = OpenAI(
                    api_key=utils.get_api_key(),
                    base_url="",  #
                )
                # 上下文记忆 ---
                response = client.chat.completions.create(
                    model=st.session_state.selected_model,
                    messages=st.session_state.messages,
                    temperature=st.session_state.temperature,
                    stream=False
                )
                st.markdown(response.choices[0].message.content)
                response_content = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            except Exception as e:
                st.error(f"调用API时出错: {e}")

