"""系统配置设置"""

import os
import yaml
from typing import Optional, List
from pydantic import BaseSettings, Field
from pathlib import Path

def load_config_file(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    config_file = Path(config_path)
    
    # 如果配置文件不存在，使用默认配置
    if not config_file.exists():
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
            print(f"成功加载配置文件: {config_path}")
            return config_data
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}

# 全局配置数据
CONFIG_DATA = load_config_file()

class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str = Field(default="sqlite:///security_events.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    
    def __init__(self, **kwargs):
        # 从配置文件读取数据库配置
        db_config = CONFIG_DATA.get('database', {})
        super().__init__(**{**db_config, **kwargs})

class RedisSettings(BaseSettings):
    """Redis配置"""
    url: str = Field(default="redis://localhost:6379/0")
    password: Optional[str] = Field(default=None)
    max_connections: int = Field(default=50)
    
    def __init__(self, **kwargs):
        # 从配置文件读取Redis配置
        redis_config = CONFIG_DATA.get('redis', {})
        super().__init__(**{**redis_config, **kwargs})

class LLMSettings(BaseSettings):
    """LLM配置"""
    provider: str = Field(default="openai")
    api_key: str = Field(default="")
    model: str = Field(default="gpt-3.5-turbo")
    daily_limit: int = Field(default=1000)
    enable_cache: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)
    
    def __init__(self, **kwargs):
        # 从配置文件读取LLM配置
        llm_config = CONFIG_DATA.get('llm', {})
        super().__init__(**{**llm_config, **kwargs})

class DetectionSettings(BaseSettings):
    """检测配置"""
    confidence_threshold: float = Field(default=0.8)
    enable_sql_detection: bool = Field(default=True)
    enable_xss_detection: bool = Field(default=True)
    enable_cmd_detection: bool = Field(default=True)
    max_request_size: int = Field(default=1024*1024)
    
    def __init__(self, **kwargs):
        # 从配置文件读取检测配置
        detection_config = CONFIG_DATA.get('detection', {})
        super().__init__(**{**detection_config, **kwargs})

class APISettings(BaseSettings):
    """API配置"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    cors_origins: List[str] = Field(default=["*"])
    rate_limit: str = Field(default="100/minute")
    
    def __init__(self, **kwargs):
        # 从配置文件读取API配置
        api_config = CONFIG_DATA.get('api', {})
        super().__init__(**{**api_config, **kwargs})

class LoggingSettings(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: Optional[str] = Field(default=None)
    max_bytes: int = Field(default=10*1024*1024)
    backup_count: int = Field(default=5)
    
    def __init__(self, **kwargs):
        # 从配置文件读取日志配置
        logging_config = CONFIG_DATA.get('logging', {})
        super().__init__(**{**logging_config, **kwargs})

class Settings(BaseSettings):
    """主配置类"""
    
    # 环境配置
    environment: str = Field(default="development")
    secret_key: str = Field(default="your-secret-key-here")
    
    # 各模块配置
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    llm: LLMSettings = LLMSettings()
    detection: DetectionSettings = DetectionSettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    
    # 数据清理配置
    data_retention_days: int = Field(default=90)
    cleanup_schedule: str = Field(default="0 2 * * *")  # 每天凌晨2点
    
    def __init__(self, **kwargs):
        # 从配置文件读取主配置
        main_config = {
            'environment': CONFIG_DATA.get('environment', 'development'),
            'secret_key': CONFIG_DATA.get('secret_key', 'your-secret-key-here'),
            'data_retention_days': CONFIG_DATA.get('data_retention_days', 90),
            'cleanup_schedule': CONFIG_DATA.get('cleanup_schedule', '0 2 * * *'),
        }
        super().__init__(**{**main_config, **kwargs})
    
    class Config:
        case_sensitive = False

# 全局配置实例
settings = Settings()

# 检测规则配置
DETECTION_RULES = {
    "sql_injection": [
        r"union\s+.*\s+select",
        r"union\s+select", 
        r"or\s+1\s*=\s*1",
        r"and\s+1\s*=\s*1",
        r"'.*or.*'.*=.*'",
        r'".*or.*".*=.*"',
        r"sleep\s*\(",
        r"waitfor\s+delay",
        r"benchmark\s*\(",
        r"\/\*.*\*\/",
        r"--.*",
        r"#.*",
        r"concat\s*\(",
        r"substring\s*\(",
        r"ascii\s*\(",
        r"version\s*\(",
        r"database\s*\(",
        r"user\s*\(",
        r"\bdrop\s+table\b",
        r"\bdrop\s+database\b",
        r"\binsert\s+into\b",
        r"\bdelete\s+from\b",
        r"\bupdate\s+.*\s+set\b",
        r"'\s*;\s*",
        r'"\s*;\s*',
        r"'\s*\|\|\s*",
        r'"\s*\|\|\s*',
    ],
    "xss": [
        r"<script.*?>",
        r"</script>",
        r"<script.*?/>",
        r"javascript\s*:",
        r"vbscript\s*:",
        r"data\s*:",
        r"on\w+\s*=",
        r"onload\s*=",
        r"onclick\s*=", 
        r"onmouseover\s*=",
        r"onerror\s*=",
        r"alert\s*\(",
        r"prompt\s*\(",
        r"confirm\s*\(",
        r"document\.cookie",
        r"document\.write",
        r"window\.location",
        r"<iframe.*?>",
        r"<object.*?>",
        r"<embed.*?>",
        r"<applet.*?>",
        r"expression\s*\(",
        r"url\s*\(",
        r"@import",
        r"&#x?\d+;",
        r"%3c",  # <
        r"%3e",  # >
        r"%22",  # "
        r"%27",  # '
        r"<img.*?src.*?=.*?>",
        r"<svg.*?>",
        r"<video.*?>",
        r"<audio.*?>",
        r"eval\s*\(",
        r"setTimeout\s*\(",
        r"setInterval\s*\(",
        r"Function\s*\(",
    ],
    "command_injection": [
        r";\s*(cat|ls|pwd|id|whoami)",
        r"\|\s*(cat|ls|pwd|id|whoami)",
        r"&&\s*(cat|ls|pwd|id|whoami)", 
        r"\$\(.*\)",
        r"`.*`",
        r"nc\s+",
        r"netcat\s+",
        r"wget\s+",
        r"curl\s+",
        r"ping\s+",
        r"nslookup\s+",
        r"dig\s+",
        r"chmod\s+",
        r"chown\s+",
        r"rm\s+",
        r"mv\s+",
        r"cp\s+",
        r"mkdir\s+",
        r"rmdir\s+",
    ]
} 