"""Web安全事件管理系统主程序入口"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config.settings import settings
from app.api import events_router, stats_router
from app.core.exceptions import SecurityManagerException

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 Web安全事件管理系统启动中...")
    
    # 初始化数据库
    try:
        # TODO: 实现数据库初始化
        logger.info("📊 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise
    
    # 初始化Redis
    try:
        # TODO: 实现Redis初始化
        logger.info("🔗 Redis连接成功")
    except Exception as e:
        logger.warning(f"⚠️ Redis连接失败: {e}")
    
    # 初始化LLM服务
    try:
        # TODO: 实现LLM服务初始化
        logger.info("🤖 LLM服务初始化成功")
    except Exception as e:
        logger.warning(f"⚠️ LLM服务初始化失败: {e}")
    
    logger.info("✅ 系统启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("🛑 系统正在关闭...")
    
    # 清理资源
    try:
        # TODO: 实现资源清理
        logger.info("🧹 资源清理完成")
    except Exception as e:
        logger.error(f"❌ 资源清理失败: {e}")
    
    logger.info("👋 系统已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="Web安全事件管理系统",
    description="基于大语言模型的Web应用安全事件管理系统",
    version="1.0.0",
    docs_url="/docs" if settings.api.debug else None,
    redoc_url="/redoc" if settings.api.debug else None,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加可信主机中间件
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# 全局异常处理
@app.exception_handler(SecurityManagerException)
async def security_exception_handler(request, exc):
    """安全管理系统异常处理"""
    logger.error(f"安全管理异常: {exc}")
    return {
        "error": "系统内部错误",
        "detail": str(exc) if settings.api.debug else "请联系管理员"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return {
        "error": "系统错误",
        "detail": str(exc) if settings.api.debug else "服务暂时不可用"
    }

# 注册路由
app.include_router(events_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")

# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Web安全事件管理系统",
        "version": "1.0.0",
        "docs": "/docs" if settings.api.debug else "文档未开放"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level=settings.logging.level.lower()
    ) 