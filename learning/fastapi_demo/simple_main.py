"""
FastAPI Demo - 图书管理系统（简化版）
演示FastAPI的核心功能和用法
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# 创建FastAPI应用实例
app = FastAPI(
    title="📚 图书管理系统 API",
    description="一个演示FastAPI用法的图书管理系统",
    version="1.0.0",
    docs_url="/docs",  # Swagger文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# ===== 数据模型定义 =====

class BookBase(BaseModel):
    """图书基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="图书标题")
    author: str = Field(..., min_length=1, max_length=100, description="作者")
    price: float = Field(..., gt=0, le=1000, description="价格（必须大于0，小于等于1000）")
    category: str = Field(..., description="分类")
    description: Optional[str] = Field(None, max_length=500, description="图书描述")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """价格验证器"""
        if v <= 0:
            raise ValueError('价格必须大于0')
        return round(v, 2)  # 保留两位小数

class BookCreate(BookBase):
    """创建图书的请求模型"""
    pass

class BookUpdate(BaseModel):
    """更新图书的请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0, le=1000)
    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)

class Book(BookBase):
    """完整的图书模型"""
    id: int = Field(..., description="图书ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        # 允许从ORM对象创建
        from_attributes = True

class APIResponse(BaseModel):
    """标准API响应模型"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")

# ===== 内存数据库（演示用） =====

class BookDatabase:
    """简单的内存数据库"""
    
    def __init__(self):
        self.books = {}
        self.next_id = 1
        # 初始化一些示例数据
        self._init_sample_data()
    
    def _init_sample_data(self):
        """初始化示例数据"""
        sample_books = [
            {
                "title": "Python编程：从入门到实践",
                "author": "Eric Matthes",
                "price": 89.0,
                "category": "编程",
                "description": "一本很棒的Python入门书籍"
            },
            {
                "title": "深度学习",
                "author": "Ian Goodfellow",
                "price": 128.0,
                "category": "AI",
                "description": "深度学习领域的经典教材"
            },
            {
                "title": "设计模式",
                "author": "Gang of Four",
                "price": 79.0,
                "category": "软件工程",
                "description": "软件设计模式的经典之作"
            }
        ]
        
        for book_data in sample_books:
            self.create_book(BookCreate(**book_data))
    
    def create_book(self, book_data: BookCreate) -> Book:
        """创建图书"""
        book = Book(
            id=self.next_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **book_data.model_dump()
        )
        self.books[self.next_id] = book
        self.next_id += 1
        return book
    
    def get_book(self, book_id: int) -> Optional[Book]:
        """获取单本图书"""
        return self.books.get(book_id)
    
    def get_books(self, skip: int = 0, limit: int = 100, 
                  category: Optional[str] = None) -> List[Book]:
        """获取图书列表"""
        books = list(self.books.values())
        
        # 分类过滤
        if category:
            books = [book for book in books if book.category.lower() == category.lower()]
        
        # 分页
        return books[skip:skip + limit]
    
    def update_book(self, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        """更新图书"""
        if book_id not in self.books:
            return None
        
        book = self.books[book_id]
        # 从 BookUpdate 模型中获取提供的字段
        # exclude_unset=True 表示只包含在请求中实际设置的字段
        # 这样可以实现部分更新，未提供的字段保持原值
        update_data = book_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(book, field, value)
        
        book.updated_at = datetime.now()
        return book
    
    def delete_book(self, book_id: int) -> bool:
        """删除图书"""
        if book_id in self.books:
            del self.books[book_id]
            return True
        return False
    
    def search_books(self, keyword: str) -> List[Book]:
        """搜索图书"""
        keyword = keyword.lower()
        results = []
        
        for book in self.books.values():
            if (keyword in book.title.lower() or 
                keyword in book.author.lower() or 
                keyword in book.category.lower()):
                results.append(book)
        
        return results

# 创建数据库实例
db = BookDatabase()

# ===== 依赖注入 =====

def get_database() -> BookDatabase:
    """获取数据库实例"""
    return db

# ===== API路由定义 =====

@app.get("/", tags=["首页"])
async def root():
    """根路径 - API信息"""
    return {
        "message": "📚 欢迎使用图书管理系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "增删改查图书",
            "图书搜索",
            "分类筛选",
            "数据验证",
            "自动文档"
        ]
    }

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "books_count": len(db.books)
    }

