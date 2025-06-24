"""XSS攻击检测器"""

from typing import List
from .base import PatternDetector
from app.core.models import AttackType

class XSSDetector(PatternDetector):
    """XSS攻击检测器"""
    
    def __init__(self, custom_patterns: List[str] = None):
        # 常见XSS攻击模式
        default_patterns = [
            # Script tags
            r"<script.*?>",
            r"</script>",
            r"<script.*?/>",
            
            # JavaScript protocols
            r"javascript\s*:",
            r"vbscript\s*:",
            r"data\s*:",
            
            # Event handlers
            r"on\w+\s*=",
            r"onload\s*=",
            r"onclick\s*=", 
            r"onmouseover\s*=",
            r"onerror\s*=",
            
            # Common XSS vectors
            r"alert\s*\(",
            r"prompt\s*\(",
            r"confirm\s*\(",
            r"document\.cookie",
            r"document\.write",
            r"window\.location",
            
            # Iframe and object tags
            r"<iframe.*?>",
            r"<object.*?>",
            r"<embed.*?>",
            r"<applet.*?>",
            
            # Expression and CSS injection
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
            
            # HTML entities and encoding
            r"&#x?\d+;",
            r"%3c",  # <
            r"%3e",  # >
            r"%22",  # "
            r"%27",  # '
            
            # Common payload patterns
            r"<img.*?src.*?=.*?>",
            r"<svg.*?>",
            r"<video.*?>",
            r"<audio.*?>",
            
            # Advanced XSS patterns
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            r"Function\s*\(",
        ]
        
        patterns = custom_patterns or default_patterns
        super().__init__(patterns)
        self.attack_type = AttackType.XSS 