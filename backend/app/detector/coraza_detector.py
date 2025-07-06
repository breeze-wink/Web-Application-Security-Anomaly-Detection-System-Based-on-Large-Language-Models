"""
Coraza WAF 检测器
基于OWASP Core Rule Set的高级Web应用防火墙检测器
"""

import re
import html
import urllib.parse
import base64
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .base import BaseDetector
from app.core.models import HTTPRequest, DetectionResult, AttackType
from app.core.exceptions import DetectionException

@dataclass
class RuleMatch:
    """规则匹配结果"""
    rule_id: str
    rule_msg: str
    matched_data: str
    severity: str
    confidence: float

class CorazaDetector(BaseDetector):
    """
    Coraza WAF检测器
    实现企业级WAF检测能力，覆盖OWASP Top 10攻击类型
    """
    
    def __init__(self):
        super().__init__()
        self.name = "CorazaDetector"
        self.version = "1.0.0"
        
        # 初始化规则集
        self._init_sql_injection_rules()
        self._init_xss_rules()
        self._init_command_injection_rules()
        self._init_path_traversal_rules()
        self._init_protocol_rules()
        self._init_scanner_rules()
        
    def detect(self, request: HTTPRequest) -> DetectionResult:
        """执行全面的安全检测"""
        try:
            matches = []
            attack_types = set()
            max_confidence = 0.0
            
            # 预处理请求数据
            processed_data = self._preprocess_request(request)
            
            # 执行各类检测
            detectors = [
                (self._detect_sql_injection, AttackType.SQL_INJECTION),
                (self._detect_xss, AttackType.XSS),
                (self._detect_command_injection, AttackType.COMMAND_INJECTION),
                (self._detect_path_traversal, AttackType.PATH_TRAVERSAL),
                (self._detect_protocol_violations, AttackType.UNKNOWN),
                (self._detect_scanner_activity, AttackType.UNKNOWN)
            ]
            
            for detector_func, attack_type in detectors:
                rule_matches = detector_func(processed_data)
                if rule_matches:
                    matches.extend(rule_matches)
                    attack_types.add(attack_type)
                    for match in rule_matches:
                        max_confidence = max(max_confidence, match.confidence)
            
            is_attack = len(matches) > 0
            
            return self._create_result(
                is_attack=is_attack,
                confidence=max_confidence,
                matched_rules=[match.rule_id for match in matches],
                payload=self._extract_payload(matches),
                details={
                    'detected_attacks': list(attack_types),
                    'rule_matches': [
                        {
                            'rule_id': match.rule_id,
                            'message': match.rule_msg,
                            'matched_data': match.matched_data,
                            'severity': match.severity,
                            'confidence': match.confidence
                        } for match in matches
                    ],
                    'processed_data_count': len(processed_data),
                    'detector': self.name,
                    'version': self.version
                }
            )
            
        except Exception as e:
            raise DetectionException(f"Coraza检测器执行失败: {e}")
    
    def _preprocess_request(self, request: HTTPRequest) -> List[str]:
        """预处理请求数据，处理编码和变换"""
        data_items = []
        
        # URL和查询参数
        data_items.append(request.url)
        for key, value in request.params.items():
            data_items.extend([key, value])
        
        # 请求头
        for key, value in request.headers.items():
            data_items.extend([key, value])
        
        # 请求体
        if request.body:
            data_items.append(request.body)
        
        # 对每个数据项进行多种解码尝试
        processed_items = []
        for item in data_items:
            if isinstance(item, str):
                processed_items.extend(self._decode_variations(item))
        
        return processed_items
    
    def _decode_variations(self, data: str) -> List[str]:
        """生成数据的各种解码变体"""
        variations = [data]  # 原始数据
        
        try:
            # URL解码
            url_decoded = urllib.parse.unquote(data)
            if url_decoded != data:
                variations.append(url_decoded)
                # 双重URL解码
                double_decoded = urllib.parse.unquote(url_decoded)
                if double_decoded != url_decoded:
                    variations.append(double_decoded)
        except:
            pass
        
        try:
            # HTML解码
            html_decoded = html.unescape(data)
            if html_decoded != data:
                variations.append(html_decoded)
        except:
            pass
        
        try:
            # Base64解码尝试
            if len(data) > 4 and data.replace('+', '').replace('/', '').replace('=', '').isalnum():
                try:
                    base64_decoded = base64.b64decode(data + '===').decode('utf-8', errors='ignore')
                    if base64_decoded and base64_decoded != data:
                        variations.append(base64_decoded)
                except:
                    pass
        except:
            pass
        
        # 去除重复
        return list(set(variations))
    
    def _init_sql_injection_rules(self):
        """初始化SQL注入检测规则"""
        self.sql_rules = [
            # Union-based SQL注入
            {
                'id': 'CRS-942100',
                'pattern': r'(?i)\b(union\s+(?:all\s+)?select)\b',
                'msg': 'SQL Injection Attack Detected: Union-based injection',
                'severity': 'critical',
                'confidence': 0.9
            },
            # Boolean-based盲注
            {
                'id': 'CRS-942110', 
                'pattern': r'(?i)\b(and|or)\s+[\'"]*\d+[\'"]*\s*[=<>]+\s*[\'"]*\d+[\'"]*',
                'msg': 'SQL Injection Attack: Boolean-based blind injection',
                'severity': 'critical',
                'confidence': 0.85
            },
            # Time-based盲注
            {
                'id': 'CRS-942120',
                'pattern': r'(?i)\b(sleep|waitfor\s+delay|benchmark|pg_sleep)\s*\(',
                'msg': 'SQL Injection Attack: Time-based blind injection',
                'severity': 'critical', 
                'confidence': 0.9
            },
            # SQL函数注入
            {
                'id': 'CRS-942130',
                'pattern': r'(?i)\b(concat|substring|ascii|char|hex|unhex|md5|sha1|version|database|user|current_user)\s*\(',
                'msg': 'SQL Injection Attack: SQL function injection',
                'severity': 'high',
                'confidence': 0.8
            },
            # SQL注释绕过
            {
                'id': 'CRS-942140',
                'pattern': r'(?i)(\/\*[\s\S]*?\*\/|--[\s]*|#)',
                'msg': 'SQL Injection Attack: Comment-based evasion',
                'severity': 'medium',
                'confidence': 0.7
            },
            # 错误注入
            {
                'id': 'CRS-942150',
                'pattern': r'(?i)\b(extractvalue|updatexml|exp|floor|rand|group\s+by)\s*\(',
                'msg': 'SQL Injection Attack: Error-based injection',
                'severity': 'high',
                'confidence': 0.85
            },
            # SQL操作符
            {
                'id': 'CRS-942160',
                'pattern': r'(?i)\b(drop|delete|insert|update|create|alter|truncate|exec|execute)\s+',
                'msg': 'SQL Injection Attack: SQL DDL/DML injection',
                'severity': 'critical',
                'confidence': 0.95
            }
        ]
    
    def _init_xss_rules(self):
        """初始化XSS检测规则"""
        self.xss_rules = [
            # Script标签
            {
                'id': 'CRS-941100',
                'pattern': r'(?i)<\s*script[^>]*>',
                'msg': 'XSS Attack Detected: Script tag injection',
                'severity': 'high',
                'confidence': 0.9
            },
            # 事件处理器
            {
                'id': 'CRS-941110', 
                'pattern': r'(?i)\bon\w+\s*=',
                'msg': 'XSS Attack: Event handler injection',
                'severity': 'high',
                'confidence': 0.85
            },
            # JavaScript伪协议
            {
                'id': 'CRS-941120',
                'pattern': r'(?i)\bjavascript\s*:',
                'msg': 'XSS Attack: JavaScript pseudo-protocol',
                'severity': 'high',
                'confidence': 0.8
            },
            # 常见XSS函数
            {
                'id': 'CRS-941130',
                'pattern': r'(?i)\b(alert|prompt|confirm|eval|setTimeout|setInterval)\s*\(',
                'msg': 'XSS Attack: Dangerous JavaScript function',
                'severity': 'high',
                'confidence': 0.8
            },
            # HTML注入
            {
                'id': 'CRS-941140',
                'pattern': r'(?i)<\s*(iframe|object|embed|applet|meta|link|form|input)\b',
                'msg': 'XSS Attack: Dangerous HTML tag injection',
                'severity': 'medium',
                'confidence': 0.7
            },
            # Data URI
            {
                'id': 'CRS-941150',
                'pattern': r'(?i)\bdata\s*:\s*[^,]*,',
                'msg': 'XSS Attack: Data URI scheme',
                'severity': 'medium',
                'confidence': 0.6
            },
            # CSS表达式
            {
                'id': 'CRS-941160',
                'pattern': r'(?i)\bexpression\s*\(',
                'msg': 'XSS Attack: CSS expression injection',
                'severity': 'medium',
                'confidence': 0.75
            }
        ]
    
    def _init_command_injection_rules(self):
        """初始化命令注入检测规则"""
        self.cmd_rules = [
            # Unix命令
            {
                'id': 'CRS-932100',
                'pattern': r'(?i)\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|mount)\b',
                'msg': 'Command Injection: Unix command detected',
                'severity': 'high',
                'confidence': 0.8
            },
            # Windows命令
            {
                'id': 'CRS-932110',
                'pattern': r'(?i)\b(dir|type|copy|del|net|ipconfig|tasklist|systeminfo)\b',
                'msg': 'Command Injection: Windows command detected', 
                'severity': 'high',
                'confidence': 0.8
            },
            # 命令分隔符（更精确的匹配）
            {
                'id': 'CRS-932120',
                'pattern': r'[;&|`$(){}]\s*[a-zA-Z]',  # 分隔符后面跟字母才算命令
                'msg': 'Command Injection: Command separator detected',
                'severity': 'medium',
                'confidence': 0.6
            },
            # 反引号执行
            {
                'id': 'CRS-932130',
                'pattern': r'`[^`]*`',
                'msg': 'Command Injection: Backtick command execution',
                'severity': 'high',
                'confidence': 0.85
            }
        ]
    
    def _init_path_traversal_rules(self):
        """初始化路径遍历检测规则"""
        self.path_rules = [
            # 目录遍历
            {
                'id': 'CRS-930100',
                'pattern': r'\.\.[\\/]',
                'msg': 'Path Traversal Attack: Directory traversal attempt',
                'severity': 'high',
                'confidence': 0.9
            },
            # 绝对路径
            {
                'id': 'CRS-930110',
                'pattern': r'(?i)[c-z]:\\|\/etc\/|\/bin\/|\/usr\/|\/var\/|\/tmp\/',
                'msg': 'Path Traversal Attack: Absolute path access',
                'severity': 'medium',
                'confidence': 0.7
            },
            # 文件包含
            {
                'id': 'CRS-930120',
                'pattern': r'(?i)(file://|php://|expect://|zip://)',
                'msg': 'Path Traversal Attack: File inclusion attempt',
                'severity': 'high',
                'confidence': 0.85
            }
        ]
    
    def _init_protocol_rules(self):
        """初始化HTTP协议违规检测规则"""
        self.protocol_rules = [
            # 超长请求
            {
                'id': 'CRS-920100',
                'pattern': r'.{10000,}',  # 超过10KB的数据
                'msg': 'Protocol Violation: Request too large',
                'severity': 'medium',
                'confidence': 0.5
            },
            # 异常字符（排除常见的编码字符）
            {
                'id': 'CRS-920110',
                'pattern': r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]',  # 移除\xFF范围，减少误报
                'msg': 'Protocol Violation: Invalid characters detected',
                'severity': 'low',
                'confidence': 0.3  # 降低置信度
            }
        ]
    
    def _init_scanner_rules(self):
        """初始化扫描器检测规则"""
        self.scanner_rules = [
            # 常见扫描器特征
            {
                'id': 'CRS-913100',
                'pattern': r'(?i)(sqlmap|nmap|nikto|dirb|gobuster|wfuzz|burp|nessus)',
                'msg': 'Scanner Detection: Known security scanner',
                'severity': 'medium',
                'confidence': 0.8
            }
        ]
    
    def _detect_sql_injection(self, data_items: List[str]) -> List[RuleMatch]:
        """检测SQL注入攻击"""
        return self._apply_rules(data_items, self.sql_rules)
    
    def _detect_xss(self, data_items: List[str]) -> List[RuleMatch]:
        """检测XSS攻击"""
        return self._apply_rules(data_items, self.xss_rules)
    
    def _detect_command_injection(self, data_items: List[str]) -> List[RuleMatch]:
        """检测命令注入攻击"""
        return self._apply_rules(data_items, self.cmd_rules)
    
    def _detect_path_traversal(self, data_items: List[str]) -> List[RuleMatch]:
        """检测路径遍历攻击"""
        return self._apply_rules(data_items, self.path_rules)
    
    def _detect_protocol_violations(self, data_items: List[str]) -> List[RuleMatch]:
        """检测HTTP协议违规"""
        return self._apply_rules(data_items, self.protocol_rules)
    
    def _detect_scanner_activity(self, data_items: List[str]) -> List[RuleMatch]:
        """检测扫描器活动"""
        return self._apply_rules(data_items, self.scanner_rules)
    
    def _apply_rules(self, data_items: List[str], rules: List[Dict]) -> List[RuleMatch]:
        """应用规则集进行匹配"""
        matches = []
        
        for rule in rules:
            pattern = rule['pattern']
            for data_item in data_items:
                try:
                    match = re.search(pattern, data_item)
                    if match:
                        matches.append(RuleMatch(
                            rule_id=rule['id'],
                            rule_msg=rule['msg'],
                            matched_data=match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0),
                            severity=rule['severity'],
                            confidence=rule['confidence']
                        ))
                        break  # 一个规则匹配一次即可
                except re.error:
                    continue  # 忽略正则表达式错误
        
        return matches
    
    def _extract_payload(self, matches: List[RuleMatch]) -> Optional[str]:
        """提取攻击载荷"""
        if not matches:
            return None
        
        # 返回最高置信度匹配的数据
        best_match = max(matches, key=lambda x: x.confidence)
        return best_match.matched_data
    
    def _create_result(
        self, 
        is_attack: bool, 
        confidence: float,
        matched_rules: List[str] = None,
        payload: str = None,
        details: Dict[str, Any] = None
    ) -> DetectionResult:
        """创建检测结果"""
        attack_types = []
        if is_attack and details:
            attack_types = details.get('detected_attacks', [])
        
        return DetectionResult(
            is_attack=is_attack,
            attack_types=attack_types,
            confidence=confidence,
            details=details or {},
            payload=payload,
            matched_rules=matched_rules or []
        ) 