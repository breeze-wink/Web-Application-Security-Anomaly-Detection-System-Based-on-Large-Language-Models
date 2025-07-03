"""
异步生成器示例
演示 AsyncGenerator 的用法，类似于你代码中的 capture_stream 方法
"""

import asyncio
import random
from typing import AsyncGenerator, List
from datetime import datetime

# 1. 基础异步生成器
async def simple_async_generator() -> AsyncGenerator[int, None]:
    """简单的异步生成器，产生数字序列"""
    print("异步生成器开始工作...")
    
    for i in range(5):
        # 模拟异步操作
        await asyncio.sleep(1)
        print(f"生成数字: {i}")
        yield i  # yield关键字：返回值但保持函数状态
    
    print("异步生成器工作结束")

# 2. 模拟数据流生成器（类似日志监控）
async def data_stream_generator(stream_name: str) -> AsyncGenerator[dict, None]:
    """模拟实时数据流，类似于日志文件监控"""
    print(f"开始监控数据流: {stream_name}")
    
    count = 0
    while count < 10:  # 模拟产生10条数据
        # 模拟数据到达的随机延迟
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # 生成模拟数据
        data = {
            "id": count,
            "stream": stream_name,
            "value": random.randint(1, 100),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[{stream_name}] 新数据: {data['value']}")
        yield data
        count += 1
    
    print(f"数据流 {stream_name} 结束")

# 3. 文件行读取生成器（类似于 log_capturer 的逻辑）
async def file_line_reader(filename: str) -> AsyncGenerator[str, None]:
    """异步读取文件行，模拟日志文件读取"""
    print(f"开始读取文件: {filename}")
    
    # 模拟文件内容
    lines = [
        "192.168.1.1 - - [25/Dec/2023:10:00:00 +0800] \"GET /index.php?id=1 HTTP/1.1\" 200 1234",
        "192.168.1.2 - - [25/Dec/2023:10:00:01 +0800] \"POST /login.php HTTP/1.1\" 200 567",
        "192.168.1.3 - - [25/Dec/2023:10:00:02 +0800] \"GET /admin.php?cmd=ls HTTP/1.1\" 403 89",
        "192.168.1.4 - - [25/Dec/2023:10:00:03 +0800] \"GET /search.php?q=<script> HTTP/1.1\" 200 456",
        "192.168.1.5 - - [25/Dec/2023:10:00:04 +0800] \"GET /api/users HTTP/1.1\" 200 789"
    ]
    
    for line in lines:
        # 模拟文件读取延迟
        await asyncio.sleep(0.5)
        print(f"读取到日志: {line[:50]}...")
        yield line
    
    print(f"文件 {filename} 读取完成")

# 4. 网络请求生成器
async def http_request_generator(urls: List[str]) -> AsyncGenerator[dict, None]:
    """模拟批量HTTP请求，异步生成响应"""
    print(f"开始处理 {len(urls)} 个URL...")
    
    for i, url in enumerate(urls):
        # 模拟网络请求延迟
        delay = random.uniform(1.0, 3.0)
        await asyncio.sleep(delay)
        
        # 模拟HTTP响应
        response = {
            "url": url,
            "status_code": random.choice([200, 404, 500]),
            "response_time": delay,
            "content_length": random.randint(100, 5000),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"请求完成 {i+1}/{len(urls)}: {url} -> {response['status_code']}")
        yield response

# 5. 监控系统资源生成器
async def system_monitor() -> AsyncGenerator[dict, None]:
    """模拟系统资源监控，持续生成监控数据"""
    print("开始系统监控...")
    
    monitor_count = 0
    while monitor_count < 8:  # 监控8次
        await asyncio.sleep(2)  # 每2秒监控一次
        
        # 模拟系统指标
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": random.uniform(10, 90),
            "memory_usage": random.uniform(30, 85),
            "disk_usage": random.uniform(20, 70),
            "network_io": random.randint(100, 10000)
        }
        
        print(f"系统指标: CPU={metrics['cpu_usage']:.1f}% MEM={metrics['memory_usage']:.1f}%")
        yield metrics
        monitor_count += 1
    
    print("系统监控结束")

# 6. 演示如何消费异步生成器
async def demo_simple_generator():
    """演示基础异步生成器的使用"""
    print("=" * 50)
    print("1. 基础异步生成器演示")
    print("=" * 50)
    
    # 使用 async for 循环消费异步生成器
    async for number in simple_async_generator():
        print(f"接收到数字: {number}")
    
    print()

