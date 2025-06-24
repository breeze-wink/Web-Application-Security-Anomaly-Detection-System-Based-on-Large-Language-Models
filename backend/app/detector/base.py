"""安全检测器基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.models import HTTPRequest, DetectionResult, AttackType
from app.core.exceptions import DetectionException

class BaseDetector(ABC):
    """检测器基类"""
    
    def __init__(self, rules: List[str] = None):
        self.rules = rules or []
        self.attack_type = AttackType.UNKNOWN
        
    @abstractmethod
    def detect(self, request: HTTPRequest) -> DetectionResult:
        """执行检测"""
        pass
    
    def _create_result(
        self, 
        is_attack: bool, 
        confidence: float, 
        matched_rules: List[str] = None,
        payload: str = None,
        details: Dict[str, Any] = None
    ) -> DetectionResult:
        """创建检测结果"""
        return DetectionResult(
            is_attack=is_attack,
            attack_types=[self.attack_type] if is_attack else [],
            confidence=confidence,
            details=details or {},
            payload=payload,
            matched_rules=matched_rules or []
        )

class PatternDetector(BaseDetector):
    """基于正则模式的检测器基类"""
    
    def __init__(self, patterns: List[str] = None):
        super().__init__()
        self.patterns = patterns or []
        
    def detect(self, request: HTTPRequest) -> DetectionResult:
        """基于正则模式检测"""
        import re
        
        # 构建待检测的文本
        text_to_check = self._build_check_text(request)
        
        matched_rules = []
        max_confidence = 0.0
        matched_payload = None
        
        for pattern in self.patterns:
            try:
                if re.search(pattern, text_to_check, re.IGNORECASE):
                    matched_rules.append(pattern)
                    # 简单的置信度计算：规则匹配数量
                    confidence = min(1.0, len(matched_rules) * 0.3)
                    max_confidence = max(max_confidence, confidence)
                    matched_payload = text_to_check
            except re.error:
                # 正则表达式错误，跳过该规则
                continue
        
        is_attack = len(matched_rules) > 0
        
        return self._create_result(
            is_attack=is_attack,
            confidence=max_confidence,
            matched_rules=matched_rules,
            payload=matched_payload if is_attack else None,
            details={
                'patterns_checked': len(self.patterns),
                'patterns_matched': len(matched_rules)
            }
        )
    
    def _build_check_text(self, request: HTTPRequest) -> str:
        """构建待检测的文本"""
        # 将URL、参数、请求体合并为待检测文本
        text_parts = [request.url]
        
        # 添加URL参数
        for key, value in request.params.items():
            text_parts.append(f"{key}={value}")
        
        # 添加请求体
        if request.body:
            text_parts.append(request.body)
            
        return " ".join(text_parts) 