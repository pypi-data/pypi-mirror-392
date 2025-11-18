"""
通用AI服务库
包含RAG知识库服务、多模态AI服务和通用UI工具
"""

from .ai_services import RAGService, MultimodalService
from .ui_components import apply_css, apply_html

__all__ = [
    'RAGService',
    'MultimodalService',
    'apply_css',
    'apply_html'
]
__version__ = '1.0.0'

