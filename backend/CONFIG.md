# 配置系统使用说明

## 概述

本系统已改为使用 YAML 配置文件进行配置管理，不再依赖环境变量。配置文件提供了更好的可读性和管理便利性。

## 配置文件结构

系统会自动寻找项目根目录下的 `config.yaml` 文件。如果文件不存在，系统将使用默认配置运行。

### 配置文件位置
```
backend/
├── config.yaml          # 主配置文件
├── app/
│   └── config/
│       └── settings.py  # 配置类定义
└── main.py
```

## 配置项说明

### 系统基础配置
```yaml
# 运行环境：development/production/testing
environment: development

# 系统密钥（生产环境必须修改）
secret_key: "your-secret-key-here-change-in-production"

# 数据保留天数
data_retention_days: 90

# 数据清理定时任务（cron格式）
cleanup_schedule: "0 2 * * *"
```

### 数据库配置
```yaml
database:
  url: "sqlite:///security_events.db"  # 数据库连接字符串
  echo: false                          # 是否打印SQL语句
  pool_size: 10                        # 连接池大小
  max_overflow: 20                     # 连接池溢出上限
```

支持的数据库类型：
- SQLite: `sqlite:///database.db`
- PostgreSQL: `postgresql://user:pass@host:port/dbname`
- MySQL: `mysql://user:pass@host:port/dbname`

### Redis配置
```yaml
redis:
  url: "redis://localhost:6379/0"  # Redis连接字符串
  password: null                   # Redis密码（可选）
  max_connections: 50              # 最大连接数
```

### 大语言模型配置
```yaml
llm:
  provider: "openai"        # LLM提供商
  api_key: ""              # API密钥
  model: "gpt-3.5-turbo"   # 使用的模型
  daily_limit: 1000        # 每日调用限制
  enable_cache: true       # 启用缓存
  cache_ttl: 3600         # 缓存过期时间（秒）
```

### 安全检测配置
```yaml
detection:
  confidence_threshold: 0.8    # 检测置信度阈值
  enable_sql_detection: true   # 启用SQL注入检测
  enable_xss_detection: true   # 启用XSS检测
  enable_cmd_detection: true   # 启用命令注入检测
  max_request_size: 1048576    # 最大请求大小（字节）
```

### API服务配置
```yaml
api:
  host: "0.0.0.0"          # 监听地址
  port: 8000               # 监听端口
  debug: false             # 调试模式
  cors_origins:            # 跨域请求允许的源
    - "*"
  rate_limit: "100/minute" # 限流配置
```

### 日志配置
```yaml
logging:
  level: "INFO"                                                      # 日志级别
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"   # 日志格式
  file_path: null                                                    # 日志文件路径
  max_bytes: 10485760                                               # 日志文件大小上限
  backup_count: 5                                                   # 备份文件数量
```

## 使用方法

### 1. 创建配置文件
复制 `config.yaml` 示例文件到项目根目录，并根据需要修改配置项。

### 2. 在代码中使用
```python
from app.config.settings import settings

# 访问配置
print(f"数据库URL: {settings.database.url}")
print(f"API端口: {settings.api.port}")
print(f"LLM模型: {settings.llm.model}")
```

### 3. 不同环境的配置
建议为不同环境创建不同的配置文件：
- `config.yaml` - 开发环境
- `config.prod.yaml` - 生产环境
- `config.test.yaml` - 测试环境

可以通过修改 `settings.py` 中的 `load_config_file()` 函数来指定不同的配置文件。

## 配置优先级

1. 代码中显式传入的参数
2. 配置文件中的设置
3. 默认值

## 注意事项

### 安全性
- 生产环境务必修改 `secret_key`
- 不要将包含敏感信息的配置文件提交到版本控制系统
- 建议使用 `.gitignore` 忽略生产环境配置文件

### 文件权限
- 确保配置文件的读取权限
- 生产环境建议限制配置文件的访问权限

### 配置验证
系统启动时会自动验证配置的有效性，如有错误会在日志中显示详细信息。

## 故障排除

### 配置文件不存在
如果配置文件不存在，系统会显示警告信息并使用默认配置。

### 配置格式错误
如果YAML格式有误，系统会显示具体的错误信息。

### 配置值类型错误
Pydantic会自动进行类型验证和转换，如果类型不匹配会抛出详细的错误。

## 示例

完整的配置文件示例请参考项目根目录的 `config.yaml` 文件。 