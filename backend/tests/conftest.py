"""
Pytest配置文件
设置测试环境和公共fixture
"""

import pytest
import asyncio
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# 移除异步的cleanup fixture，简化配置
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """每个测试后的清理工作"""
    yield
    # 测试后清理工作可以在这里添加
    pass 