# ===== 图书相关API =====

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["图书管理"])
async def create_book(
    book_data: BookCreate,
    database: BookDatabase = Depends(get_database)
):
    """
    创建新图书
    
    - **title**: 图书标题（必填）
    - **author**: 作者（必填）
    - **price**: 价格（必填，大于0）
    - **category**: 分类（必填）
    - **description**: 描述（可选）
    """
    try:
        book = database.create_book(book_data)
        return book
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建图书失败: {str(e)}"
        )

@app.get("/books", response_model=List[Book], tags=["图书管理"])
async def get_books(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    database: BookDatabase = Depends(get_database)
):
    """
    获取图书列表
    
    支持分页和分类筛选
    """
    books = database.get_books(skip=skip, limit=limit, category=category)
    return books

@app.get("/books/{book_id}", response_model=Book, tags=["图书管理"])
async def get_book(
    book_id: int,
    database: BookDatabase = Depends(get_database)
):
    """
    根据ID获取单本图书
    """
    book = database.get_book(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"图书ID {book_id} 不存在"
        )
    return book

@app.put("/books/{book_id}", response_model=Book, tags=["图书管理"])
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    database: BookDatabase = Depends(get_database)
):
    """
    更新图书信息
    
    只需要提供要更新的字段
    """
    book = database.update_book(book_id, book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"图书ID {book_id} 不存在"
        )
    return book

@app.delete("/books/{book_id}", response_model=APIResponse, tags=["图书管理"])
async def delete_book(
    book_id: int,
    database: BookDatabase = Depends(get_database)
):
    """
    删除图书
    """
    success = database.delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"图书ID {book_id} 不存在"
        )
    
    return APIResponse(
        code=200,
        message=f"图书ID {book_id} 删除成功"
    )

# ===== 搜索API =====

@app.get("/books/search/", response_model=List[Book], tags=["搜索"])
async def search_books(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    database: BookDatabase = Depends(get_database)
):
    """
    搜索图书
    
    在标题、作者、分类中搜索关键词
    """
    books = database.search_books(q)
    return books

# ===== 统计API =====

@app.get("/stats", tags=["统计"])
async def get_statistics(database: BookDatabase = Depends(get_database)):
    """
    获取图书统计信息
    """
    books = list(database.books.values())
    
    # 按分类统计
    category_stats = {}
    total_value = 0
    
    for book in books:
        category = book.category
        if category not in category_stats:
            category_stats[category] = {"count": 0, "total_value": 0}
        
        category_stats[category]["count"] += 1
        category_stats[category]["total_value"] += book.price
        total_value += book.price
    
    return {
        "total_books": len(books),
        "total_value": round(total_value, 2),
        "average_price": round(total_value / len(books), 2) if books else 0,
        "categories": category_stats,
        "most_expensive": max(books, key=lambda x: x.price) if books else None,
        "cheapest": min(books, key=lambda x: x.price) if books else None
    }

# ===== 异常处理示例 =====

@app.get("/books/error-demo", tags=["异常演示"])
async def error_demo(error_type: str = Query("not_found", description="错误类型")):
    """
    演示不同类型的异常处理
    """
    if error_type == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="这是一个404错误示例"
        )
    elif error_type == "validation":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="这是一个数据验证错误示例"
        )
    elif error_type == "server_error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="这是一个服务器错误示例"
        )
    else:
        return {"message": "没有错误，一切正常！"}

# ===== 启动提示 =====

if __name__ == "__main__":
    print("🚀 FastAPI图书管理系统Demo已准备就绪！")
    print("📖 要查看API文档，请运行：")
    print("   fastapi dev simple_main.py")
    print("📚 然后访问: http://localhost:8000/docs")
    print("💡 或者运行：python -m fastapi dev simple_main.py") 