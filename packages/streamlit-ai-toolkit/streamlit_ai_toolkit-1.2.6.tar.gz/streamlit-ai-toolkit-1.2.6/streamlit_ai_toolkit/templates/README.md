# AI Toolkit - Streamlit Application Template

A comprehensive AI application framework built with Streamlit, featuring:
- 💬 **AI Chat**: Conversational AI with OpenAI-compatible APIs
- 📚 **Knowledge Base Q&A**: RAG (Retrieval Augmented Generation) with FAISS
- 🎨 **Multimodal AI**: Text-to-Image and Image-to-Text capabilities
- 🌐 **Web Search**: Internet search with AI-powered answers
- 🧠 **Deep Thinking**: Extended reasoning mode for complex problems

---

## 🚀 Quick Start

### 1. Initialize Project

```bash
# Install the toolkit
pip install streamlit-ai-toolkit

# Create a new project
mkdir my_ai_app
cd my_ai_app

# Initialize with templates
streamlit-ai-toolkit init
```

### 2. Configure API Keys

**Option A: Using config.py (Recommended)**

```bash
# Copy the example config
cp config.example.py config.py

# Edit config.py and add your API keys
# OPENAI_API_KEY = "your-api-key-here"
```

**Option B: Using environment variables**

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your-api-key-here

# Install python-dotenv
pip install python-dotenv
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install streamlit openai

# For Knowledge Base Q&A (RAG)
pip install sentence-transformers faiss-cpu numpy

# For Multimodal AI (optional, requires GPU for good performance)
pip install diffusers transformers torch pillow
```

### 4. Run the Application

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
my_ai_app/
├── app.py                  # Main application entry point
├── ai_chat.py             # AI Chat module
├── knowledge_base.py      # Knowledge Base Q&A module
├── multimodal.py          # Multimodal AI module
├── web_search.py          # Web Search module
├── deep_thinking.py       # Deep Thinking module
├── utils.py               # Configuration utilities
├── ui_config.py           # UI styling configuration
├── config.example.py      # Configuration template
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
├── sample_knowledge.json  # Example knowledge base
└── README.md             # This file
```

---

## 🔧 Configuration

### API Configuration

The toolkit supports any OpenAI-compatible API:

**OpenAI**:
```python
OPENAI_API_KEY = "sk-..."
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-3.5-turbo"
```

**Alibaba Qwen**:
```python
OPENAI_API_KEY = "sk-..."
OPENAI_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_MODEL = "qwen-plus"
```

**DeepSeek**:
```python
OPENAI_API_KEY = "sk-..."
OPENAI_API_BASE = "https://api.deepseek.com/v1"
OPENAI_MODEL = "deepseek-chat"
```

### Knowledge Base Configuration

1. **Prepare your knowledge base**:
   - Create a JSON file with your data (see `products.json` for format)
   - Each entry should have a "content" field

2. **Configure the path**:
   ```python
   KNOWLEDGE_BASE_PATH = "your_knowledge_base.json"
   ```

3. **The system will automatically**:
   - Build a FAISS vector index
   - Save the index for faster loading
   - Enable semantic search

---

## 📚 Module Overview

### 1. AI Chat (`ai_chat.py`)

**Features**:
- Streaming responses from LLM
- Conversation history management
- Customizable model parameters
- Support for any OpenAI-compatible API

**TODO - Customize**:
- Add system prompts
- Implement conversation memory limits
- Add export functionality
- Customize UI and styling

### 2. Knowledge Base Q&A (`knowledge_base.py`)

**Features**:
- Vector-based semantic search with FAISS
- RAG (Retrieval Augmented Generation)
- Two answer modes:
  - Retrieval Only: Show retrieved documents
  - LLM Enhanced: Generate answers using LLM

**TODO - Customize**:
- Add your own knowledge base
- Implement knowledge base management
- Add source citation
- Support multiple knowledge sources

### 3. Multimodal AI (`multimodal.py`)

**Features**:
- Text-to-Image generation (Stable Diffusion)
- Image-to-Text captioning (BLIP)
- Image upload and processing

**TODO - Implement**:
- Load and configure models
- Implement generation functions
- Add image editing features
- Support batch processing

