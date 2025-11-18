"""
核心服务库
包含RAG知识库服务和多模态服务的核心实现
"""
import os
import json
import warnings
import numpy as np
import faiss
import torch
import streamlit as st
from sentence_transformers import SentenceTransformer
from diffusers import StableDiffusionPipeline
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests

# 抑制警告信息
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


# ==================== RAG 知识库服务 ====================
class RAGService:
    """RAG知识库服务类"""

    def __init__(self, knowledge_file="products.json", index_file="my_faiss_index.index"):
        """初始化RAG服务"""
        # 模型路径配置
        model_path = "./models/paraphrase-multilingual-MiniLM-L12-v2"
        model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

        # 检查本地模型是否存在且完整
        model_exists = False
        if os.path.exists(model_path):
            config_exists = os.path.exists(os.path.join(model_path, "config.json"))
            has_weights = any(
                os.path.exists(os.path.join(model_path, f))
                for f in ["pytorch_model.bin", "model.safetensors", "tf_model.h5"]
            )
            if config_exists and has_weights:
                model_exists = True

        # 加载模型
        if model_exists:
            try:
                st.info("正在加载本地模型...")
                self.model = SentenceTransformer(model_path)
                st.success("本地模型加载成功！")
            except Exception as e:
                st.warning(f"本地模型加载失败: {e}")
                model_exists = False

        if not model_exists:
            st.warning(f"正在从HuggingFace下载模型... (约500MB)")
            try:
                self.model = SentenceTransformer(model_id)
                try:
                    os.makedirs(model_path, exist_ok=True)
                    self.model.save(model_path)
                    st.success(f"模型已下载并保存到: {model_path}")
                except Exception as save_error:
                    st.warning(f"模型保存失败: {save_error}，但可以继续使用")
            except Exception as download_error:
                st.error(f"模型下载失败: {download_error}")
                raise

        # 设置文件路径
        self.index_file = index_file
        self.knowledge_file = knowledge_file

        # 加载知识文档
        with open(self.knowledge_file, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # 加载或构建索引
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            self._build_knowledge_base()

    def _build_knowledge_base(self):
        """构建向量知识库"""
        if not self.documents or not self.model:
            return

        contents = [doc["content"] for doc in self.documents]
        embeddings = self.model.encode(contents, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")
        d = embeddings.shape[1] if embeddings is not None and len(embeddings) > 0 else 0
        self.index = faiss.IndexFlatL2(d)
        self.index.add(embeddings)
        faiss.write_index(self.index, self.index_file)

    def search(self, query: str, top_k=3) -> list:
        """向量语义搜索"""
        if self.index is None or not query or not self.model:
            return []

        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i in indices[0]:
            if 0 <= i < len(self.documents):
                results.append(self.documents[i]["content"])
        return results


# ==================== 多模态服务 ====================
class MultimodalService:
    """多模态服务类：文生图和图生文"""

    def __init__(self):
        """初始化多模态服务"""
        self.text_to_image_pipe = None
        self.image_to_text_processor = None
        self.image_to_text_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_text_to_image_model(self):
        """加载文生图模型"""
        if self.text_to_image_pipe is None:
            model_path = "./models/stable-diffusion-v1-5"
            model_id = "runwayml/stable-diffusion-v1-5"

            # 检查模型是否存在且完整
            model_exists = False
            if os.path.exists(model_path) and os.path.exists(os.path.join(model_path, "model_index.json")):
                unet_path = os.path.join(model_path, "unet")
                if os.path.exists(unet_path):
                    model_exists = True

            try:
                if model_exists:
                    st.info("正在加载本地文生图模型...")
                    self.text_to_image_pipe = StableDiffusionPipeline.from_pretrained(
                        model_path,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        safety_checker=None
                    )
                    self.text_to_image_pipe = self.text_to_image_pipe.to(self.device)
                    st.success(f"文生图模型加载成功！使用设备: {self.device}")
                else:
                    st.warning(f"未找到本地模型，正在从HuggingFace下载 {model_id}...")
                    st.info("首次下载约4GB，请耐心等待...")
                    self.text_to_image_pipe = StableDiffusionPipeline.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        safety_checker=None
                    )
                    self.text_to_image_pipe = self.text_to_image_pipe.to(self.device)
                    try:
                        os.makedirs(model_path, exist_ok=True)
                        self.text_to_image_pipe.save_pretrained(model_path)
                        st.success(f"模型下载并保存到: {model_path}，使用设备: {self.device}")
                    except Exception as save_error:
                        st.warning(f"模型保存失败: {save_error}，但可以继续使用")
            except Exception as e:
                st.error(f"模型加载失败: {e}")
                st.info("请检查网络连接，稍后重试")
                return None
        return self.text_to_image_pipe

    def load_image_to_text_model(self):
        """加载图生文模型"""
        if self.image_to_text_processor is None or self.image_to_text_model is None:
            model_path = "./models/blip-image-captioning-base"
            model_id = "Salesforce/blip-image-captioning-base"

            # 检查模型是否存在且完整
            model_exists = False
            if os.path.exists(model_path) and os.path.exists(os.path.join(model_path, "config.json")):
                has_weights = any(
                    os.path.exists(os.path.join(model_path, f))
                    for f in ["pytorch_model.bin", "model.safetensors"]
                )
                if has_weights:
                    model_exists = True

            try:
                if model_exists:
                    st.info("正在加载本地图生文模型...")
                    self.image_to_text_processor = BlipProcessor.from_pretrained(model_path)
                    self.image_to_text_model = BlipForConditionalGeneration.from_pretrained(
                        model_path,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                    self.image_to_text_model = self.image_to_text_model.to(self.device)
                    st.success(f"图生文模型加载成功！使用设备: {self.device}")
                else:
                    st.warning(f"未找到本地模型，正在从HuggingFace下载 {model_id}...")
                    st.info("首次下载约1GB，请耐心等待...")
                    self.image_to_text_processor = BlipProcessor.from_pretrained(model_id)
                    self.image_to_text_model = BlipForConditionalGeneration.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                    self.image_to_text_model = self.image_to_text_model.to(self.device)
                    try:
                        os.makedirs(model_path, exist_ok=True)
                        self.image_to_text_processor.save_pretrained(model_path)
                        self.image_to_text_model.save_pretrained(model_path)
                        st.success(f"模型下载并保存到: {model_path}，使用设备: {self.device}")
                    except Exception as save_error:
                        st.warning(f"模型保存失败: {save_error}，但可以继续使用")
            except Exception as e:
                st.error(f"模型加载失败: {e}")
                st.info("请检查网络连接，稍后重试")
                return None, None
        return self.image_to_text_processor, self.image_to_text_model

    def generate_image(self, prompt, num_inference_steps=50, guidance_scale=7.5):
        """根据文本生成图片"""
        pipe = self.load_text_to_image_model()
        if pipe is None:
            return None

        with st.spinner("正在生成图片，请稍候..."):
            try:
                image = pipe(
                    prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale
                ).images[0]
                return image
            except Exception as e:
                st.error(f"生成图片时出错: {e}")
                return None

    def generate_caption(self, image):
        """根据图片生成文本描述"""
        processor, model = self.load_image_to_text_model()
        if processor is None or model is None:
            return None

        with st.spinner("正在分析图片，请稍候..."):
            try:
                inputs = processor(image, return_tensors="pt").to(self.device)
                out = model.generate(**inputs, max_length=50)
                caption = processor.decode(out[0], skip_special_tokens=True)
                return caption
            except Exception as e:
                st.error(f"分析图片时出错: {e}")
                return None

    @staticmethod
    def download_sample_images():
        """下载示例图片"""
        sample_dir = "./sample_images"
        os.makedirs(sample_dir, exist_ok=True)

        sample_images = {
            "cat.jpg": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=500",
            "dog.jpg": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=500",
            "landscape.jpg": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500",
        }

        for filename, url in sample_images.items():
            filepath = os.path.join(sample_dir, filename)
            if not os.path.exists(filepath):
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        st.success(f"下载示例图片: {filename}")
                except Exception as e:
                    st.warning(f"下载 {filename} 失败: {e}")

