"""
Configuration file for AI Toolkit

TODO: Copy this file to config.py and fill in your actual values
DO NOT commit config.py to version control!

Usage:
1. Copy this file: cp config.example.py config.py
2. Fill in your API keys and settings in config.py
3. Add config.py to .gitignore
"""

# =============================================================================
# API Configuration
# =============================================================================

# TODO: Set your OpenAI-compatible API key
# Get your key from:
# - OpenAI: https://platform.openai.com/api-keys
# - Alibaba Qwen: https://dashscope.console.aliyun.com/apiKey
# - Other providers: Check their documentation
OPENAI_API_KEY = "your-api-key-here"

# TODO: Set your API base URL
# Examples:
# - OpenAI: "https://api.openai.com/v1"
# - Azure OpenAI: "https://your-resource.openai.azure.com"
# - Alibaba Qwen: "https://dashscope.aliyuncs.com/compatible-mode/v1"
# - DeepSeek: "https://api.deepseek.com/v1"
OPENAI_API_BASE = "https://api.openai.com/v1"

# TODO: Set your model name
# Examples:
# - OpenAI: "gpt-4", "gpt-3.5-turbo"
# - Alibaba Qwen: "qwen-plus", "qwen-turbo", "qwen-max"
# - DeepSeek: "deepseek-chat"
OPENAI_MODEL = "gpt-3.5-turbo"

# =============================================================================
# Knowledge Base Configuration
# =============================================================================

# TODO: Set path to your knowledge base file
# This should be a JSON file with your knowledge base data
# See sample_knowledge.json for example format
KNOWLEDGE_BASE_PATH = "sample_knowledge.json"

# TODO: Set path to save/load FAISS index
# The vector index will be saved here for faster loading
FAISS_INDEX_PATH = "knowledge_base.faiss"

# TODO: Set embedding model for RAG
# Examples:
# - "paraphrase-multilingual-MiniLM-L12-v2" (multilingual, 384 dim)
# - "all-MiniLM-L6-v2" (English, 384 dim)
# - "all-mpnet-base-v2" (English, 768 dim)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# =============================================================================
# Multimodal AI Configuration
# =============================================================================

# TODO: Set text-to-image model
# Examples:
# - "runwayml/stable-diffusion-v1-5"
# - "stabilityai/stable-diffusion-2-1"
# - "CompVis/stable-diffusion-v1-4"
TEXT_TO_IMAGE_MODEL = "runwayml/stable-diffusion-v1-5"

# TODO: Set image-to-text model
# Examples:
# - "Salesforce/blip-image-captioning-base"
# - "Salesforce/blip-image-captioning-large"
# - "nlpconnect/vit-gpt2-image-captioning"
IMAGE_TO_TEXT_MODEL = "Salesforce/blip-image-captioning-base"

# =============================================================================
# Application Configuration
# =============================================================================

# TODO: Customize your application settings
APP_TITLE = "AI Toolkit"
APP_ICON = "🤖"
APP_LAYOUT = "wide"

# TODO: Set maximum conversation history length
MAX_HISTORY_LENGTH = 10

# TODO: Set default temperature for LLM
DEFAULT_TEMPERATURE = 0.7

# TODO: Set default max tokens for LLM response
DEFAULT_MAX_TOKENS = 2000

# =============================================================================
# Advanced Configuration
# =============================================================================

# TODO: Enable/disable features
ENABLE_CHAT = True
ENABLE_RAG = True
ENABLE_MULTIMODAL = True

# TODO: Set logging level
# Options: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"

# TODO: Set cache directory for models
CACHE_DIR = "./models"

# TODO: Enable GPU acceleration (if available)
USE_GPU = True

