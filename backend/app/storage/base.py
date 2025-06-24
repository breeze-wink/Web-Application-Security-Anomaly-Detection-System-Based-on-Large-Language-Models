"""数据存储基类"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.core.models import SecurityEvent
from app.core.exceptions import StorageException

class BaseStorage(ABC):
    """存储服务基类"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    @abstractmethod
    async def save_event(self, event: SecurityEvent) -> str:
        """保存安全事件，返回事件ID"""
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[SecurityEvent]:
        """获取单个安全事件"""
        pass
    
    @abstractmethod  
    async def query_events(self, **filters) -> List[SecurityEvent]:
        """查询安全事件列表"""
        pass
    
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """删除安全事件"""
        pass
    
    @abstractmethod
    async def update_event(self, event_id: str, event: SecurityEvent) -> bool:
        """更新安全事件"""
        pass
    
    @abstractmethod
    async def count_events(self, **filters) -> int:
        """统计事件数量"""
        pass
    
    @abstractmethod
    async def get_statistics(self, **filters) -> Dict[str, Any]:
        """获取统计数据"""
        pass 