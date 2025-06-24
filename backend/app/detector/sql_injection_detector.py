"""SQL注入检测器"""

from typing import List
from .base import PatternDetector
from app.core.models import AttackType

class SQLInjectionDetector(PatternDetector):
    """SQL注入检测器"""
    
    def __init__(self, custom_patterns: List[str] = None):
        # 常见SQL注入攻击模式
        default_patterns = [
            # Union based SQL injection
            r"union\s+.*\s+select",
            r"union\s+select",
            
            # Boolean based SQL injection  
            r"or\s+1\s*=\s*1",
            r"and\s+1\s*=\s*1",
            r"or\s+[\"']*\d+[\"']*\s*=\s*[\"']*\d+[\"']*",
            r"and\s+[\"']*\d+[\"']*\s*=\s*[\"']*\d+[\"']*",
            
            # Error based SQL injection
            r"'.*or.*'.*=.*'",
            r'".*or.*".*=.*"',
            
            # Time based SQL injection
            r"sleep\s*\(",
            r"waitfor\s+delay",
            r"benchmark\s*\(",
            
            # Comment injection
            r"\/\*.*\*\/",
            r"--.*",
            r"#.*",
            
            # SQL functions
            r"concat\s*\(",
            r"substring\s*\(",
            r"ascii\s*\(",
            r"version\s*\(",
            r"database\s*\(",
            r"user\s*\(",
            
            # SQL keywords
            r"\bdrop\s+table\b",
            r"\bdrop\s+database\b",
            r"\binsert\s+into\b",
            r"\bdelete\s+from\b",
            r"\bupdate\s+.*\s+set\b",
            
            # Special characters patterns
            r"'\s*;\s*",
            r'"\s*;\s*',
            r"'\s*\|\|\s*",
            r'"\s*\|\|\s*',
        ]
        
        patterns = custom_patterns or default_patterns
        super().__init__(patterns)
        self.attack_type = AttackType.SQL_INJECTION 