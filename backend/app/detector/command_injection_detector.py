"""命令注入检测器"""

from typing import List
from .base import PatternDetector
from app.core.models import AttackType

class CommandInjectionDetector(PatternDetector):
    """命令注入检测器"""
    
    def __init__(self, custom_patterns: List[str] = None):
        # 常见命令注入攻击模式
        default_patterns = [
            # 命令分隔符
            r";\s*(cat|ls|pwd|id|whoami|uname)",
            r"\|\s*(cat|ls|pwd|id|whoami|uname)",
            r"&&\s*(cat|ls|pwd|id|whoami|uname)",
            r"\|\|\s*(cat|ls|pwd|id|whoami|uname)",
            
            # 命令替换
            r"\$\([^)]*\)",
            r"`[^`]*`",
            
            # 网络命令
            r"\b(nc|netcat|telnet|ssh|ftp)\s+",
            r"\b(wget|curl|fetch)\s+",
            
            # 系统信息收集
            r"\b(ping|nslookup|dig|host)\s+",
            r"\b(ps|top|netstat|ss)\s+",
            
            # 文件操作
            r"\b(chmod|chown|chgrp)\s+",
            r"\b(rm|mv|cp|mkdir|rmdir)\s+",
            r"\b(find|locate|which|whereis)\s+",
            
            # 查看文件内容
            r"\b(cat|head|tail|more|less)\s+",
            r"\b(grep|awk|sed|sort|uniq)\s+",
            
            # 系统命令
            r"\b(su|sudo|passwd)\s+",
            r"\b(kill|killall|pkill)\s+",
            r"\b(mount|umount|df|du)\s+",
            
            # 编程语言执行
            r"\b(python|perl|php|ruby|node|java)\s+",
            r"\b(sh|bash|zsh|csh|tcsh)\s+",
            
            # Windows命令
            r"\b(cmd|powershell|wmic)\s+",
            r"\b(dir|type|copy|del|md|rd)\s+",
            r"\b(net|sc|reg|tasklist|taskkill)\s+",
        ]
        
        patterns = custom_patterns or default_patterns
        super().__init__(patterns)
        self.attack_type = AttackType.COMMAND_INJECTION 