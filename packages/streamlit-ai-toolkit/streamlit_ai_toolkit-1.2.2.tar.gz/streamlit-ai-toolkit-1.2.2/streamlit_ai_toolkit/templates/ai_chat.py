"""
AI Chat Module - Streaming Conversation with LLM

This module provides a chat interface with:
- Streaming responses from OpenAI-compatible APIs
- Conversation history management
- Customizable model parameters

TODO: Customize this module for your needs:
1. Configure your API key in utils.py or config.py
2. Adjust model parameters (temperature, max_tokens, etc.)
3. Customize the UI and styling
4. Add system prompts or context
5. Implement conversation memory limits
"""

import streamlit as st
from openai import OpenAI
import utils
from ui_config import GRADIENT_BACKGROUND_CSS


def apply_css(css_code):
    """Apply custom CSS styling"""
    st.markdown(css_code, unsafe_allow_html=True)


def render_page():
    """
    Render the AI chat page

    TODO: Customize this function to match your requirements
    """
    # Page header
    st.title("💬 AI Chat Assistant")
    st.markdown("*Have a conversation with AI using OpenAI-compatible APIs*")

    # Apply custom styling
    apply_css(GRADIENT_BACKGROUND_CSS)

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Chat Settings")

        # TODO: Customize available models based on your API provider
        # Examples:
        # - OpenAI: ["gpt-4", "gpt-3.5-turbo"]
        # - Alibaba Qwen: ["qwen-plus", "qwen-turbo", "qwen-max"]
        # - DeepSeek: ["deepseek-chat"]
        model = st.selectbox(
            "Select Model",
            ["gpt-3.5-turbo", "gpt-4"],  # TODO: Update with your available models
            key="selected_model",
            help="Choose the AI model to use for conversation"
        )

        # Temperature control
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.05,
            key="temperature",
            help="Higher values make output more random, lower values more focused"
        )

        # TODO: Add more parameters
        # max_tokens = st.slider("Max Tokens", 100, 4000, 2000)
        # top_p = st.slider("Top P", 0.0, 1.0, 1.0)

        st.markdown("---")

        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        # TODO: Add export conversation button
        # if st.button("💾 Export Chat"):
        #     export_conversation()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

        # TODO: Add a system prompt to customize AI behavior
        # st.session_state.messages.append({
        #     "role": "system",
        #     "content": "You are a helpful AI assistant."
        # })

    # Display chat history
    for message in st.session_state.messages:
        # Skip system messages in display
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    # TODO: Customize the placeholder text
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            try:
                # Initialize OpenAI client
                # TODO: Make sure your API key and base URL are configured in utils.py
                client = OpenAI(
                    api_key=utils.get_api_key(),
                    base_url=utils.get_api_base()
                )

                # Call API with conversation history
                # TODO: Implement conversation memory limit to avoid token limits
                # For example, keep only last 10 messages
                response = client.chat.completions.create(
                    model=st.session_state.selected_model,
                    messages=st.session_state.messages,
                    temperature=st.session_state.temperature,
                    stream=True  # TODO: Set to True for streaming responses
                )

                # Display streaming response
                # TODO: Customize response display
                response_placeholder = st.empty()
                full_response = ""

                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)

                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                st.error(f"❌ Error calling API: {e}")
                st.info("💡 Make sure you have configured your API key in `utils.py` or `config.py`")

                # TODO: Add more specific error handling
                # - Check if API key is valid
                # - Check if model is available
                # - Handle rate limits
                # - Handle network errors
