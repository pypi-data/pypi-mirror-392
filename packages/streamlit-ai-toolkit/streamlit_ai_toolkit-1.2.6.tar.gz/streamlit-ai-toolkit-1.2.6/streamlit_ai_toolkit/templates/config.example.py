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


# ============================================================
# Web Search Configuration
# ============================================================

# TODO: Choose and configure your search provider
# Supported providers: "tavily", "serpapi", "bing"
SEARCH_PROVIDER = "tavily"

# TODO: Set your search API key
# Get API key from:
# - Tavily: https://tavily.com
# - SerpAPI: https://serpapi.com
# - Bing: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
SEARCH_API_KEY = "your-search-api-key-here"

# Search configuration
SEARCH_MAX_RESULTS = 5  # Maximum number of search results to retrieve
SEARCH_INCLUDE_ANSWER = True  # Whether to generate AI answer from results


# ============================================================
# Deep Thinking Configuration
# ============================================================

# TODO: Configure thinking/reasoning model
# Recommended models:
# - "deepseek-reasoner" (DeepSeek R1, best for reasoning)
# - "claude-3-5-sonnet-20241022" (Claude with thinking)
# - "gpt-4-turbo" or "gpt-4o" (with chain-of-thought prompting)
THINKING_MODEL = "deepseek-reasoner"

# TODO: Set API credentials for thinking model
# If using DeepSeek R1:
THINKING_API_KEY = "your-deepseek-api-key-here"
THINKING_API_BASE = "https://api.deepseek.com/v1"

# If using Claude:
# THINKING_API_KEY = "your-anthropic-api-key-here"
# THINKING_API_BASE = "https://api.anthropic.com/v1"

# If using OpenAI:
# THINKING_API_KEY = "your-openai-api-key-here"
# THINKING_API_BASE = "https://api.openai.com/v1"

# Thinking configuration
THINKING_MAX_TIME = 60  # Maximum thinking time in seconds
THINKING_TEMPERATURE = 0.7  # Temperature for thinking model
SHOW_THINKING_PROCESS = True  # Whether to show thinking process
STREAM_THINKING = True  # Whether to stream thinking in real-time

CACHE_DIR = "./models"

# TODO: Enable GPU acceleration (if available)
USE_GPU = True

