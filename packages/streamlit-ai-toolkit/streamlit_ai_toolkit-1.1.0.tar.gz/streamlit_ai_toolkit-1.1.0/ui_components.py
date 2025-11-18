"""
UI组件库
提供通用的UI组件和样式工具
"""
import streamlit as st


def apply_css(css_code):
    """
    应用CSS样式（通用方法）

    参数：
        css_code: CSS代码字符串（可以包含<style>标签，也可以不包含）

    使用方法：
        from Library import apply_css

        # 方式1：直接传入CSS代码
        apply_css(".my-class { color: red; }")

        # 方式2：传入完整的HTML样式标签
        apply_css("<style>.my-class { color: red; }</style>")
    """
    if not css_code.strip().startswith("<style>"):
        css_code = f"<style>{css_code}</style>"
    st.markdown(css_code, unsafe_allow_html=True)


def apply_html(html_code):
    """
    应用HTML代码（通用方法）

    参数：
        html_code: HTML代码字符串

    使用方法：
        from Library import apply_html
        apply_html("<div class='custom'>内容</div>")
    """
    st.markdown(html_code, unsafe_allow_html=True)

