"""
Knowledge Base Q&A Module - RAG (Retrieval Augmented Generation)

This module provides:
- Vector-based knowledge base search using FAISS
- Semantic search with sentence transformers
- Integration with LLM for intelligent answers

TODO: Customize this module for your needs:
1. Prepare your knowledge base in JSON format (see products.json for example)
2. Configure embedding model in utils.py or config.py
3. Adjust search parameters (top_k, similarity threshold)
4. Customize the answer generation prompt
5. Add knowledge base management features (add/update/delete)
"""

import streamlit as st
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import utils
from ui_config import GRADIENT_BACKGROUND_CSS


def apply_css(css_code):
    """Apply custom CSS styling"""
    st.markdown(css_code, unsafe_allow_html=True)


class RAGService:
    """
    RAG (Retrieval Augmented Generation) Service

    This class handles:
    - Loading and encoding knowledge base
    - Building FAISS vector index
    - Semantic search

    TODO: Extend this class with:
    - Dynamic knowledge base updates
    - Multiple knowledge sources
    - Hybrid search (vector + keyword)
    - Relevance scoring
    """

    def __init__(self, knowledge_file=None, index_file=None):
        """
        Initialize RAG Service

        Args:
            knowledge_file: Path to knowledge base JSON file
            index_file: Path to save/load FAISS index

        TODO: Customize initialization:
        - Add support for multiple knowledge sources
        - Implement lazy loading for large knowledge bases
        - Add caching mechanisms
        """
        # TODO: Get configuration from utils or config
        if knowledge_file is None:
            knowledge_file = utils.get_knowledge_base_path()
        if index_file is None:
            index_file = "knowledge_base.faiss"

        self.knowledge_file = knowledge_file
        self.index_file = index_file

        # Load embedding model
        # TODO: Make model configurable via utils.py or config.py
        model_path = "./models/paraphrase-multilingual-MiniLM-L12-v2"
        model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

        # Check if model exists locally
        model_exists = False
        if os.path.exists(model_path):
            config_exists = os.path.exists(os.path.join(model_path, "config.json"))
            has_weights = any(
                os.path.exists(os.path.join(model_path, f))
                for f in ["pytorch_model.bin", "model.safetensors", "tf_model.h5"]
            )
            if config_exists and has_weights:
                model_exists = True

        # Load model
        if model_exists:
            try:
                with st.spinner("Loading embedding model from local cache..."):
                    self.model = SentenceTransformer(model_path)
                st.success("✅ Embedding model loaded successfully!")
            except Exception as e:
                st.warning(f"⚠️ Failed to load local model: {e}")
                model_exists = False

        if not model_exists:
            st.warning("📥 Downloading embedding model from HuggingFace... (this may take a few minutes)")
            try:
                self.model = SentenceTransformer(model_id)
                # Save model locally for future use
                try:
                    os.makedirs(model_path, exist_ok=True)
                    self.model.save(model_path)
                    st.success(f"✅ Model downloaded and saved to: {model_path}")
                except Exception as save_error:
                    st.warning(f"⚠️ Failed to save model: {save_error}, but can continue")
            except Exception as download_error:
                st.error(f"❌ Failed to download model: {download_error}")
                raise

        # Load knowledge base
        # TODO: Add support for different file formats (CSV, Excel, Database)
        if not os.path.exists(self.knowledge_file):
            st.error(f"❌ Knowledge base file not found: {self.knowledge_file}")
            st.info("💡 Please create a knowledge base file. See products.json for example format.")
            self.documents = []
            self.index = None
            return

        try:
            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            st.success(f"✅ Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            st.error(f"❌ Failed to load knowledge base: {e}")
            self.documents = []
            self.index = None
            return

        # Load or build FAISS index
        if os.path.exists(self.index_file):
            try:
                self.index = faiss.read_index(self.index_file)
                st.success("✅ Loaded existing FAISS index")
            except Exception as e:
                st.warning(f"⚠️ Failed to load index: {e}, rebuilding...")
                self._build_knowledge_base()
        else:
            st.info("🔨 Building FAISS index for the first time...")
            self._build_knowledge_base()

    def _build_knowledge_base(self):
        """
        Build vector knowledge base using FAISS

        TODO: Optimize for large knowledge bases:
        - Use batch processing for large datasets
        - Implement incremental indexing
        - Add progress tracking
        - Support different FAISS index types (IVF, HNSW, etc.)
        """
        if not self.documents or not self.model:
            st.warning("⚠️ No documents or model available")
            return

        try:
            # Extract content from documents
            contents = [doc["content"] for doc in self.documents]

            # Generate embeddings
            with st.spinner(f"Encoding {len(contents)} documents..."):
                embeddings = self.model.encode(contents, show_progress_bar=True)

            # Convert to numpy array
            embeddings = np.array(embeddings).astype("float32")
            d = embeddings.shape[1] if embeddings is not None and len(embeddings) > 0 else 0

            # Create FAISS index
            # TODO: Use more advanced index types for better performance
            # - IndexIVFFlat for large datasets
            # - IndexHNSWFlat for fast search
            self.index = faiss.IndexFlatL2(d)
            self.index.add(embeddings)

            # Save index to file
            faiss.write_index(self.index, self.index_file)
            st.success(f"✅ FAISS index built and saved to {self.index_file}")

        except Exception as e:
            st.error(f"❌ Failed to build knowledge base: {e}")
            self.index = None

    def search(self, query: str, top_k=3) -> list:
        """
        Semantic search using vector similarity

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            list: List of relevant document contents

        TODO: Enhance search functionality:
        - Add relevance scoring
        - Implement hybrid search (vector + keyword)
        - Add filtering by metadata
        - Support multi-query search
        """
        if self.index is None or not query or not self.model:
            return []

        try:
            # Encode query
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype("float32")

            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, top_k)

            # Collect results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if 0 <= idx < len(self.documents):
                    # TODO: Add relevance score threshold
                    # TODO: Include metadata in results
                    results.append({
                        "content": self.documents[idx]["content"],
                        "distance": float(distance),
                        "index": int(idx)
                    })

            return results

        except Exception as e:
            st.error(f"❌ Search failed: {e}")
            return []


