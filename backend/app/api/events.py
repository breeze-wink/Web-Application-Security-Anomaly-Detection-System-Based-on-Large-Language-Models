"""事件相关API接口"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.core.models import SecurityEvent, HTTPRequest
from app.detector import DetectionEngine  
from app.storage.base import BaseStorage

router = APIRouter(prefix="/events", tags=["events"])

class DetectRequest(BaseModel):
    """检测请求模型"""
    url: str
    method: str = "GET"
    headers: dict = {}
    params: dict = {}
    body: Optional[str] = None
    source_ip: str = "127.0.0.1"

class DetectResponse(BaseModel):
    """检测响应模型"""
    event_id: str
    is_attack: bool
    attack_types: List[str]
    confidence: float
    severity: Optional[str] = None
    recommendations: List[str] = []

class EventResponse(BaseModel):
    """事件响应模型"""
    event_id: str
    timestamp: datetime
    source_ip: str
    url: str
    method: str
    is_attack: bool
    attack_types: List[str]
    confidence: float
    severity: Optional[str] = None

class EventListResponse(BaseModel):
    """事件列表响应模型"""
    events: List[EventResponse]
    total: int
    page: int
    page_size: int

# 依赖注入
async def get_detection_engine() -> DetectionEngine:
    """获取检测引擎实例"""
    return DetectionEngine()

# 临时的内存存储实现，避免运行时错误
class MemoryStorage(BaseStorage):
    """临时的内存存储实现"""
    
    def __init__(self):
        self.events = {}
        self.event_counter = 0
    
    async def save_event(self, event: SecurityEvent) -> str:
        self.event_counter += 1
        event_id = f"event_{self.event_counter}"
        event.event_id = event_id
        self.events[event_id] = event
        return event_id
    
    async def get_event(self, event_id: str) -> Optional[SecurityEvent]:
        return self.events.get(event_id)
    
    async def query_events(self, **filters) -> List[SecurityEvent]:
        # 简化实现，返回所有事件
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 20)
        start = (page - 1) * page_size
        end = start + page_size
        
        all_events = list(self.events.values())
        return all_events[start:end]
    
    async def delete_event(self, event_id: str) -> bool:
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False
    
    async def update_event(self, event_id: str, event: SecurityEvent) -> bool:
        if event_id in self.events:
            self.events[event_id] = event
            return True
        return False
    
    async def count_events(self, **filters) -> int:
        return len(self.events)
    
    async def get_statistics(self, **filters) -> Dict[str, Any]:
        return {
            "total_events": len(self.events),
            "attack_events": 0,
            "attack_distribution": {},
            "trend_data": [],
            "top_attack_sources": []
        }

# 创建全局存储实例
_storage_instance = MemoryStorage()

async def get_storage() -> BaseStorage:
    """获取存储实例"""
    return _storage_instance

@router.post("/detect", response_model=DetectResponse)
async def detect_request(
    request: DetectRequest,
    detection_engine: DetectionEngine = Depends(get_detection_engine),
    storage: BaseStorage = Depends(get_storage)
):
    """检测HTTP请求"""
    try:
        # 构建HTTP请求对象
        http_request = HTTPRequest(
            url=request.url,
            method=request.method,
            headers=request.headers,
            params=request.params,
            body=request.body,
            source_ip=request.source_ip,
            timestamp=datetime.now(),
            raw_data=f"{request.method} {request.url}"
        )
        
        # 执行检测
        detection_result = detection_engine.detect_all(http_request)
        
        # 创建安全事件
        security_event = SecurityEvent(
            event_id="",  # 将由存储层生成
            request=http_request,
            detection=detection_result,
            llm_analysis=None,  # 暂不进行LLM分析
            created_at=datetime.now()
        )
        
        # 保存事件
        event_id = await storage.save_event(security_event)
        
        return DetectResponse(
            event_id=event_id,
            is_attack=detection_result.is_attack,
            attack_types=[t.value for t in detection_result.attack_types],
            confidence=detection_result.confidence,
            recommendations=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    storage: BaseStorage = Depends(get_storage)
):
    """获取单个事件详情"""
    try:
        event = await storage.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件未找到")
        
        return EventResponse(
            event_id=event.event_id,
            timestamp=event.request.timestamp,
            source_ip=event.request.source_ip,
            url=event.request.url,
            method=event.request.method,
            is_attack=event.detection.is_attack,
            attack_types=[t.value for t in event.detection.attack_types],
            confidence=event.detection.confidence,
            severity=event.llm_analysis.severity.value if event.llm_analysis else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取事件失败: {str(e)}")

@router.get("", response_model=EventListResponse) 
async def query_events(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    is_attack: Optional[bool] = Query(None, description="是否为攻击"),
    attack_type: Optional[str] = Query(None, description="攻击类型"),
    source_ip: Optional[str] = Query(None, description="来源IP"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    storage: BaseStorage = Depends(get_storage)
):
    """查询事件列表"""
    try:
        # 构建过滤条件
        filters = {
            "page": page,
            "page_size": page_size
        }
        
        if is_attack is not None:
            filters["is_attack"] = is_attack
        if attack_type:
            filters["attack_type"] = attack_type
        if source_ip:
            filters["source_ip"] = source_ip
        if start_time:
            filters["start_time"] = start_time
        if end_time:
            filters["end_time"] = end_time
        
        # 查询事件
        events = await storage.query_events(**filters)
        total = await storage.count_events(**filters)
        
        # 转换响应格式
        event_responses = [
            EventResponse(
                event_id=event.event_id,
                timestamp=event.request.timestamp,
                source_ip=event.request.source_ip,
                url=event.request.url,
                method=event.request.method,
                is_attack=event.detection.is_attack,
                attack_types=[t.value for t in event.detection.attack_types],
                confidence=event.detection.confidence,
                severity=event.llm_analysis.severity.value if event.llm_analysis else None
            )
            for event in events
        ]
        
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询事件失败: {str(e)}")

@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    storage: BaseStorage = Depends(get_storage)
):
    """删除事件"""
    try:
        success = await storage.delete_event(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="事件未找到")
        
        return {"message": "事件删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除事件失败: {str(e)}") 