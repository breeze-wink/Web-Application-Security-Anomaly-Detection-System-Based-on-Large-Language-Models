# LogFileCapturer 功能测试

这个目录包含了对 `LogFileCapturer` 类的全面功能测试。

## 📁 文件结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py              # pytest配置文件
├── test_log_capturer.py     # 主要测试文件
├── run_tests.py             # 测试运行脚本
├── sample_logs/             # 测试用样本日志
│   └── access.log           # Apache格式访问日志样本
└── README.md                # 本文件
```

## 🧪 测试覆盖范围

### 单元测试
- ✅ `_parse_query_string()` - 查询参数解析
- ✅ `_parse_log_line()` - 日志行解析
- ✅ 各种日志格式的解析（GET、POST、SQL注入、XSS等）
- ✅ 无效格式日志的处理

### 异步功能测试
- ✅ `capture_single()` - 单个请求捕获
- ✅ `capture_stream()` - 流式请求捕获
- ✅ 文件位置跟踪
- ✅ 实时模式和批量模式
- ✅ 并发访问处理

### 错误处理测试
- ✅ 文件不存在的异常处理
- ✅ 权限错误处理
- ✅ 格式错误日志的跳过

### 边界条件测试
- ✅ 空文件处理
- ✅ 文件读取完毕的处理
- ✅ 并发调用安全性

## 🚀 运行测试

### 方法1: 使用便捷脚本（推荐）

```bash
# 切换到tests目录
cd backend/tests

# 运行所有测试
python run_tests.py

# 运行特定测试
python run_tests.py test_parse_query_string
```

### 方法2: 直接使用pytest

```bash
# 安装依赖
pip install pytest pytest-asyncio

# 切换到tests目录
cd backend/tests

# 运行所有测试
pytest test_log_capturer.py -v

# 运行特定测试类
pytest test_log_capturer.py::TestLogFileCapturer -v

# 运行特定测试方法
pytest test_log_capturer.py::TestLogFileCapturer::test_parse_query_string -v
```

### 方法3: 直接运行测试文件

```bash
cd backend/tests
python test_log_capturer.py
```

## 📊 测试数据

测试使用了多种类型的HTTP请求日志：

1. **标准GET请求** - 带查询参数
2. **POST请求** - 登录表单提交
3. **SQL注入尝试** - `' OR 1=1--` 模式
4. **XSS攻击尝试** - `<script>alert(1)</script>` 
5. **路径遍历攻击** - `../../../etc/passwd`
6. **404错误** - 不存在的资源
7. **API请求** - RESTful接口调用
8. **移动端请求** - iPhone用户代理

## 🔧 测试环境要求

- Python 3.7+
- pytest
- pytest-asyncio
- aiofiles（在主项目requirements.txt中）

## 📝 添加新测试

1. 在 `TestLogFileCapturer` 类中添加新的测试方法
2. 使用 `@pytest.mark.asyncio` 装饰器标记异步测试
3. 使用提供的 fixtures 获取测试数据：
   - `temp_log_file` - 临时日志文件
   - `capturer` - LogFileCapturer实例
   - `sample_log_lines` - 测试日志行数据

## 🐛 故障排除

### 常见问题

1. **ImportError: No module named 'pytest'**
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **路径错误**
   确保在 `backend/tests` 目录下运行测试

3. **异步测试失败**
   检查是否安装了 `pytest-asyncio`

4. **权限错误**
   确保测试目录有写权限（用于创建临时文件）

### 调试技巧

- 使用 `-s` 选项查看print输出：`pytest -s`
- 使用 `-v` 选项获得详细输出：`pytest -v`
- 使用 `--tb=long` 查看完整错误信息
- 单独运行失败的测试进行调试

## 📈 测试报告

运行测试后会显示：
- ✅ 通过的测试数量
- ❌ 失败的测试详情
- ⏱️ 最慢的测试耗时
- 📊 整体覆盖情况

Example output:
```
🚀 开始运行 LogFileCapturer 功能测试...
✅ pytest 已安装
✅ pytest-asyncio 已安装
--------------------------------------------------
test_log_capturer.py::TestLogFileCapturer::test_parse_query_string PASSED
test_log_capturer.py::TestLogFileCapturer::test_parse_log_line_success PASSED
...
🎉 所有测试通过！
✅ LogFileCapturer 功能正常
``` 