async def demo_data_streams():
    """演示多个数据流并发处理"""
    print("=" * 50)
    print("2. 并发数据流演示")
    print("=" * 50)
    
    # 创建多个异步生成器任务
    async def process_stream(stream_name: str):
        """处理单个数据流"""
        data_count = 0
        async for data in data_stream_generator(stream_name):
            data_count += 1
            print(f"  处理来自 {stream_name} 的数据: {data['value']}")
        print(f"  流 {stream_name} 处理完成，共 {data_count} 条数据")
    
    # 并发处理多个数据流
    await asyncio.gather(
        process_stream("传感器A"),
        process_stream("传感器B"),
        process_stream("传感器C")
    )
    print()

async def demo_file_processing():
    """演示文件处理（类似日志捕获）"""
    print("=" * 50)
    print("3. 文件行处理演示（类似日志捕获）")
    print("=" * 50)
    
    line_count = 0
    async for line in file_line_reader("access.log"):
        line_count += 1
        # 简单解析日志（提取IP地址）
        ip = line.split()[0] if line.split() else "unknown"
        print(f"  处理第 {line_count} 行，IP: {ip}")
    
    print(f"文件处理完成，共处理 {line_count} 行")
    print()

async def demo_http_requests():
    """演示HTTP请求批处理"""
    print("=" * 50)
    print("4. HTTP请求批处理演示")
    print("=" * 50)
    
    urls = [
        "https://api.example.com/users",
        "https://api.example.com/products", 
        "https://api.example.com/orders",
        "https://api.github.com/repos",
        "https://httpbin.org/delay/1"
    ]
    
    success_count = 0
    error_count = 0
    
    async for response in http_request_generator(urls):
        if response["status_code"] == 200:
            success_count += 1
            print(f"  ✅ 成功: {response['url']}")
        else:
            error_count += 1
            print(f"  ❌ 失败: {response['url']} (状态码: {response['status_code']})")
    
    print(f"请求完成 - 成功: {success_count}, 失败: {error_count}")
    print()

async def demo_system_monitoring():
    """演示系统监控"""
    print("=" * 50)
    print("5. 系统监控演示")
    print("=" * 50)
    
    high_cpu_count = 0
    async for metrics in system_monitor():
        # 检查CPU使用率
        if metrics["cpu_usage"] > 70:
            high_cpu_count += 1
            print(f"  ⚠️  高CPU使用率警告: {metrics['cpu_usage']:.1f}%")
        else:
            print(f"  📊 正常: CPU={metrics['cpu_usage']:.1f}% MEM={metrics['memory_usage']:.1f}%")
    
    print(f"监控完成，共发现 {high_cpu_count} 次高CPU使用率")
    print()

# 7. 异步生成器的高级用法：带有控制的生成器
class AsyncDataProducer:
    """可控制的异步数据生产者"""
    
    def __init__(self):
        self.is_running = False
        self.data_count = 0
    
    async def start_production(self) -> AsyncGenerator[dict, None]:
        """开始数据生产"""
        self.is_running = True
        print("数据生产者启动...")
        
        while self.is_running and self.data_count < 15:
            await asyncio.sleep(0.8)
            
            data = {
                "id": self.data_count,
                "value": random.randint(1, 1000),
                "timestamp": datetime.now().isoformat()
            }
            
            self.data_count += 1
            print(f"生产数据 #{self.data_count}: {data['value']}")
            yield data
        
        print("数据生产结束")
    
    def stop_production(self):
        """停止数据生产"""
        self.is_running = False
        print("收到停止信号...")

async def demo_controlled_generator():
    """演示可控制的异步生成器"""
    print("=" * 50)
    print("6. 可控制的异步生成器演示")
    print("=" * 50)
    
    producer = AsyncDataProducer()
    
    # 创建一个任务来模拟外部停止信号
    async def stop_after_delay():
        await asyncio.sleep(10)  # 10秒后停止
        producer.stop_production()
    
    # 同时运行数据生产和停止任务
    stop_task = asyncio.create_task(stop_after_delay())
    
    collected_data = []
    async for data in producer.start_production():
        collected_data.append(data)
        if len(collected_data) >= 10:  # 收集够10条数据就停止
            producer.stop_production()
            break
    
    # 取消停止任务（如果还在运行）
    stop_task.cancel()
    
    print(f"共收集到 {len(collected_data)} 条数据")
    print()

# 主函数
async def main():
    """主函数，运行所有演示"""
    print("🚀 Python异步生成器示例\n")
    
    await demo_simple_generator()
    await demo_data_streams() 
    await demo_file_processing()
    await demo_http_requests()
    await demo_system_monitoring()
    await demo_controlled_generator()
    
    print("✅ 所有异步生成器示例执行完成！")

if __name__ == "__main__":
    asyncio.run(main()) 