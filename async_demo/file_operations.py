"""
异步文件操作示例
演示 aiofiles 的用法，类似于你代码中的异步文件读取
"""

import asyncio
import aiofiles
import aiofiles.os
import os
from typing import List, AsyncGenerator
from datetime import datetime

# 1. 基础异步文件读写
async def demo_basic_file_operations():
    """演示基础的异步文件读写操作"""
    print("=" * 50)
    print("1. 基础异步文件操作演示")
    print("=" * 50)
    
    filename = "async_demo_test.txt"
    
    # 异步写入文件
    print("正在异步写入文件...")
    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.write("这是第一行内容\n")
        await f.write("这是第二行内容\n")
        await f.write("这是第三行内容\n")
        # 模拟写入延迟
        await asyncio.sleep(0.5)
        await f.write("这是延迟写入的内容\n")
    
    print("文件写入完成！")
    
    # 异步读取整个文件
    print("\n正在异步读取整个文件...")
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
        print("文件内容:")
        print(content)
    
    # 异步按行读取
    print("正在异步按行读取文件...")
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        line_number = 1
        async for line in f:  # aiofiles支持异步迭代
            print(f"第 {line_number} 行: {line.strip()}")
            line_number += 1
            await asyncio.sleep(0.2)  # 模拟处理延迟
    
    # 清理测试文件
    await aiofiles.os.remove(filename)
    print(f"已删除测试文件: {filename}")
    print()

# 2. 模拟日志文件实时监控（类似 log_capturer）
async def simulate_log_monitoring():
    """模拟实时日志监控，类似于log_capturer的follow模式"""
    print("=" * 50)
    print("2. 日志文件实时监控演示")
    print("=" * 50)
    
    log_file = "demo_access.log"
    
    # 创建模拟日志文件
    sample_logs = [
        '192.168.1.1 - - [25/Dec/2023:10:00:00 +0800] "GET /index.php?id=1 HTTP/1.1" 200 1234',
        '192.168.1.2 - - [25/Dec/2023:10:00:01 +0800] "POST /login.php HTTP/1.1" 200 567',
        '192.168.1.3 - - [25/Dec/2023:10:00:02 +0800] "GET /admin.php?cmd=ls HTTP/1.1" 403 89',
        '192.168.1.4 - - [25/Dec/2023:10:00:03 +0800] "GET /search.php?q=<script> HTTP/1.1" 200 456',
        '192.168.1.5 - - [25/Dec/2023:10:00:04 +0800] "GET /api/users HTTP/1.1" 200 789'
    ]
    
    # 异步写入初始日志
    async with aiofiles.open(log_file, 'w', encoding='utf-8') as f:
        for log in sample_logs:
            await f.write(log + '\n')
    
    print(f"已创建模拟日志文件: {log_file}")
    
    # 模拟日志监控器
    async def log_monitor():
        """监控日志文件的新内容"""
        print("开始监控日志文件...")
        file_position = 0
        
        # 监控5轮
        for round_num in range(5):
            async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                # 移动到上次读取位置
                await f.seek(file_position)
                
                # 读取新内容
                new_content = await f.read()
                if new_content:
                    lines = new_content.strip().split('\n')
                    for line in lines:
                        if line:  # 忽略空行
                            ip = line.split()[0] if line.split() else "unknown"
                            print(f"  监控到新日志: IP={ip}")
                
                # 更新文件位置
                file_position = await f.tell()
            
            # 等待新数据
            await asyncio.sleep(2)
        
        print("日志监控结束")
    
    # 模拟新日志写入
    async def log_writer():
        """模拟新日志写入"""
        await asyncio.sleep(1)  # 稍等一下再开始写入
        
        new_logs = [
            '192.168.1.6 - - [25/Dec/2023:10:00:05 +0800] "GET /dashboard HTTP/1.1" 200 2345',
            '192.168.1.7 - - [25/Dec/2023:10:00:06 +0800] "POST /api/data HTTP/1.1" 201 678',
            '192.168.1.8 - - [25/Dec/2023:10:00:07 +0800] "DELETE /admin/users/1 HTTP/1.1" 403 123'
        ]
        
        for i, log in enumerate(new_logs):
            await asyncio.sleep(3)  # 每3秒写入一条新日志
            async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
                await f.write(log + '\n')
            print(f"写入新日志 {i+1}: {log[:30]}...")
    
    # 并发运行监控和写入
    await asyncio.gather(log_monitor(), log_writer())
    
    # 清理测试文件
    await aiofiles.os.remove(log_file)
    print(f"已删除测试日志文件: {log_file}")
    print()