def render_page():
    """
    Render the Knowledge Base Q&A page

    TODO: Customize this function:
    - Add knowledge base management UI
    - Implement answer generation with LLM
    - Add source citation
    - Support file upload for knowledge base
    """
    # Apply styling
    apply_css(GRADIENT_BACKGROUND_CSS)

    # Page header
    st.title("📚 Knowledge Base Q&A")
    st.markdown("*Ask questions and get answers from your knowledge base using RAG*")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ RAG Settings")

        # TODO: Add configuration options
        top_k = st.slider(
            "Number of Results",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of relevant documents to retrieve"
        )

        # TODO: Add answer mode selection
        answer_mode = st.radio(
            "Answer Mode",
            ["Retrieval Only", "LLM Enhanced"],
            help="Retrieval Only: Show retrieved documents\nLLM Enhanced: Generate answer using LLM"
        )

        st.markdown("---")

        # Knowledge base info
        st.subheader("📊 Knowledge Base")
        kb_path = utils.get_knowledge_base_path()
        if os.path.exists(kb_path):
            st.success(f"✅ Loaded: {kb_path}")
            # TODO: Show knowledge base statistics
        else:
            st.error(f"❌ Not found: {kb_path}")
            st.info("💡 Create a knowledge base file to get started")

        # TODO: Add knowledge base management buttons
        # if st.button("🔄 Rebuild Index"):
        #     rebuild_index()
        # if st.button("📤 Upload Knowledge Base"):
        #     upload_knowledge_base()

    # Initialize chat history
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []

    # Initialize RAG service
    if "rag_service" not in st.session_state:
        try:
            st.session_state.rag_service = RAGService()
        except Exception as e:
            st.error(f"❌ Failed to initialize RAG service: {e}")
            st.info("💡 Make sure your knowledge base file exists and is properly formatted")
            return

    rag_service = st.session_state.rag_service

    # Display chat history
    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    # TODO: Customize placeholder text
    if prompt := st.chat_input("Ask a question about your knowledge base..."):
        # Add user message
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve relevant documents
        with st.chat_message("assistant"):
            if not rag_service or not rag_service.index:
                st.error("❌ RAG service not available")
                return

            # Search knowledge base
            with st.spinner("Searching knowledge base..."):
                search_results = rag_service.search(prompt, top_k=top_k)

            if search_results:
                # Display retrieved documents
                st.markdown("### 📚 Retrieved Knowledge:")
                for i, result in enumerate(search_results, 1):
                    with st.expander(f"Result {i} (Distance: {result['distance']:.4f})"):
                        st.markdown(result["content"])

                # Generate answer based on mode
                if answer_mode == "LLM Enhanced":
                    # TODO: Implement LLM-based answer generation
                    st.markdown("---")
                    st.markdown("### 🤖 AI-Generated Answer:")

                    try:
                        # Prepare context from retrieved documents
                        context = "\n\n".join([f"{i}. {r['content']}" for i, r in enumerate(search_results, 1)])

                        # Create prompt for LLM
                        system_prompt = """You are a helpful assistant that answers questions based on the provided knowledge base.
Use ONLY the information from the retrieved documents to answer the question.
If the information is not in the documents, say so clearly."""

                        user_prompt = f"""Question: {prompt}

Retrieved Knowledge:
{context}

Please provide a clear and concise answer based on the above knowledge."""

                        # Call LLM
                        # TODO: Make sure API key is configured
                        client = OpenAI(
                            api_key=utils.get_api_key(),
                            base_url=utils.get_api_base()
                        )

                        response = client.chat.completions.create(
                            model=utils.get_model_name(),
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.3,  # Lower temperature for more factual answers
                            stream=True
                        )

                        # Display streaming response
                        response_placeholder = st.empty()
                        full_response = ""

                        for chunk in response:
                            if chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                response_placeholder.markdown(full_response + "▌")

                        response_placeholder.markdown(full_response)
                        assistant_response = full_response

                    except Exception as e:
                        st.error(f"❌ Failed to generate answer: {e}")
                        st.info("💡 Make sure your API key is configured in utils.py or config.py")
                        assistant_response = "Failed to generate answer. Showing retrieved documents only."
                else:
                    # Retrieval only mode
                    assistant_response = f"Found {len(search_results)} relevant documents (see above)"

            else:
                st.warning("⚠️ No relevant documents found in the knowledge base")
                assistant_response = "Sorry, I couldn't find any relevant information in the knowledge base."

            # Save assistant response
            st.session_state.rag_messages.append({
                "role": "assistant",
                "content": assistant_response
            })


# TODO: Add helper functions
# def rebuild_index():
#     """Rebuild FAISS index from knowledge base"""
#     pass

# def upload_knowledge_base():
#     """Upload new knowledge base file"""
#     pass

# def export_conversation():
#     """Export conversation history"""
#     pass


if __name__ == "__main__":
    render_page()
