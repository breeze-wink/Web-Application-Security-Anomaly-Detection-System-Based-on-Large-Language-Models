# 📚 FastAPI Demo - 图书管理系统

这是一个完整的FastAPI演示项目，用于学习和理解FastAPI的核心功能。

## 🎯 项目特点

### 核心功能演示
- ✅ **RESTful API** - 完整的CRUD操作
- ✅ **数据验证** - Pydantic模型和Field验证
- ✅ **自动文档** - Swagger UI 和 ReDoc
- ✅ **依赖注入** - FastAPI的DI系统
- ✅ **中间件** - 请求日志中间件
- ✅ **异常处理** - 统一的错误处理
- ✅ **异步支持** - 异步API演示
- ✅ **查询参数** - 分页、筛选、搜索

### API接口列表

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/` | 首页信息 | API基本信息 |
| GET | `/health` | 健康检查 | 系统状态 |
| GET | `/docs` | API文档 | Swagger UI |
| GET | `/redoc` | API文档 | ReDoc格式 |
| **图书管理** ||||
| POST | `/books` | 创建图书 | 新增图书记录 |
| GET | `/books` | 获取图书列表 | 支持分页和筛选 |
| GET | `/books/{id}` | 获取单本图书 | 根据ID查询 |
| PUT | `/books/{id}` | 更新图书 | 修改图书信息 |
| DELETE | `/books/{id}` | 删除图书 | 删除指定图书 |
| **搜索功能** ||||
| GET | `/books/search/` | 搜索图书 | 关键词搜索 |
| **统计功能** ||||
| GET | `/stats` | 统计信息 | 图书统计数据 |
| **演示功能** ||||
| GET | `/books/async-demo/{id}` | 异步处理演示 | 模拟耗时操作 |
| GET | `/books/error-demo` | 异常处理演示 | 各种错误示例 |

## 🚀 快速开始

### 1. 安装依赖
```bash
cd fastapi_demo
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python main.py
```

### 3. 访问API文档
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API首页**: http://localhost:8000

## 📖 学习要点

### 1. FastAPI应用创建
```python
app = FastAPI(
    title="📚 图书管理系统 API",
    description="一个演示FastAPI用法的图书管理系统",
    version="1.0.0"
)
```

### 2. Pydantic数据模型
```python
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, le=1000)
    category: str
    description: Optional[str] = None
```

### 3. 路径参数和查询参数
```python
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    pass

@app.get("/books")
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    pass
```

### 4. 依赖注入
```python
def get_database() -> BookDatabase:
    return db

@app.post("/books")
async def create_book(
    book_data: BookCreate,
    database: BookDatabase = Depends(get_database)
):
    pass
```

### 5. 异常处理
```python
if not book:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"图书ID {book_id} 不存在"
    )
```

### 6. 中间件
```python
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    print(f"📝 {request.method} {request.url} - {process_time:.3f}s")
    return response
```

## 🧪 测试API

### 使用curl测试

#### 1. 获取所有图书
```bash
curl http://localhost:8000/books
```

#### 2. 创建新图书
```bash
curl -X POST "http://localhost:8000/books" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "FastAPI实战",
       "author": "张三",
       "price": 99.9,
       "category": "编程",
       "description": "FastAPI框架实战教程"
     }'
```

#### 3. 搜索图书
```bash
curl "http://localhost:8000/books/search/?q=Python"
```

#### 4. 获取统计信息
```bash
curl http://localhost:8000/stats
```

### 使用Swagger UI测试
1. 访问 http://localhost:8000/docs
2. 点击任意API接口
3. 点击"Try it out"按钮
4. 填写参数并点击"Execute"

## 💡 核心概念解释

### FastAPI vs Flask/Django
- **FastAPI**: 现代异步API框架，自动文档，类型安全
- **Flask**: 轻量级，灵活，需要手动配置很多功能
- **Django**: 全栈框架，适合大型Web应用

### Pydantic的作用
- **数据验证**: 自动验证请求数据
- **类型转换**: 自动转换数据类型
- **错误提示**: 详细的验证错误信息
- **自动文档**: 生成API文档的数据模型

### 异步的优势
- **高并发**: 支持同时处理多个请求
- **性能**: 比同步框架快2-3倍
- **现代化**: 支持async/await语法

### 依赖注入的好处
- **解耦**: 组件之间松耦合
- **测试**: 容易进行单元测试
- **复用**: 依赖可以在多个地方复用
- **管理**: 统一管理组件生命周期

## 🔍 代码结构

```
fastapi_demo/
├── main.py              # 主程序文件
├── requirements.txt     # 依赖包列表
└── README.md           # 项目说明
```

这个Demo包含了约400行代码，涵盖了FastAPI的所有核心功能，是学习FastAPI的绝佳起点！

## 📚 学习建议

1. **先运行**: 先把项目跑起来，在浏览器中查看API文档
2. **看代码**: 从main.py开始，理解每个部分的作用
3. **试接口**: 使用Swagger UI测试各个API接口
4. **改代码**: 尝试修改代码，添加新的功能
5. **理解概念**: 深入理解异步、依赖注入等核心概念

祝您学习愉快！🎉 