# 3. 批量文件处理
async def demo_batch_file_processing():
    """演示批量异步文件处理"""
    print("=" * 50)
    print("3. 批量文件处理演示")
    print("=" * 50)
    
    # 创建多个测试文件
    test_files = []
    for i in range(5):
        filename = f"test_file_{i}.txt"
        test_files.append(filename)
        
        # 异步创建文件
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            content = f"这是测试文件 {i}\n"
            content += f"创建时间: {datetime.now()}\n"
            content += f"文件大小: {len(content)} 字节\n"
            for j in range(10):
                content += f"数据行 {j}: {j * i}\n"
            await f.write(content)
    
    print(f"已创建 {len(test_files)} 个测试文件")
    
    # 并发读取所有文件
    async def read_file_info(filename: str) -> dict:
        """读取单个文件的信息"""
        async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
            content = await f.read()
            line_count = len(content.split('\n'))
            char_count = len(content)
            
            # 模拟文件处理延迟
            await asyncio.sleep(0.5)
            
            return {
                "filename": filename,
                "lines": line_count,
                "characters": char_count,
                "size_bytes": len(content.encode('utf-8'))
            }
    
    print("开始并发读取文件信息...")
    start_time = asyncio.get_event_loop().time()
    
    # 并发处理所有文件
    file_infos = await asyncio.gather(*[read_file_info(f) for f in test_files])
    
    end_time = asyncio.get_event_loop().time()
    
    print("文件信息统计:")
    total_size = 0
    for info in file_infos:
        print(f"  {info['filename']}: {info['lines']} 行, {info['characters']} 字符, {info['size_bytes']} 字节")
        total_size += info['size_bytes']
    
    print(f"总大小: {total_size} 字节")
    print(f"并发处理耗时: {end_time - start_time:.2f} 秒")
    
    # 清理测试文件
    for filename in test_files:
        await aiofiles.os.remove(filename)
    print("已清理所有测试文件")
    print()

# 4. 大文件流式处理
async def demo_large_file_streaming():
    """演示大文件的流式处理"""
    print("=" * 50)
    print("4. 大文件流式处理演示")
    print("=" * 50)
    
    large_file = "large_test_file.txt"
    
    # 创建一个模拟的大文件
    print("正在创建大文件...")
    async with aiofiles.open(large_file, 'w', encoding='utf-8') as f:
        for i in range(1000):  # 1000行数据
            line = f"数据行 {i:04d}: {'A' * 50} - 时间戳 {datetime.now()}\n"
            await f.write(line)
            
            # 每100行输出一次进度
            if i % 100 == 0:
                print(f"  已写入 {i} 行...")
                await asyncio.sleep(0.01)  # 避免阻塞
    
    print(f"大文件创建完成: {large_file}")
    
    # 流式读取和处理
    async def stream_process_file():
        """流式处理文件，避免内存占用过大"""
        print("开始流式处理文件...")
        
        line_count = 0
        total_chars = 0
        
        async with aiofiles.open(large_file, 'r', encoding='utf-8') as f:
            async for line in f:
                line_count += 1
                total_chars += len(line)
                
                # 每100行处理一次统计
                if line_count % 100 == 0:
                    print(f"  已处理 {line_count} 行，累计 {total_chars} 字符")
                    await asyncio.sleep(0.01)  # 让出控制权
        
        print(f"流式处理完成: 总共 {line_count} 行，{total_chars} 字符")
    
    await stream_process_file()
    
    # 获取文件统计信息
    stat = await aiofiles.os.stat(large_file)
    print(f"文件大小: {stat.st_size} 字节")
    
    # 清理大文件
    await aiofiles.os.remove(large_file)
    print(f"已删除大文件: {large_file}")
    print()

