"""
基础异步编程示例
演示async/await的基本用法和概念
"""

import asyncio
import time
from typing import List

# 1. 同步函数示例 - 阻塞执行
def sync_task(name: str, duration: int) -> str:
    """同步任务 - 会阻塞线程"""
    print(f"[同步] 任务 {name} 开始执行...")
    time.sleep(duration)  # 模拟耗时操作（会阻塞整个线程）
    print(f"[同步] 任务 {name} 执行完成，耗时 {duration} 秒")
    return f"任务 {name} 的结果"

# 2. 异步函数示例 - 非阻塞执行
async def async_task(name: str, duration: int) -> str:
    """异步任务 - 不会阻塞事件循环"""
    print(f"[异步] 任务 {name} 开始执行...")
    await asyncio.sleep(duration)  # 模拟耗时操作（不会阻塞事件循环）
    print(f"[异步] 任务 {name} 执行完成，耗时 {duration} 秒")
    return f"任务 {name} 的结果"

# 3. 网络请求模拟
async def fetch_data(url: str) -> dict:
    """模拟异步网络请求"""
    print(f"开始请求: {url}")
    # 模拟网络延迟
    await asyncio.sleep(2)
    print(f"请求完成: {url}")
    return {"url": url, "status": "success", "data": "some data"}

# 4. 数据库操作模拟
async def query_database(sql: str) -> List[dict]:
    """模拟异步数据库查询"""
    print(f"执行SQL: {sql}")
    await asyncio.sleep(1.5)  # 模拟数据库查询时间
    print(f"SQL执行完成: {sql}")
    return [{"id": 1, "name": "测试数据"}]

# 5. 演示同步vs异步的区别
def demo_sync_vs_async():
    """演示同步和异步执行的区别"""
    print("=" * 50)
    print("1. 同步执行演示（阻塞）")
    print("=" * 50)
    
    start_time = time.time()
    
    # 同步执行 - 一个接一个执行
    sync_task("A", 2)
    sync_task("B", 2)
    sync_task("C", 2)
    
    sync_time = time.time() - start_time
    print(f"同步执行总耗时: {sync_time:.2f} 秒\n")

async def demo_async_execution():
    """演示异步执行"""
    print("=" * 50)
    print("2. 异步执行演示（非阻塞）")
    print("=" * 50)
    
    start_time = time.time()
    
    # 异步执行 - 并发执行
    tasks = [
        async_task("A", 2),
        async_task("B", 2), 
        async_task("C", 2)
    ]
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks)
    
    async_time = time.time() - start_time
    print(f"异步执行总耗时: {async_time:.2f} 秒")
    print(f"执行结果: {results}\n")

async def demo_sequential_async():
    """演示顺序执行的异步任务"""
    print("=" * 50)
    print("3. 顺序异步执行演示")
    print("=" * 50)
    
    start_time = time.time()
    
    # 顺序执行异步任务（等待每个任务完成后再执行下一个）
    result1 = await async_task("顺序-A", 1)
    result2 = await async_task("顺序-B", 1)
    result3 = await async_task("顺序-C", 1)
    
    sequential_time = time.time() - start_time
    print(f"顺序异步执行总耗时: {sequential_time:.2f} 秒\n")

async def demo_mixed_operations():
    """演示混合异步操作"""
    print("=" * 50)
    print("4. 混合异步操作演示")
    print("=" * 50)
    
    # 同时执行不同类型的异步操作
    tasks = [
        fetch_data("https://api.example1.com/data"),
        fetch_data("https://api.example2.com/data"),
        query_database("SELECT * FROM users"),
        query_database("SELECT * FROM products"),
        async_task("计算任务", 1)
    ]
    
    # 并发执行所有任务
    results = await asyncio.gather(*tasks)
    
    print("所有操作完成！")
    for i, result in enumerate(results):
        print(f"任务 {i+1} 结果: {result}")

# 6. 异常处理示例
async def risky_task(name: str, should_fail: bool = False):
    """可能失败的异步任务"""
    print(f"执行风险任务: {name}")
    await asyncio.sleep(1)
    
    if should_fail:
        raise Exception(f"任务 {name} 执行失败！")
    
    return f"任务 {name} 成功完成"

async def demo_error_handling():
    """演示异步异常处理"""
    print("=" * 50)
    print("5. 异步异常处理演示")
    print("=" * 50)
    
    tasks = [
        risky_task("安全任务", False),
        risky_task("危险任务", True),
        risky_task("另一个安全任务", False)
    ]
    
    # 使用 gather 的 return_exceptions=True 参数
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"任务 {i+1} 失败: {result}")
        else:
            print(f"任务 {i+1} 成功: {result}")

# 主函数
async def main():
    """主异步函数"""
    print("🚀 Python异步编程基础示例\n")
    
    # 先演示同步执行
    demo_sync_vs_async()
    
    # 再演示各种异步模式
    await demo_async_execution()
    await demo_sequential_async()
    await demo_mixed_operations()
    await demo_error_handling()
    
    print("✅ 所有示例执行完成！")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 