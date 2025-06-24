from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class AttackType(Enum):
    """攻击类型枚举"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    UNKNOWN = "unknown"

class Severity(Enum):
    """危险等级枚举"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

@dataclass
class HTTPRequest:
    """标准化的HTTP请求数据结构"""
    url: str
    method: str
    headers: Dict[str, str]
    params: Dict[str, str]
    body: Optional[str]
    source_ip: str
    timestamp: datetime
    raw_data: str
    user_agent: Optional[str] = None

@dataclass  
class DetectionResult:
    """检测结果数据结构"""
    is_attack: bool
    attack_types: List[AttackType]
    confidence: float        # 0.0-1.0
    details: Dict[str, Any]  # 详细检测信息
    payload: Optional[str]   # 攻击载荷
    matched_rules: List[str] # 匹配的规则

@dataclass
class LLMAnalysis:
    """LLM分析结果"""
    severity: Severity
    attack_intent: str      # 攻击意图描述
    potential_impact: str   # 可能影响
    recommendations: List[str]
    confidence: float
    analysis_time: datetime

@dataclass
class SecurityEvent:
    """完整的安全事件"""
    event_id: str
    request: HTTPRequest
    detection: DetectionResult
    llm_analysis: Optional[LLMAnalysis]
    created_at: datetime
    updated_at: Optional[datetime] = None 