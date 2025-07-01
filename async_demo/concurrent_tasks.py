"""
并发任务控制示例
演示 asyncio 中的并发控制、任务管理、信号量等高级用法
"""

import asyncio
import random
import time
from typing import List, Dict, Any
from datetime import datetime

# 1. 基础并发控制
async def demo_basic_concurrency():
    """演示基础并发控制"""
    print("=" * 50)
    print("1. 基础并发控制演示")
    print("=" * 50)
    
    async def worker(name: str, work_time: float) -> str:
        """工作协程"""
        print(f"工作者 {name} 开始工作...")
        await asyncio.sleep(work_time)
        print(f"工作者 {name} 完成工作，耗时 {work_time} 秒")
        return f"工作者 {name} 的结果"
    
    # 1.1 asyncio.gather - 等待所有任务完成
    print("使用 asyncio.gather 并发执行:")
    start_time = time.time()
    
    results = await asyncio.gather(
        worker("A", 2),
        worker("B", 1.5),
        worker("C", 3),
        worker("D", 1)
    )
    
    end_time = time.time()
    print(f"所有任务完成，总耗时: {end_time - start_time:.2f} 秒")
    print(f"结果: {results}")
    print()

# 2. 任务创建和管理
async def demo_task_management():
    """演示任务创建和管理"""
    print("=" * 50)
    print("2. 任务创建和管理演示")
    print("=" * 50)
    
    async def background_task(task_id: int):
        """后台任务"""
        print(f"后台任务 {task_id} 启动")
        for i in range(5):
            await asyncio.sleep(0.5)
            print(f"  任务 {task_id} 进度: {i+1}/5")
        print(f"后台任务 {task_id} 完成")
        return f"任务 {task_id} 结果"
    
    # 2.1 创建任务
    print("创建多个后台任务:")
    tasks = []
    for i in range(3):
        task = asyncio.create_task(background_task(i))
        tasks.append(task)
        print(f"已创建任务 {i}")
    
    # 2.2 等待特定任务完成
    print("\n等待第一个任务完成:")
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    
    for task in done:
        result = await task
        print(f"最快完成的任务结果: {result}")
    
    # 2.3 取消剩余任务
    print("取消剩余任务:")
    for task in pending:
        task.cancel()
        print(f"任务 {task} 已取消")
    
    # 等待取消操作完成
    await asyncio.gather(*pending, return_exceptions=True)
    print()

# 3. 信号量控制并发数量
async def demo_semaphore():
    """演示使用信号量控制并发数量"""
    print("=" * 50)
    print("3. 信号量控制并发数量演示")
    print("=" * 50)
    
    # 创建信号量，限制同时运行的任务数量为3
    semaphore = asyncio.Semaphore(3)
    
    async def limited_worker(worker_id: int):
        """受限制的工作者"""
        async with semaphore:  # 获取信号量
            print(f"工作者 {worker_id} 获得信号量，开始工作")
            work_time = random.uniform(1, 3)
            await asyncio.sleep(work_time)
            print(f"工作者 {worker_id} 完成工作，释放信号量")
            return f"工作者 {worker_id} 结果"
    
    # 创建10个任务，但同时只能运行3个
    print("创建10个任务，但限制同时运行3个:")
    tasks = [limited_worker(i) for i in range(10)]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"所有任务完成，总耗时: {end_time - start_time:.2f} 秒")
    print(f"完成任务数: {len(results)}")
    print()

# 4. 队列实现生产者-消费者模式
async def demo_producer_consumer():
    """演示生产者-消费者模式"""
    print("=" * 50)
    print("4. 生产者-消费者模式演示")
    print("=" * 50)
    
    # 创建队列
    queue = asyncio.Queue(maxsize=5)  # 限制队列大小
    
    async def producer(name: str, items: int):
        """生产者"""
        print(f"生产者 {name} 开始生产")
        for i in range(items):
            item = f"{name}-item-{i}"
            await queue.put(item)  # 向队列添加项目
            print(f"  生产者 {name} 生产了: {item}")
            await asyncio.sleep(random.uniform(0.1, 0.5))
        print(f"生产者 {name} 完成生产")
    
    async def consumer(name: str):
        """消费者"""
        print(f"消费者 {name} 开始消费")
        consumed_count = 0
        
        while True:
            try:
                # 设置超时，避免无限等待
                item = await asyncio.wait_for(queue.get(), timeout=2.0)
                print(f"  消费者 {name} 消费了: {item}")
                consumed_count += 1
                
                # 标记任务完成
                queue.task_done()
                
                # 模拟处理时间
                await asyncio.sleep(random.uniform(0.2, 0.8))
                
            except asyncio.TimeoutError:
                print(f"消费者 {name} 超时退出，共消费 {consumed_count} 个项目")
                break
    
    # 启动生产者和消费者
    await asyncio.gather(
        producer("生产者1", 5),
        producer("生产者2", 3),
        consumer("消费者A"),
        consumer("消费者B"),
        consumer("消费者C")
    )
    
    # 等待队列中所有任务完成
    await queue.join()
    print("生产者-消费者演示完成")
    print()

