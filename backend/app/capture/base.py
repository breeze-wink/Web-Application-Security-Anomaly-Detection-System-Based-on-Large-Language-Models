"""HTTP请求捕获基类"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from app.core.models import HTTPRequest
from app.core.exceptions import CaptureException

class BaseCapturer(ABC):
    """HTTP请求捕获基类"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.is_running = False
    
    @abstractmethod
    async def capture_single(self) -> Optional[HTTPRequest]:
        """捕获单个HTTP请求"""
        pass
    
    @abstractmethod
    async def capture_stream(self) -> AsyncGenerator[HTTPRequest, None]:
        """捕获HTTP请求流"""
        pass
    
    @abstractmethod
    async def start_capture(self):
        """开始捕获"""
        pass
    
    @abstractmethod 
    async def stop_capture(self):
        """停止捕获"""
        pass
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start_capture()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop_capture() 