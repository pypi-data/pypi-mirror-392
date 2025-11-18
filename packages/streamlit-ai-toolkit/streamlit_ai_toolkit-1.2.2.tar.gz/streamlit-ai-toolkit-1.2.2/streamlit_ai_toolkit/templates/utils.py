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