**Note**: This module provides UI template only. Actual implementation requires:
- Installing large models (several GB)
- GPU for reasonable performance
- See code comments for implementation examples

### 4. Web Search (`web_search.py`)

**Features**:
- Internet search using APIs (Tavily, SerpAPI, Bing)
- AI-powered answer generation from results
- Source citation and link display
- Search history management

**TODO - Implement**:
- Configure search API provider
- Implement search result processing
- Add result filtering and ranking
- Customize UI and display format

**Supported Providers**:
- **Tavily**: Optimized for AI applications
- **SerpAPI**: Google Search results
- **Bing Search API**: Microsoft Bing results

### 5. Deep Thinking (`deep_thinking.py`)

**Features**:
- Extended reasoning mode for complex questions
- Visible thinking process (like Claude's thinking)
- Step-by-step problem solving
- Reasoning chain visualization

**TODO - Implement**:
- Configure thinking model
- Implement thinking process extraction
- Add reasoning visualization
- Customize thinking depth

**Recommended Models**:
- **DeepSeek R1**: Native reasoning model
- **Claude 3.5 Sonnet**: Extended thinking feature
- **GPT-4**: Chain-of-thought prompting

---

## 🎨 Customization Guide

### Change App Title and Icon

Edit `app.py`:
```python
st.set_page_config(
    page_title="Your App Name",
    page_icon="🚀",
    ...
)
```

### Add New Pages

1. Create a new file `your_feature.py`
2. Implement `render_page()` function
3. Add to navigation in `app.py`

### Customize Styling

Edit `ui_config.py` to change:
- Colors and gradients
- Fonts and typography
- Layout and spacing

### Add Authentication

```python
# In app.py, before page rendering
import streamlit_authenticator as stauth

# Add authentication logic
# See: https://github.com/mkhorasani/Streamlit-Authenticator
```

---

## 📦 Knowledge Base Format

Your knowledge base should be a JSON file with this structure:

```json
[
    {
        "content": "Your knowledge content here...",
        "metadata": {
            "source": "optional",
            "category": "optional"
        }
    },
    {
        "content": "Another piece of knowledge...",
        "metadata": {}
    }
]
```

**Example** (`sample_knowledge.json`):
```json
[
    {
        "content": "Product A is a high-quality widget designed for...",
        "metadata": {
            "category": "products",
            "id": "prod_001"
        }
    }
]
```

---

## 🔒 Security Best Practices

1. **Never commit API keys**:
   - Add `config.py` and `.env` to `.gitignore`
   - Use environment variables in production

2. **Use secrets management**:
   - Streamlit Cloud: Use Secrets management
   - Docker: Use environment variables
   - Production: Use vault services (AWS Secrets Manager, etc.)

3. **Validate user input**:
   - Sanitize file uploads
   - Limit input length
   - Implement rate limiting

---

## 🚀 Deployment

### Streamlit Cloud

1. Push your code to GitHub (without `config.py` or `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Settings → Secrets

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Other Platforms

- **Heroku**: Use Procfile
- **AWS/GCP/Azure**: Use container services
- **VPS**: Use systemd or supervisor

---

## 📝 Requirements

Create `requirements.txt`:

```
streamlit>=1.28.0
openai>=1.0.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
numpy>=1.24.0

# Optional: For multimodal features
# diffusers>=0.21.0
# transformers>=4.30.0
# torch>=2.0.0
# pillow>=9.0.0
```

---

## 🤝 Contributing

This is a template project. Feel free to:
- Customize for your needs
- Add new features
- Share improvements

---

## 📄 License

MIT License - Feel free to use this template for any purpose.

---

## 🆘 Troubleshooting

### "API key not configured"
- Make sure you've created `config.py` from `config.example.py`
- Or set `OPENAI_API_KEY` environment variable

### "Knowledge base file not found"
- Create `sample_knowledge.json` or update `KNOWLEDGE_BASE_PATH` in config
- See example format above

### "Model download failed"
- Check internet connection
- Ensure sufficient disk space
- For China users: May need to configure HuggingFace mirror

### "Out of memory"
- Multimodal models require significant RAM/VRAM
- Use smaller models or reduce batch size
- Consider using cloud GPU services

---

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Hugging Face Models](https://huggingface.co/models)

---

**Built with ❤️ using Streamlit AI Toolkit**

