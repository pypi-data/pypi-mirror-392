"""
Streamlit AI Toolkit - A comprehensive AI application framework

This package provides templates and utilities for building AI applications with Streamlit.
"""

__version__ = '1.2.6'

# Lazy imports to avoid dependency issues
__all__ = [
    'RAGService',
    'MultimodalService',
    'apply_css',
    'apply_html'
]


def __getattr__(name):
    """Lazy import to avoid loading heavy dependencies on package import"""
    if name == 'RAGService' or name == 'MultimodalService':
        from .ai_services import RAGService, MultimodalService
        return RAGService if name == 'RAGService' else MultimodalService
    elif name == 'apply_css' or name == 'apply_html':
        from .ui_components import apply_css, apply_html
        return apply_css if name == 'apply_css' else apply_html
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