# 5. 锁和同步
async def demo_locks():
    """演示锁和同步机制"""
    print("=" * 50)
    print("5. 锁和同步机制演示")
    print("=" * 50)
    
    # 共享资源
    shared_resource = {"counter": 0, "data": []}
    lock = asyncio.Lock()
    
    async def worker_with_lock(worker_id: int):
        """使用锁的工作者"""
        for i in range(5):
            async with lock:  # 获取锁
                # 临界区：修改共享资源
                current_value = shared_resource["counter"]
                await asyncio.sleep(0.01)  # 模拟处理时间
                shared_resource["counter"] = current_value + 1
                shared_resource["data"].append(f"worker-{worker_id}-{i}")
                print(f"工作者 {worker_id} 更新计数器: {shared_resource['counter']}")
            
            # 非临界区
            await asyncio.sleep(0.1)
    
    # 启动多个工作者
    print("使用锁保护共享资源:")
    await asyncio.gather(*[worker_with_lock(i) for i in range(3)])
    
    print(f"最终计数器值: {shared_resource['counter']}")
    print(f"数据项数量: {len(shared_resource['data'])}")
    print()

# 6. 事件和条件变量
async def demo_events_and_conditions():
    """演示事件和条件变量"""
    print("=" * 50)
    print("6. 事件和条件变量演示")
    print("=" * 50)
    
    # 事件演示
    start_event = asyncio.Event()
    stop_event = asyncio.Event()
    
    async def waiter(name: str):
        """等待者"""
        print(f"等待者 {name} 等待开始信号...")
        await start_event.wait()  # 等待事件被设置
        print(f"等待者 {name} 收到开始信号，开始工作")
        
        # 工作一段时间
        work_time = random.uniform(1, 3)
        await asyncio.sleep(work_time)
        
        print(f"等待者 {name} 工作完成")
    
    async def coordinator():
        """协调者"""
        print("协调者: 准备阶段...")
        await asyncio.sleep(1)
        
        print("协调者: 发送开始信号")
        start_event.set()  # 设置事件，唤醒所有等待者
        
        await asyncio.sleep(4)
        print("协调者: 发送停止信号")
        stop_event.set()
    
    # 启动等待者和协调者
    await asyncio.gather(
        waiter("A"),
        waiter("B"),
        waiter("C"),
        coordinator()
    )
    print()

# 7. 超时控制
async def demo_timeout_control():
    """演示超时控制"""
    print("=" * 50)
    print("7. 超时控制演示")
    print("=" * 50)
    
    async def slow_operation(name: str, duration: float):
        """慢操作"""
        print(f"慢操作 {name} 开始，预计耗时 {duration} 秒")
        await asyncio.sleep(duration)
        print(f"慢操作 {name} 完成")
        return f"{name} 结果"
    
    # 7.1 单个操作超时
    print("单个操作超时测试:")
    try:
        result = await asyncio.wait_for(slow_operation("快速", 1), timeout=2.0)
        print(f"操作成功: {result}")
    except asyncio.TimeoutError:
        print("操作超时！")
    
    try:
        result = await asyncio.wait_for(slow_operation("慢速", 3), timeout=2.0)
        print(f"操作成功: {result}")
    except asyncio.TimeoutError:
        print("操作超时！")
    
    # 7.2 多个操作的超时控制
    print("\n多个操作超时测试:")
    tasks = [
        slow_operation("任务1", 1.5),
        slow_operation("任务2", 2.5),
        slow_operation("任务3", 0.5)
    ]
    
    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=2.0)
        print(f"所有操作完成: {results}")
    except asyncio.TimeoutError:
        print("批量操作超时！")
    
    print()

