"""系统配置设置"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field

class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str = Field(default="sqlite:///security_events.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

class RedisSettings(BaseSettings):
    """Redis配置"""
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")

class LLMSettings(BaseSettings):
    """LLM配置"""
    provider: str = Field(default="openai", env="LLM_PROVIDER")
    api_key: str = Field(default="", env="OPENAI_API_KEY")
    model: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
    daily_limit: int = Field(default=1000, env="LLM_DAILY_LIMIT")
    enable_cache: bool = Field(default=True, env="LLM_ENABLE_CACHE")
    cache_ttl: int = Field(default=3600, env="LLM_CACHE_TTL")

class DetectionSettings(BaseSettings):
    """检测配置"""
    confidence_threshold: float = Field(default=0.8, env="DETECTION_CONFIDENCE_THRESHOLD")
    enable_sql_detection: bool = Field(default=True, env="ENABLE_SQL_DETECTION")
    enable_xss_detection: bool = Field(default=True, env="ENABLE_XSS_DETECTION")
    enable_cmd_detection: bool = Field(default=True, env="ENABLE_CMD_DETECTION")
    max_request_size: int = Field(default=1024*1024, env="MAX_REQUEST_SIZE")

class APISettings(BaseSettings):
    """API配置"""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="API_DEBUG")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    rate_limit: str = Field(default="100/minute", env="API_RATE_LIMIT")

class LoggingSettings(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_bytes: int = Field(default=10*1024*1024, env="LOG_MAX_BYTES")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

class Settings(BaseSettings):
    """主配置类"""
    
    # 环境配置
    environment: str = Field(default="development", env="ENVIRONMENT")
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    # 各模块配置
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    llm: LLMSettings = LLMSettings()
    detection: DetectionSettings = DetectionSettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    
    # 数据清理配置
    data_retention_days: int = Field(default=90, env="DATA_RETENTION_DAYS")
    cleanup_schedule: str = Field(default="0 2 * * *", env="CLEANUP_SCHEDULE")  # 每天凌晨2点
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
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