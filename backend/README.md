# Web安全事件管理系统 - 后端

基于大语言模型的Web应用安全事件管理系统后端服务。

## 🏗 项目架构

```
backend/
├── app/
│   ├── capture/          # HTTP请求捕获模块
│   │   ├── base.py       # 捕获器基类
│   │   ├── log_capturer.py   # 日志文件捕获器
│   │   └── __init__.py
│   ├── detector/         # 安全检测引擎模块
│   │   ├── base.py       # 检测器基类
│   │   ├── sql_injection_detector.py   # SQL注入检测器
│   │   ├── xss_detector.py     # XSS攻击检测器
│   │   ├── detection_engine.py # 检测引擎聚合器
│   │   └── __init__.py
│   ├── llm/             # LLM分析模块
│   │   ├── base.py      # LLM提供者基类
│   │   ├── openai_provider.py  # OpenAI实现
│   │   └── __init__.py
│   ├── storage/         # 数据存储模块
│   │   ├── base.py      # 存储基类
│   │   └── __init__.py
│   ├── api/             # API接口模块
│   │   ├── events.py    # 事件相关接口
│   │   ├── statistics.py    # 统计相关接口
│   │   └── __init__.py
│   ├── config/          # 配置管理模块
│   │   ├── settings.py  # 系统配置
│   │   └── __init__.py
│   ├── core/            # 核心数据结构和异常
│   │   ├── models.py    # 数据模型
│   │   ├── exceptions.py    # 异常类
│   │   └── __init__.py
│   └── __init__.py
├── requirements.txt     # Python依赖
├── main.py             # 主程序入口
└── README.md           # 项目说明
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
复制并修改环境变量配置：
```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
# 主要配置项：
# - OPENAI_API_KEY: OpenAI API密钥
# - DATABASE_URL: 数据库连接URL
# - REDIS_URL: Redis连接URL
```

### 3. 启动服务
```bash
# 开发模式启动
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问服务
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 📖 API接口说明

### 事件检测接口
```bash
# 检测HTTP请求
POST /api/v1/events/detect
{
    "url": "/login?id=1' OR 1=1--",
    "method": "GET",
    "source_ip": "192.168.1.100"
}

# 查询事件列表
GET /api/v1/events?page=1&page_size=20&is_attack=true

# 获取事件详情
GET /api/v1/events/{event_id}
```

### 统计接口
```bash
# 获取仪表板数据
GET /api/v1/statistics/dashboard?hours=24

# 获取趋势数据
GET /api/v1/statistics/trends?period=hour&limit=24

# 获取攻击类型统计
GET /api/v1/statistics/attack-types?hours=24
```

## 🔧 模块说明

### 核心数据模型 (`core/models.py`)
- `HTTPRequest`: HTTP请求数据结构
- `DetectionResult`: 检测结果数据结构
- `LLMAnalysis`: LLM分析结果
- `SecurityEvent`: 完整的安全事件

### HTTP请求捕获 (`capture/`)
- `BaseCapturer`: 捕获器基类
- `LogFileCapturer`: 从日志文件捕获HTTP请求

### 安全检测引擎 (`detector/`)
- `BaseDetector`: 检测器基类
- `SQLInjectionDetector`: SQL注入检测器
- `XSSDetector`: XSS攻击检测器
- `DetectionEngine`: 检测引擎聚合器

### LLM分析 (`llm/`)
- `BaseLLMProvider`: LLM提供者基类
- `OpenAIProvider`: OpenAI API实现
- `LLMProviderFactory`: LLM提供者工厂

### 数据存储 (`storage/`)
- `BaseStorage`: 存储基类
- 支持MySQL、PostgreSQL、SQLite

## 🔍 使用示例

### 基础检测示例
```python
from app.detector import DetectionEngine
from app.core.models import HTTPRequest
from datetime import datetime

# 创建检测引擎
engine = DetectionEngine()

# 构建HTTP请求
request = HTTPRequest(
    url="/login?id=1' OR 1=1--",
    method="GET",
    headers={},
    params={"id": "1' OR 1=1--"},
    body=None,
    source_ip="192.168.1.100",
    timestamp=datetime.now(),
    raw_data="GET /login?id=1' OR 1=1-- HTTP/1.1"
)

# 执行检测
result = engine.detect_all(request)
print(f"是否攻击: {result.is_attack}")
print(f"攻击类型: {result.attack_types}")
print(f"置信度: {result.confidence}")
```

### LLM分析示例
```python
from app.llm import LLMProviderFactory
from app.core.models import SecurityEvent

# 创建LLM提供者
llm_provider = LLMProviderFactory.create_provider(
    "openai", 
    {"api_key": "your-api-key"}
)

# 分析安全事件
analysis = await llm_provider.analyze_security_event(security_event)
print(f"危险等级: {analysis.severity}")
print(f"攻击意图: {analysis.attack_intent}")
print(f"防护建议: {analysis.recommendations}")
```

## 🛠 开发指南

### 添加新的检测器
1. 继承 `BaseDetector` 或 `PatternDetector`
2. 实现 `detect` 方法
3. 在 `DetectionEngine` 中注册

```python
from app.detector.base import PatternDetector
from app.core.models import AttackType

class CustomDetector(PatternDetector):
    def __init__(self):
        patterns = [r"your-pattern-here"]
        super().__init__(patterns)
        self.attack_type = AttackType.CUSTOM
```

### 添加新的LLM提供者
1. 继承 `BaseLLMProvider`
2. 实现必需的抽象方法
3. 通过工厂注册

```python
from app.llm.base import BaseLLMProvider

class CustomLLMProvider(BaseLLMProvider):
    async def analyze_security_event(self, event):
        # 实现分析逻辑
        pass

# 注册提供者
LLMProviderFactory.register_provider("custom", CustomLLMProvider)
```

## 📋 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | development |
| `API_PORT` | API端口 | 8000 |
| `DATABASE_URL` | 数据库URL | sqlite:///security_events.db |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `LLM_DAILY_LIMIT` | LLM每日调用限制 | 1000 |
| `DETECTION_CONFIDENCE_THRESHOLD` | 检测置信度阈值 | 0.8 |

## 🧪 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app tests/

# 运行特定测试
pytest tests/test_detector.py -v
```

## 📝 TODO

- [ ] 实现MySQL/PostgreSQL存储器
- [ ] 添加Redis缓存支持
- [ ] 实现实时流量捕获器
- [ ] 添加更多攻击检测器（命令注入、路径遍历等）
- [ ] 实现LLM成本控制和缓存
- [ ] 添加统计分析功能
- [ ] 实现报告生成功能
- [ ] 添加完整的测试用例
- [ ] 实现Docker部署
- [ ] 添加API认证和授权

## �� 许可证

MIT License 