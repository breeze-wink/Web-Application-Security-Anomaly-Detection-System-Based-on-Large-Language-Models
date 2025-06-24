"""LLM分析基类"""

from abc import ABC, abstractmethod
from typing import Optional
from app.core.models import SecurityEvent, LLMAnalysis
from app.core.exceptions import LLMException

class BaseLLMProvider(ABC):
    """LLM服务提供者基类"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
    @abstractmethod
    async def analyze_security_event(self, event: SecurityEvent) -> LLMAnalysis:
        """分析安全事件"""
        pass
    
    @abstractmethod
    async def generate_summary(self, prompt: str) -> str:
        """生成文本摘要"""
        pass
        
    @abstractmethod
    async def check_availability(self) -> bool:
        """检查服务可用性"""
        pass

class LLMProviderFactory:
    """LLM提供者工厂"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """注册LLM提供者"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str, config: dict = None) -> BaseLLMProvider:
        """创建LLM提供者实例"""
        if name not in cls._providers:
            raise LLMException(f"未找到LLM提供者: {name}")
        
        return cls._providers[name](config) 