"""
Configuration utilities for AI Toolkit

TODO: Configure your API keys and settings here
You can use environment variables or a config file
"""

import os
from pathlib import Path

# TODO: Method 1 - Set your API key directly (NOT recommended for production)
# OPENAI_API_KEY = "your-api-key-here"

# TODO: Method 2 - Use environment variables (Recommended)
# Set in your terminal: export OPENAI_API_KEY="your-key"
# Or create a .env file and use python-dotenv

# TODO: Method 3 - Use a config file (Most flexible)
# Create a config.py file with your settings


def get_api_key():
    """
    Get OpenAI-compatible API key from environment or config

    TODO: Customize this function to load your API key
    Priority: Environment Variable > Config File > Hardcoded

    Returns:
        str: API key
    """
    # Try to get from environment variable first
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        return api_key

    # Try to load from config file
    try:
        import config
        if hasattr(config, 'OPENAI_API_KEY'):
            return config.OPENAI_API_KEY
    except ImportError:
        pass

    # Fallback to hardcoded (NOT recommended)
    # TODO: Replace with your actual API key or use environment variables
    return "your-api-key-here"


def get_api_base():
    """
    Get API base URL

    TODO: Customize for your API provider
    - OpenAI: https://api.openai.com/v1
    - Azure OpenAI: https://your-resource.openai.azure.com
    - Alibaba Qwen: https://dashscope.aliyuncs.com/compatible-mode/v1
    - Other providers: Check their documentation

    Returns:
        str: API base URL
    """
    # Try environment variable first
    api_base = os.getenv("OPENAI_API_BASE")

    if api_base:
        return api_base

    # Try config file
    try:
        import config
        if hasattr(config, 'OPENAI_API_BASE'):
            return config.OPENAI_API_BASE
    except ImportError:
        pass

    # Default to OpenAI
    # TODO: Change this to your API provider's base URL
    return "https://api.openai.com/v1"


def get_model_name():
    """
    Get model name to use

    TODO: Customize for your model
    - OpenAI: gpt-4, gpt-3.5-turbo
    - Alibaba Qwen: qwen-plus, qwen-turbo
    - Other providers: Check their model names

    Returns:
        str: Model name
    """
    model = os.getenv("OPENAI_MODEL")

    if model:
        return model

    try:
        import config
        if hasattr(config, 'OPENAI_MODEL'):
            return config.OPENAI_MODEL
    except ImportError:
        pass

    # TODO: Change to your preferred model
    return "gpt-3.5-turbo"


def get_knowledge_base_path():
    """
    Get path to knowledge base file

    TODO: Customize to point to your knowledge base

    Returns:
        str: Path to knowledge base JSON file
    """
    kb_path = os.getenv("KNOWLEDGE_BASE_PATH")

    if kb_path:
        return kb_path

    try:
        import config
        if hasattr(config, 'KNOWLEDGE_BASE_PATH'):
            return config.KNOWLEDGE_BASE_PATH
    except ImportError:
        pass

    # Default to sample_knowledge.json in current directory
    return "sample_knowledge.json"



def get_search_api_key():
    """
    Get search API key from environment or config

    Supports: Tavily, SerpAPI, Bing Search API

    Returns:
        str: Search API key

    TODO: Set your search API key in config.py or .env:
        SEARCH_API_KEY = "your-search-api-key"
    """
    # Try environment variable first
    api_key = os.getenv("SEARCH_API_KEY")
    if api_key:
        return api_key

    # Try config file
    try:
        import config
        if hasattr(config, 'SEARCH_API_KEY'):
            return config.SEARCH_API_KEY
    except ImportError:
        pass

    # Default placeholder
    return "your-search-api-key-here"


def get_search_provider():
    """
    Get search provider from environment or config

    Supported providers: tavily, serpapi, bing

    Returns:
        str: Search provider name

    TODO: Set your search provider in config.py or .env:
        SEARCH_PROVIDER = "tavily"
    """
    # Try environment variable first
    provider = os.getenv("SEARCH_PROVIDER")
    if provider:
        return provider

    # Try config file
    try:
        import config
        if hasattr(config, 'SEARCH_PROVIDER'):
            return config.SEARCH_PROVIDER
    except ImportError:
        pass

    # Default to tavily
    return "tavily"


def get_thinking_api_key():
    """
    Get API key for thinking/reasoning model

    Returns:
        str: Thinking model API key

    TODO: Set your thinking API key in config.py or .env:
        THINKING_API_KEY = "your-thinking-api-key"
    """
    # Try environment variable first
    api_key = os.getenv("THINKING_API_KEY")
    if api_key:
        return api_key

    # Try config file
    try:
        import config
        if hasattr(config, 'THINKING_API_KEY'):
            return config.THINKING_API_KEY
    except ImportError:
        pass

    # Fallback to main API key
    return get_api_key()


def get_thinking_api_base():
    """
    Get API base URL for thinking model

    Returns:
        str: Thinking model API base URL

    TODO: Set your thinking API base in config.py or .env:
        THINKING_API_BASE = "https://api.deepseek.com/v1"
    """
    # Try environment variable first
    api_base = os.getenv("THINKING_API_BASE")
    if api_base:
        return api_base

    # Try config file
    try:
        import config
        if hasattr(config, 'THINKING_API_BASE'):
            return config.THINKING_API_BASE
    except ImportError:
        pass

    # Fallback to main API base
    return get_api_base()


def get_thinking_model():
    """
    Get thinking/reasoning model name

    Returns:
        str: Thinking model name

    TODO: Set your thinking model in config.py or .env:
        THINKING_MODEL = "deepseek-reasoner"
    """
    # Try environment variable first
    model = os.getenv("THINKING_MODEL")
    if model:
        return model

    # Try config file
    try:
        import config
        if hasattr(config, 'THINKING_MODEL'):
            return config.THINKING_MODEL
    except ImportError:
        pass

    # Default to deepseek-reasoner
    return "deepseek-reasoner"

