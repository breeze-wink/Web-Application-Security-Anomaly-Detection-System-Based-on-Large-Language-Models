"""检测引擎聚合器"""

from typing import List, Dict, Any
from .base import BaseDetector
from .sql_injection_detector import SQLInjectionDetector
from .xss_detector import XSSDetector
from .command_injection_detector import CommandInjectionDetector
from app.core.models import HTTPRequest, DetectionResult, AttackType
from app.core.exceptions import DetectionException

class DetectionEngine:
    """检测引擎聚合器"""
    
    def __init__(self, custom_detectors: List[BaseDetector] = None):
        if custom_detectors:
            self.detectors = custom_detectors
        else:
            # 默认检测器
            self.detectors = [
                SQLInjectionDetector(),
                XSSDetector(),
                CommandInjectionDetector(),
            ]
    
    def detect_all(self, request: HTTPRequest) -> DetectionResult:
        """运行所有检测器"""
        try:
            all_attack_types = []
            all_matched_rules = []
            max_confidence = 0.0
            is_attack = False
            combined_details = {}
            final_payload = None
            
            for detector in self.detectors:
                try:
                    result = detector.detect(request)
                    
                    if result.is_attack:
                        is_attack = True
                        all_attack_types.extend(result.attack_types)
                        all_matched_rules.extend(result.matched_rules)
                        max_confidence = max(max_confidence, result.confidence)
                        
                        if result.payload and not final_payload:
                            final_payload = result.payload
                    
                    # 合并详细信息
                    detector_name = detector.__class__.__name__
                    combined_details[detector_name] = result.details
                    
                except Exception as e:
                    # 单个检测器错误不影响其他检测器
                    detector_name = detector.__class__.__name__
                    combined_details[detector_name] = {"error": str(e)}
                    continue
            
            # 去重攻击类型
            unique_attack_types = list(set(all_attack_types))
            
            return DetectionResult(
                is_attack=is_attack,
                attack_types=unique_attack_types,
                confidence=max_confidence,
                details=combined_details,
                payload=final_payload,
                matched_rules=all_matched_rules
            )
            
        except Exception as e:
            raise DetectionException(f"检测引擎执行失败: {e}")
    
    def add_detector(self, detector: BaseDetector):
        """添加新的检测器"""
        self.detectors.append(detector)
    
    def remove_detector(self, detector_class: type):
        """移除指定类型的检测器"""
        self.detectors = [d for d in self.detectors if not isinstance(d, detector_class)]
    
    def get_detector_info(self) -> Dict[str, Any]:
        """获取所有检测器信息"""
        return {
            "total_detectors": len(self.detectors),
            "detector_types": [d.__class__.__name__ for d in self.detectors]
        } 