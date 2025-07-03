# Python异步编程Demo

这是一个全面的Python异步编程学习示例，通过实际代码演示帮助你理解异步编程的核心概念和最佳实践。

## 📋 目录结构

```
async_demo/
├── basic_async.py          # 基础异步编程概念
├── async_generators.py     # 异步生成器示例
├── file_operations.py      # 异步文件操作
├── concurrent_tasks.py     # 并发任务控制
├── requirements.txt        # 项目依赖
└── README.md              # 说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例

每个Python文件都可以独立运行：

```bash
# 基础异步概念
python basic_async.py

# 异步生成器
python async_generators.py

# 异步文件操作
python file_operations.py

# 并发任务控制
python concurrent_tasks.py
```

## 📚 学习内容

### 1. basic_async.py - 基础异步编程

**核心概念：**
- `async/await` 语法基础
- 同步 vs 异步执行对比
- 异步函数的定义和调用
- `asyncio.gather()` 并发执行
- 异常处理机制

**示例包括：**
- 同步函数 vs 异步函数的性能对比
- 网络请求模拟
- 数据库查询模拟
- 混合异步操作
- 异步异常处理

**关键学习点：**
```python
# 异步函数定义
async def async_task(name: str, duration: int) -> str:
    await asyncio.sleep(duration)  # 非阻塞等待
    return f"任务 {name} 的结果"

# 并发执行多个任务
results = await asyncio.gather(
    async_task("A", 2),
    async_task("B", 3),
    async_task("C", 1)
)
```

### 2. async_generators.py - 异步生成器

**核心概念：**
- `AsyncGenerator` 类型注解
- `yield` 在异步函数中的使用
- `async for` 循环消费异步生成器
- 实时数据流处理
- 可控制的异步生成器

**示例包括：**
- 基础异步生成器
- 数据流监控（类似你的日志捕获）
- 文件行读取生成器
- 网络请求批处理
- 系统监控数据生成

**关键学习点：**
```python
# 异步生成器定义
async def data_stream() -> AsyncGenerator[dict, None]:
    for i in range(10):
        await asyncio.sleep(1)
        yield {"id": i, "data": f"数据{i}"}

# 消费异步生成器
async for data in data_stream():
    print(f"收到数据: {data}")
```

### 3. file_operations.py - 异步文件操作

**核心概念：**
- `aiofiles` 库的使用
- 异步文件读写
- 文件流式处理
- 文件监控（类似 `tail -f`）
- 批量文件处理

**示例包括：**
- 基础异步文件读写
- 日志文件实时监控（类似你的 log_capturer）
- 批量文件处理
- 大文件流式处理
- 文件内容搜索

**关键学习点：**
```python
# 异步文件读取
async with aiofiles.open('file.txt', 'r') as f:
    content = await f.read()
    
# 异步文件监控
async with aiofiles.open('log.txt', 'r') as f:
    await f.seek(0, 2)  # 移动到文件末尾
    while True:
        line = await f.readline()
        if line:
            process_log_line(line)
        else:
            await asyncio.sleep(0.1)
```

### 4. concurrent_tasks.py - 并发任务控制

**核心概念：**
- 任务创建和管理 (`asyncio.create_task`)
- 并发控制 (`asyncio.Semaphore`)
- 生产者-消费者模式 (`asyncio.Queue`)
- 锁和同步 (`asyncio.Lock`)
- 事件和条件变量 (`asyncio.Event`)
- 超时控制 (`asyncio.wait_for`)
- 资源池管理

**示例包括：**
- 基础并发控制
- 任务生命周期管理
- 信号量限制并发数
- 队列实现生产者-消费者
- 锁保护共享资源
- 事件协调多个协程
- 超时处理机制
- 网页爬虫模拟
- 资源池管理

**关键学习点：**
```python
# 信号量控制并发数
semaphore = asyncio.Semaphore(3)  # 最多3个并发

async def worker(worker_id):
    async with semaphore:
        # 工作代码
        await do_work()

# 生产者-消费者模式
queue = asyncio.Queue(maxsize=10)

async def producer():
    await queue.put(item)

async def consumer():
    item = await queue.get()
    queue.task_done()
```

## 🎯 与你的项目关联

这个demo特别关注了与你的 `log_capturer.py` 相似的模式：

1. **文件监控模式** - `file_operations.py` 中的日志监控示例
2. **异步生成器** - `async_generators.py` 中的流式数据处理
3. **并发控制** - `concurrent_tasks.py` 中的资源管理

## 💡 核心异步编程概念

### 1. 事件循环 (Event Loop)
异步编程的核心，负责调度和执行异步任务。

### 2. 协程 (Coroutine)
使用 `async def` 定义的函数，可以被暂停和恢复执行。

### 3. 等待点 (Await Point)
使用 `await` 的地方，协程会在此处暂停，让出控制权。

### 4. 并发 vs 并行
- **并发**: 多个任务交替执行（单线程）
- **并行**: 多个任务同时执行（多线程/多进程）

### 5. 非阻塞 I/O
异步操作不会阻塞整个程序，其他任务可以继续执行。

## 🔧 最佳实践

### 1. 何时使用异步编程
- I/O 密集型任务（文件读写、网络请求、数据库操作）
- 需要高并发处理的场景
- 实时数据流处理

### 2. 避免常见陷阱
- 不要在异步函数中使用阻塞操作（如 `time.sleep`）
- 正确处理异步异常
- 避免忘记使用 `await` 关键字

### 3. 性能优化
- 使用信号量控制并发数量
- 适当使用超时处理
- 合理管理资源（文件句柄、网络连接等）

## 🏃‍♂️ 实际应用场景

1. **Web 爬虫** - 并发抓取多个网页
2. **API 服务** - 处理大量并发请求
3. **数据处理** - 实时处理数据流
4. **文件监控** - 监控日志文件变化
5. **批量操作** - 并发处理大量文件或数据

## 📖 进阶学习

运行完这些示例后，建议深入学习：

1. `asyncio` 官方文档
2. `aiohttp` 用于异步HTTP客户端/服务器
3. `asyncpg` 用于异步PostgreSQL操作
4. `aioredis` 用于异步Redis操作
5. FastAPI 框架（异步Web框架）

## 🤝 与你的代码对比

你的 `log_capturer.py` 中的关键模式：

```python
# 你的代码模式
async def capture_stream(self) -> AsyncGenerator[HTTPRequest, None]:
    async with aiofiles.open(self.log_file_path, 'r') as f:
        while self.is_running:
            line = await f.readline()
            if line:
                request = self._parse_log_line(line.strip())
                if request:
                    yield request
            else:
                await asyncio.sleep(0.1)
```

对应的demo示例在 `file_operations.py` 和 `async_generators.py` 中。

## 🎉 总结

通过这个demo，你将学会：
- 异步编程的基本概念和语法
- 如何编写高效的异步代码
- 并发控制和资源管理
- 实际应用场景的最佳实践

每个示例都包含详细注释，帮助你理解异步编程的工作原理和应用方法。 