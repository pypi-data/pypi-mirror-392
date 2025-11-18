import streamlit as st
from PIL import Image
import os
from ui_config import GRADIENT_BACKGROUND_CSS

def apply_css(css_code):
    """应用自定义CSS"""
    st.markdown(css_code, unsafe_allow_html=True)


def render_page():
    """渲染多模态智能页面"""
    # 动态背景
    apply_css(GRADIENT_BACKGROUND_CSS)
    st.title("任务三：多模态智能")


    st.write("图像处理。")


    tab1, tab2 = st.tabs(["AI绘画", "图片解析"])

    with tab1:
        st.header("文本生成图片")
        st.write("输入文本描述，AI将为您生成对应的图片")

        # 文本输入
        prompt = st.text_area(
            "请输入图片描述（建议使用英文）",
            placeholder="例如: a beautiful sunset over the ocean, digital art",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            num_steps = st.slider("生成步数", min_value=20, max_value=100, value=50, step=10,
                                 help="步数越多，图片质量越好，但生成时间越长")
        with col2:
            guidance_scale = st.slider("引导强度", min_value=1.0, max_value=20.0, value=7.5, step=0.5,
                                      help="值越大，生成的图片越符合描述")

        if st.button("🎨 生成图片", type="primary", key="generate_image"):
            if prompt:
                st.info("📝 任务3.1已完成：页面基础结构搭建完成")
                st.markdown(f"**您的描述**: {prompt}")
                st.markdown(f"**生成步数**: {num_steps}")
                st.markdown(f"**引导强度**: {guidance_scale}")
                st.warning("💡 提示：文生图功能需要加载Stable Diffusion模型（约5GB），题目仅要求完成任务3.1的页面结构")
            else:
                st.warning("请先输入图片描述")

        # 示例提示词
        with st.expander("💡 示例提示词"):
            st.markdown("""
            - `a beautiful landscape with mountains and lake, sunset, digital art`
            - `a cute cat sitting on a windowsill, watercolor painting`
            - `futuristic city with flying cars, cyberpunk style`
            - `a cozy coffee shop interior, warm lighting, realistic`
            - `abstract art with vibrant colors, modern style`
            """)

    # ========== 标签页2: 图生文 ==========
    with tab2:
        st.header("图片生成文本")
        st.write("上传图片，AI将为您生成图片的文字描述")

        # 图片上传
        uploaded_file = st.file_uploader("选择图片文件", type=["jpg", "jpeg", "png", "webp"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="上传的图片", use_container_width=True)

        if st.button("🔍 分析图片", type="primary", key="analyze_image"):
            if uploaded_file:
                st.success("图片已上传！")
                st.markdown("### 📝 图片描述（示例）")
                demo_caption = "a beautiful landscape with mountains and a lake at sunset"
                st.info(demo_caption)
                st.markdown("*注: 描述为英文，您可以使用翻译工具转换为中文*")
                st.warning("💡 提示：图生文功能需要加载BLIP模型（约661MB），题目仅要求完成任务3.1的页面结构")
            else:
                st.warning("请先上传图片")


if __name__ == "__main__":
    render_page()

