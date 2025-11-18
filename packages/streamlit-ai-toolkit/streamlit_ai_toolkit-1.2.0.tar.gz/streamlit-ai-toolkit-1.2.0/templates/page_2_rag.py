import streamlit as st
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from ui_config import GRADIENT_BACKGROUND_CSS

def apply_css(css_code):

    st.markdown(css_code, unsafe_allow_html=True)

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

        # 加载已保存的FAISS索引
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            self._build_knowledge_base()

    def _build_knowledge_base(self):
        """构建向量知识库"""
        if not self.documents or not self.model:
            return

        contents = [doc["content"] for doc in self.documents]
        # 生成文本向量
        embeddings = self.model.encode(contents, show_progress_bar=True)
        # 转换数据格式
        embeddings = np.array(embeddings).astype("float32")
        d = embeddings.shape[1] if embeddings is not None and len(embeddings) > 0 else 0
        # 创建FAISS索引
        self.index = faiss.IndexFlatL2(d)
        self.index.add(embeddings)
        # 保存索引到文件
        faiss.write_index(self.index, self.index_file)

    def search(self, query: str, top_k=3) -> list:
        """向量语义搜索"""
        if self.index is None or not query or not self.model:
            return []

        # 将查询转换为向量
        query_embedding = self.model.encode([query])
        # 格式转换
        query_embedding = np.array(query_embedding).astype("float32")
        # 执行向量搜索
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in indices[0]:
            if 0 <= i < len(self.documents):
                results.append(self.documents[i]["content"])
        return results


def render_page():
    apply_css(GRADIENT_BACKGROUND_CSS)
    st.title("任务二：知识库问答 (RAG)")

    with st.sidebar:
        st.subheader("⚙️ RAG 配置")
        st.markdown("---")


    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []

    # 检查索引文件
    index_file = "my_faiss_index.index"
    if os.path.exists(index_file):
        st.success(f"✅ {index_file} 索引文件已存在")
    else:
        st.warning(f"⚠️ {index_file} 索引文件不存在，将自动构建")

    # 初始化RAG服务
    if "rag_service" not in st.session_state:
        st.session_state.rag_service = RAGService()
        
    rag_service = st.session_state.rag_service
    
    # 显示历史消息
    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("您想了解什么？"):
        # 记录用户消息
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 知识检索
        search_results = []
        if rag_service:
            search_results = rag_service.search(prompt, top_k=3)

        # 显示检索结果
        with st.chat_message("assistant"):
            if search_results:
                st.markdown("### 📚 检索到的相关知识：\n")
                for i, result in enumerate(search_results, 1):
                    st.markdown(f"**{i}.** {result}\n")
                
                assistant_response = f"根据知识库检索，找到以下相关信息：\n\n" + "\n\n".join([f"{i}. {r}" for i, r in enumerate(search_results, 1)])
            else:
                assistant_response = "抱歉，没有找到相关的知识信息。"
                st.warning(assistant_response)
            
            st.session_state.rag_messages.append({
                "role": "assistant", 
                "content": assistant_response
            })


if __name__ == "__main__":
    render_page()