# 5. 文件变化监控（类似tail -f）
async def demo_file_tail_follow():
    """演示文件追踪功能，类似于 tail -f"""
    print("=" * 50)
    print("5. 文件追踪演示（类似 tail -f）")
    print("=" * 50)
    
    follow_file = "follow_demo.log"
    
    # 创建初始文件
    async with aiofiles.open(follow_file, 'w', encoding='utf-8') as f:
        await f.write("初始日志内容\n")
    
    # 文件跟踪器
    async def file_follower():
        """跟踪文件新增内容"""
        print("开始跟踪文件...")
        
        async with aiofiles.open(follow_file, 'r', encoding='utf-8') as f:
            # 移动到文件末尾
            await f.seek(0, 2)  # 2表示从文件末尾开始
            
            # 持续监控新内容
            follow_count = 0
            while follow_count < 10:  # 监控10轮
                line = await f.readline()
                if line:
                    print(f"  [跟踪] 新内容: {line.strip()}")
                else:
                    await asyncio.sleep(0.5)  # 没有新内容时等待
                follow_count += 1
    
    # 内容写入器
    async def content_writer():
        """定期写入新内容"""
        await asyncio.sleep(1)  # 等待跟踪器启动
        
        for i in range(5):
            await asyncio.sleep(2)
            async with aiofiles.open(follow_file, 'a', encoding='utf-8') as f:
                new_line = f"新增日志 {i}: {datetime.now()}\n"
                await f.write(new_line)
            print(f"写入新内容 {i}")
    
    # 并发运行跟踪和写入
    await asyncio.gather(file_follower(), content_writer())
    
    # 清理文件
    await aiofiles.os.remove(follow_file)
    print(f"已删除跟踪文件: {follow_file}")
    print()

# 6. 异步文件搜索
async def demo_async_file_search():
    """演示异步文件内容搜索"""
    print("=" * 50)
    print("6. 异步文件搜索演示")
    print("=" * 50)
    
    # 创建包含搜索内容的测试文件
    search_files = []
    keywords = ["error", "warning", "success", "info"]
    
    for i in range(3):
        filename = f"search_test_{i}.log"
        search_files.append(filename)
        
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            for j in range(20):
                import random
                keyword = random.choice(keywords)
                line = f"[{datetime.now()}] {keyword.upper()}: 这是第 {j} 条{keyword}日志\n"
                await f.write(line)
    
    print(f"已创建 {len(search_files)} 个搜索测试文件")
    
    # 异步搜索函数
    async def search_in_file(filename: str, keyword: str) -> List[str]:
        """在单个文件中搜索关键字"""
        matches = []
        line_number = 0
        
        async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
            async for line in f:
                line_number += 1
                if keyword.lower() in line.lower():
                    matches.append(f"{filename}:{line_number}: {line.strip()}")
                await asyncio.sleep(0.01)  # 避免阻塞
        
        return matches
    
    # 并发搜索所有文件
    search_keyword = "error"
    print(f"搜索关键字: '{search_keyword}'")
    
    search_tasks = [search_in_file(f, search_keyword) for f in search_files]
    all_matches = await asyncio.gather(*search_tasks)
    
    # 汇总结果
    total_matches = []
    for matches in all_matches:
        total_matches.extend(matches)
    
    print(f"搜索结果 (共找到 {len(total_matches)} 条匹配):")
    for match in total_matches[:5]:  # 只显示前5条
        print(f"  {match}")
    
    if len(total_matches) > 5:
        print(f"  ... 还有 {len(total_matches) - 5} 条结果")
    
    # 清理搜索文件
    for filename in search_files:
        await aiofiles.os.remove(filename)
    print("已清理搜索测试文件")
    print()

# 主函数
async def main():
    """主函数，运行所有文件操作演示"""
    print("🚀 Python异步文件操作示例\n")
    
    await demo_basic_file_operations()
    await simulate_log_monitoring()
    await demo_batch_file_processing()
    await demo_large_file_streaming()
    await demo_file_tail_follow()
    await demo_async_file_search()
    
    print("✅ 所有异步文件操作示例执行完成！")

if __name__ == "__main__":
    asyncio.run(main()) 