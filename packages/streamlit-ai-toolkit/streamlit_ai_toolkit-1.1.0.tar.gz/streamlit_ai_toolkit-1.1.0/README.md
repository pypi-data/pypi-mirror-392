# Streamlit AI Toolkit

[![PyPI version](https://badge.fury.io/py/streamlit-ai-toolkit.svg)](https://badge.fury.io/py/streamlit-ai-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📦 简介

Streamlit AI Toolkit 是一个功能强大的AI工具包，专为Streamlit应用设计。它提供了开箱即用的RAG（检索增强生成）知识库问答和多模态AI功能（文生图、图生文），让你能够快速构建智能AI应用。

**核心特性：**
- 🔍 **RAG知识库问答** - 基于FAISS向量检索的语义搜索
- 🎨 **文本生成图片** - 使用Stable Diffusion v1.5
- 📝 **图片生成文本** - 使用BLIP图像描述模型
- 🚀 **开箱即用** - 自动下载和管理AI模型
- 💻 **GPU加速** - 自动检测并使用CUDA加速
- 🎯 **Streamlit优化** - 专为Streamlit应用设计的API

## 🚀 快速安装

```bash
# 基础安装（使用CPU）
pip install streamlit-ai-toolkit

# GPU加速版本（推荐，需要CUDA）
pip install streamlit-ai-toolkit[gpu]

# 开发版本
pip install streamlit-ai-toolkit[dev]
```

## 📖 快速开始

### 1. RAG知识库问答

```python
import streamlit as st
from streamlit_ai_toolkit import RAGService

# 初始化RAG服务
if "rag" not in st.session_state:
    st.session_state.rag = RAGService(
        knowledge_file="knowledge.json",
        index_file="faiss.index"
    )

# 搜索知识库
query = st.text_input("请输入问题：")
if query:
    results = st.session_state.rag.search(query, top_k=3)
    for result in results:
        st.write(result)
```

### 2. 文本生成图片

```python
import streamlit as st
from streamlit_ai_toolkit import MultimodalService

# 初始化多模态服务
if "mm" not in st.session_state:
    st.session_state.mm = MultimodalService()

# 生成图片
prompt = st.text_input("描述你想要的图片：")
if st.button("生成"):
    image = st.session_state.mm.generate_image(
        prompt=prompt,
        num_inference_steps=50,
        guidance_scale=7.5
    )
    st.image(image)
```

### 3. 图片生成文本

```python
import streamlit as st
from streamlit_ai_toolkit import MultimodalService
from PIL import Image

# 初始化服务
if "mm" not in st.session_state:
    st.session_state.mm = MultimodalService()

# 上传图片并生成描述
uploaded_file = st.file_uploader("上传图片", type=["jpg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image)

    caption = st.session_state.mm.generate_caption(image)
    st.write(f"图片描述：{caption}")
```

### 4. UI工具

```python
import streamlit as st
from streamlit_ai_toolkit import apply_css

# 应用自定义CSS样式
gradient_css = """
<style>
.stApp {
    background: linear-gradient(-45deg, #FF6B6B, #4ECDC4);
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
apply_css(gradient_css)
```

## 📚 核心模块

### 1. RAGService - RAG知识库服务

提供基于向量检索的知识库问答功能。

**功能特性：**
- ✅ 自动加载/下载 Sentence Transformer 模型
- ✅ 构建和管理 FAISS 向量索引
- ✅ 语义搜索功能
- ✅ 支持本地模型缓存

**使用示例：**

```python
from Library import RAGService

# 初始化服务
rag = RAGService(
    knowledge_file="products.json",
    index_file="my_faiss_index.index"
)

# 搜索相关知识
results = rag.search("咖啡机怎么清洁？", top_k=3)
for result in results:
    print(result)
```

**API文档：**

- `__init__(knowledge_file, index_file)` - 初始化RAG服务
  - `knowledge_file`: 知识库JSON文件路径
  - `index_file`: FAISS索引文件路径

- `search(query, top_k=3)` - 语义搜索
  - `query`: 查询文本
  - `top_k`: 返回结果数量
  - 返回: 相关知识列表

### 2. MultimodalService - 多模态AI服务

提供文生图和图生文功能。

**功能特性：**
- ✅ 文本生成图片（Stable Diffusion v1.5）
- ✅ 图片生成文本（BLIP）
- ✅ 自动加载/下载模型
- ✅ GPU/CPU 自动检测
- ✅ 示例图片下载

**使用示例：**

```python
from Library import MultimodalService
from PIL import Image

# 初始化服务
mm = MultimodalService()

# 文生图
image = mm.generate_image(
    prompt="a beautiful sunset over the ocean",
    num_inference_steps=50,
    guidance_scale=7.5
)
image.save("output.png")

# 图生文
img = Image.open("photo.jpg")
caption = mm.generate_caption(img)
print(caption)

# 下载示例图片
mm.download_sample_images()
```

**API文档：**

- `__init__()` - 初始化多模态服务

- `generate_image(prompt, num_inference_steps=50, guidance_scale=7.5)` - 文本生成图片
  - `prompt`: 文本描述
  - `num_inference_steps`: 生成步数（20-100）
  - `guidance_scale`: 引导强度（1.0-20.0）
  - 返回: PIL Image对象

- `generate_caption(image)` - 图片生成文本
  - `image`: PIL Image对象
  - 返回: 图片描述文本

- `download_sample_images()` - 下载示例图片（静态方法）



## 🔧 配置说明

### 模型路径

模型会自动下载到以下目录：
- Sentence Transformer: `./models/paraphrase-multilingual-MiniLM-L12-v2`
- Stable Diffusion: `./models/stable-diffusion-v1-5`
- BLIP: `./models/blip-image-captioning-base`

### 模型大小

- Sentence Transformer: ~500MB
- Stable Diffusion v1.5: ~4GB
- BLIP: ~1GB

### GPU支持

库会自动检测CUDA是否可用：
- 有GPU：使用CUDA加速
- 无GPU：使用CPU（速度较慢）



## 🛠️ 高级用法

### 自定义知识库

```python
# 准备知识库JSON文件
knowledge = [
    {"content": "知识条目1"},
    {"content": "知识条目2"},
    # ...
]

import json
with open("my_knowledge.json", "w", encoding="utf-8") as f:
    json.dump(knowledge, f, ensure_ascii=False)

# 使用自定义知识库
rag = RAGService(
    knowledge_file="my_knowledge.json",
    index_file="my_index.index"
)
```

### 调整生成参数

```python
# 高质量图片生成（慢）
image = mm.generate_image(
    prompt="detailed portrait",
    num_inference_steps=100,  # 更多步数
    guidance_scale=12.0       # 更强引导
)

# 快速生成（质量较低）
image = mm.generate_image(
    prompt="simple sketch",
    num_inference_steps=20,   # 更少步数
    guidance_scale=5.0        # 较弱引导
)
```

## 📝 注意事项

1. **首次使用**：首次使用时会自动下载模型，需要较长时间和稳定网络
2. **内存需求**：建议至少8GB RAM，GPU推荐12GB显存
3. **模型缓存**：模型下载后会保存到本地，后续使用无需重新下载
4. **错误处理**：所有方法都包含异常处理，失败时会返回None

## 🔄 版本信息

- **当前版本**: 1.0.0
- **Python要求**: >= 3.8
- **主要依赖**:
  - streamlit
  - sentence-transformers
  - faiss-cpu / faiss-gpu
  - diffusers
  - transformers
  - torch
  - PIL

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

- 项目主页: [https://github.com/xiaozhou/streamlit-ai-toolkit](https://github.com/xiaozhou/streamlit-ai-toolkit)
- 问题反馈: [GitHub Issues](https://github.com/xiaozhou/streamlit-ai-toolkit/issues)

## 🙏 致谢

本项目使用了以下优秀的开源项目：
- [Streamlit](https://streamlit.io/) - Web应用框架
- [Sentence Transformers](https://www.sbert.net/) - 文本嵌入模型
- [FAISS](https://github.com/facebookresearch/faiss) - 向量检索引擎
- [Stable Diffusion](https://github.com/CompVis/stable-diffusion) - 文生图模型
- [BLIP](https://github.com/salesforce/BLIP) - 图生文模型

---

**Streamlit AI Toolkit** - 让AI应用开发更简单 🚀