# 8. 实际应用：网页爬虫示例
async def demo_web_crawler_simulation():
    """演示实际应用：模拟网页爬虫"""
    print("=" * 50)
    print("8. 网页爬虫模拟演示")
    print("=" * 50)
    
    # 模拟网站
    websites = [
        {"url": "https://example1.com", "delay": 1.0},
        {"url": "https://example2.com", "delay": 1.5},
        {"url": "https://example3.com", "delay": 0.8},
        {"url": "https://example4.com", "delay": 2.0},
        {"url": "https://example5.com", "delay": 1.2},
        {"url": "https://example6.com", "delay": 0.5}
    ]
    
    # 控制并发数的信号量
    crawler_semaphore = asyncio.Semaphore(3)
    
    async def crawl_website(site: dict) -> dict:
        """爬取单个网站"""
        async with crawler_semaphore:
            print(f"开始爬取: {site['url']}")
            start_time = time.time()
            
            # 模拟网络请求
            await asyncio.sleep(site['delay'])
            
            end_time = time.time()
            
            # 模拟随机失败
            success = random.random() > 0.2  # 80%成功率
            
            result = {
                "url": site['url'],
                "success": success,
                "response_time": end_time - start_time,
                "timestamp": datetime.now().isoformat(),
                "data_size": random.randint(1000, 10000) if success else 0
            }
            
            status = "成功" if success else "失败"
            print(f"爬取{status}: {site['url']} ({result['response_time']:.2f}s)")
            
            return result
    
    # 执行爬虫任务
    print(f"开始爬取 {len(websites)} 个网站，并发限制为 3...")
    start_time = time.time()
    
    results = await asyncio.gather(*[crawl_website(site) for site in websites])
    
    end_time = time.time()
    
    # 统计结果
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    total_data = sum(r['data_size'] for r in results)
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    
    print(f"\n爬虫统计:")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"成功: {successful}, 失败: {failed}")
    print(f"平均响应时间: {avg_response_time:.2f} 秒")
    print(f"总数据量: {total_data} 字节")
    print()

# 9. 资源池管理
class AsyncResourcePool:
    """异步资源池"""
    
    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self.resources = asyncio.Queue(maxsize=max_size)
        self.created_count = 0
        self.lock = asyncio.Lock()
    
    async def create_resource(self) -> str:
        """创建新资源"""
        async with self.lock:
            self.created_count += 1
            resource_id = f"resource-{self.created_count}"
            print(f"创建新资源: {resource_id}")
            await asyncio.sleep(0.1)  # 模拟资源创建时间
            return resource_id
    
    async def get_resource(self) -> str:
        """获取资源"""
        try:
            # 先尝试从池中获取现有资源
            resource = self.resources.get_nowait()
            print(f"从池中获取资源: {resource}")
            return resource
        except asyncio.QueueEmpty:
            # 池中没有资源，创建新的
            if self.created_count < self.max_size:
                return await self.create_resource()
            else:
                # 等待资源归还
                print("等待资源归还...")
                return await self.resources.get()
    
    async def return_resource(self, resource: str):
        """归还资源"""
        await self.resources.put(resource)
        print(f"归还资源: {resource}")

async def demo_resource_pool():
    """演示资源池管理"""
    print("=" * 50)
    print("9. 资源池管理演示")
    print("=" * 50)
    
    pool = AsyncResourcePool(max_size=3)
    
    async def worker(worker_id: int):
        """使用资源池的工作者"""
        print(f"工作者 {worker_id} 请求资源")
        resource = await pool.get_resource()
        
        try:
            # 使用资源
            work_time = random.uniform(0.5, 2.0)
            print(f"工作者 {worker_id} 使用 {resource} 工作 {work_time:.2f} 秒")
            await asyncio.sleep(work_time)
            
        finally:
            # 确保资源被归还
            await pool.return_resource(resource)
            print(f"工作者 {worker_id} 完成工作")
    
    # 启动多个工作者，超过资源池大小
    await asyncio.gather(*[worker(i) for i in range(6)])
    print()

# 主函数
async def main():
    """主函数，运行所有并发控制演示"""
    print("🚀 Python异步并发控制示例\n")
    
    await demo_basic_concurrency()
    await demo_task_management()
    await demo_semaphore()
    await demo_producer_consumer()
    await demo_locks()
    await demo_events_and_conditions()
    await demo_timeout_control()
    await demo_web_crawler_simulation()
    await demo_resource_pool()
    
    print("✅ 所有并发控制示例执行完成！")

if __name__ == "__main__":
    asyncio.run(main()) 