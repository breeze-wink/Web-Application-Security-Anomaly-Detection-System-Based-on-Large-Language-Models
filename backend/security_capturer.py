"""
安全采集器 - 集成日志采集和攻击检测
将LogFileCapturer和DetectionEngine结合，提供完整的安全监控功能
"""

import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from app.capture.log_capturer import LogFileCapturer
from app.detector import DetectionEngine
from app.core.models import HTTPRequest, DetectionResult
from app.core.exceptions import CaptureException, DetectionException

@dataclass
class SecurityEvent:
    """安全事件数据结构"""
    request: HTTPRequest
    detection_result: DetectionResult
    timestamp: datetime
    event_id: str
    risk_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'risk_level': self.risk_level,
            'request': {
                'url': self.request.url,
                'method': self.request.method,
                'source_ip': self.request.source_ip,
                'user_agent': self.request.user_agent,
                'params': self.request.params,
                'body': self.request.body
            },
            'detection': {
                'is_attack': self.detection_result.is_attack,
                'attack_types': [t.value for t in self.detection_result.attack_types],
                'confidence': self.detection_result.confidence,
                'payload': self.detection_result.payload,
                'matched_rules': self.detection_result.matched_rules
            }
        }

class SecurityCapturer:
    """
    安全采集器 - 日志采集 + 攻击检测的完整解决方案
    
    功能：
    1. 从日志文件采集HTTP请求
    2. 使用Coraza WAF检测攻击
    3. 生成安全事件
    4. 支持实时监控和批量分析
    """
    
    def __init__(self, log_file_path: str, follow: bool = False):
        """
        初始化安全采集器
        
        Args:
            log_file_path: 日志文件路径
            follow: 是否实时跟踪日志文件
        """
        self.log_capturer = LogFileCapturer(log_file_path, follow)
        self.detection_engine = DetectionEngine()
        self.event_counter = 0
        self.stats = {
            'total_requests': 0,
            'attack_requests': 0,
            'normal_requests': 0,
            'processing_errors': 0,
            'start_time': None,
            'last_event_time': None
        }
    
    async def capture_and_analyze_single(self) -> Optional[SecurityEvent]:
        """
        采集并分析单个请求
        
        Returns:
            SecurityEvent: 安全事件对象，如果没有数据则返回None
        """
        try:
            # 1. 采集HTTP请求
            request = await self.log_capturer.capture_single()
            if not request:
                return None
            
            # 2. 安全检测
            detection_result = self.detection_engine.detect_all(request)
            
            # 3. 生成安全事件
            event = self._create_security_event(request, detection_result)
            
            # 4. 更新统计信息
            self._update_stats(event)
            
            return event
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            raise CaptureException(f"安全采集失败: {e}")
    
    async def capture_and_analyze_stream(self) -> AsyncGenerator[SecurityEvent, None]:
        """
        持续采集并分析请求流
        
        Yields:
            SecurityEvent: 安全事件对象
        """
        try:
            # 启动采集
            await self.log_capturer.start_capture()
            self.stats['start_time'] = datetime.now()
            
            # 持续处理请求流
            async for request in self.log_capturer.capture_stream():
                try:
                    # 安全检测
                    detection_result = self.detection_engine.detect_all(request)
                    
                    # 生成安全事件
                    event = self._create_security_event(request, detection_result)
                    
                    # 更新统计信息
                    self._update_stats(event)
                    
                    yield event
                    
                except DetectionException as e:
                    # 检测失败，记录错误但继续处理
                    self.stats['processing_errors'] += 1
                    print(f"检测失败: {e}")
                    continue
                    
        except Exception as e:
            raise CaptureException(f"安全采集流失败: {e}")
    
    async def analyze_attack_only_stream(self) -> AsyncGenerator[SecurityEvent, None]:
        """
        只返回攻击事件的流（过滤正常请求）
        
        Yields:
            SecurityEvent: 攻击事件对象
        """
        async for event in self.capture_and_analyze_stream():
            if event.detection_result.is_attack:
                yield event
    
    async def batch_analyze_log(self, max_requests: int = None) -> Dict[str, Any]:
        """
        批量分析日志文件
        
        Args:
            max_requests: 最大处理请求数，None表示处理全部
            
        Returns:
            分析报告字典
        """
        events = []
        attacks = []
        processed_count = 0
        
        try:
            async for event in self.capture_and_analyze_stream():
                events.append(event)
                if event.detection_result.is_attack:
                    attacks.append(event)
                
                processed_count += 1
                if max_requests and processed_count >= max_requests:
                    break
            
            # 生成分析报告
            report = self._generate_analysis_report(events, attacks)
            return report
            
        except Exception as e:
            raise CaptureException(f"批量分析失败: {e}")
    
    def _create_security_event(self, request: HTTPRequest, detection_result: DetectionResult) -> SecurityEvent:
        """创建安全事件"""
        self.event_counter += 1
        
        # 确定风险级别
        risk_level = self._determine_risk_level(detection_result)
        
        # 生成事件ID
        event_id = f"SEC-{datetime.now().strftime('%Y%m%d')}-{self.event_counter:06d}"
        
        return SecurityEvent(
            request=request,
            detection_result=detection_result,
            timestamp=datetime.now(),
            event_id=event_id,
            risk_level=risk_level
        )
    
    def _determine_risk_level(self, detection_result: DetectionResult) -> str:
        """确定风险级别"""
        if not detection_result.is_attack:
            return "SAFE"
        
        if detection_result.confidence >= 0.9:
            return "HIGH"
        elif detection_result.confidence >= 0.7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _update_stats(self, event: SecurityEvent):
        """更新统计信息"""
        self.stats['total_requests'] += 1
        self.stats['last_event_time'] = event.timestamp
        
        if event.detection_result.is_attack:
            self.stats['attack_requests'] += 1
        else:
            self.stats['normal_requests'] += 1
    
    def _generate_analysis_report(self, events: list, attacks: list) -> Dict[str, Any]:
        """生成分析报告"""
        if not events:
            return {
                'summary': '没有处理任何请求',
                'total_events': 0,
                'attack_events': 0,
                'attack_rate': 0.0,
                'top_attack_types': [],
                'top_attack_ips': [],
                'risk_distribution': {}
            }
        
        # 攻击类型统计
        attack_types = {}
        attack_ips = {}
        risk_distribution = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'SAFE': 0}
        
        for event in events:
            # 风险级别分布
            risk_distribution[event.risk_level] += 1
            
            if event.detection_result.is_attack:
                # 攻击类型统计
                for attack_type in event.detection_result.attack_types:
                    attack_types[attack_type.value] = attack_types.get(attack_type.value, 0) + 1
                
                # 攻击IP统计
                ip = event.request.source_ip
                attack_ips[ip] = attack_ips.get(ip, 0) + 1
        
        # 排序统计
        top_attack_types = sorted(attack_types.items(), key=lambda x: x[1], reverse=True)[:10]
        top_attack_ips = sorted(attack_ips.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'summary': f'分析了{len(events)}个请求，发现{len(attacks)}个攻击',
            'total_events': len(events),
            'attack_events': len(attacks),
            'attack_rate': len(attacks) / len(events) * 100,
            'top_attack_types': top_attack_types,
            'top_attack_ips': top_attack_ips,
            'risk_distribution': risk_distribution,
            'processing_stats': self.stats
        }
    
    async def start_monitoring(self):
        """启动监控模式"""
        await self.log_capturer.start_capture()
        self.stats['start_time'] = datetime.now()
        print(f"🚀 安全监控已启动，监控文件: {self.log_capturer.log_file_path}")
    
    async def stop_monitoring(self):
        """停止监控模式"""
        await self.log_capturer.stop_capture()
        print("🛑 安全监控已停止")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        stats = self.stats.copy()
        if stats['start_time']:
            runtime = datetime.now() - stats['start_time']
            stats['runtime_seconds'] = runtime.total_seconds()
            
            if stats['total_requests'] > 0:
                stats['requests_per_second'] = stats['total_requests'] / stats['runtime_seconds']
                stats['attack_rate'] = (stats['attack_requests'] / stats['total_requests']) * 100
        
        return stats
    
    def get_detector_info(self) -> Dict[str, Any]:
        """获取检测器信息"""
        return self.detection_engine.get_detector_info() 