"""
LogFileCapturer 功能测试
测试日志文件捕获器的各项功能
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import AsyncMock, patch
import aiofiles

# 添加app路径到Python路径，以便导入模块
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.capture.log_capturer import LogFileCapturer
from app.core.models import HTTPRequest
from app.core.exceptions import CaptureException


class TestLogFileCapturer:
    """LogFileCapturer测试类"""
    
    @pytest.fixture
    def sample_log_lines(self):
        """提供测试用的日志行样本"""
        return [
            # 标准Apache Combined Log Format
            '192.168.1.100 - - [25/Dec/2023:10:00:00 +0800] "GET /index.php?id=1&name=test HTTP/1.1" 200 1234 "http://example.com/refer" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"',
            
            # POST请求
            '10.0.0.1 - admin [25/Dec/2023:10:01:30 +0800] "POST /admin/login.php HTTP/1.1" 302 0 "http://example.com/admin" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"',
            
            # 带SQL注入尝试的GET请求
            '192.168.1.50 - - [25/Dec/2023:10:02:15 +0800] "GET /search.php?q=\' OR 1=1-- HTTP/1.1" 200 2048 "-" "sqlmap/1.6.12"',
            
            # XSS尝试
            '203.0.113.10 - - [25/Dec/2023:10:03:00 +0800] "GET /comment.php?msg=<script>alert(1)</script> HTTP/1.1" 200 512 "http://evil.com" "curl/7.68.0"',
            
            # 404错误
            '192.168.1.200 - - [25/Dec/2023:10:04:45 +0800] "GET /nonexistent.php HTTP/1.1" 404 169 "-" "Bot/1.0"'
        ]
    
    @pytest.fixture
    async def temp_log_file(self, sample_log_lines):
        """创建临时日志文件用于测试"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            for line in sample_log_lines:
                f.write(line + '\n')
            temp_path = f.name
        
        yield temp_path
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def static_log_file(self):
        """使用静态样本日志文件进行测试"""
        log_file_path = os.path.join(os.path.dirname(__file__), 'sample_logs', 'access.log')
        if not os.path.exists(log_file_path):
            pytest.skip(f"静态日志文件不存在: {log_file_path}")
        return log_file_path
    
    @pytest.fixture
    def capturer(self, temp_log_file):
        """创建LogFileCapturer实例（使用临时文件）"""
        return LogFileCapturer(temp_log_file, follow=False)
    
    @pytest.fixture
    def static_capturer(self, static_log_file):
        """创建LogFileCapturer实例（使用静态文件）"""
        return LogFileCapturer(static_log_file, follow=False)
    
    def test_parse_query_string(self):
        """测试查询字符串解析功能"""
        capturer = LogFileCapturer("/dummy/path")
        
        # 测试标准查询参数
        result = capturer._parse_query_string("id=1&name=test&page=2")
        expected = {"id": "1", "name": "test", "page": "2"}
        assert result == expected
        
        # 测试空查询字符串
        result = capturer._parse_query_string("")
        assert result == {}
        
        # 测试包含特殊字符的参数
        result = capturer._parse_query_string("q=' OR 1=1--&action=search")
        expected = {"q": "' OR 1=1--", "action": "search"}
        assert result == expected
        
        # 测试没有值的参数
        result = capturer._parse_query_string("debug&verbose&id=1")
        expected = {"debug": "", "verbose": "", "id": "1"}
        assert result == expected
        
        # 测试值中包含等号的情况
        result = capturer._parse_query_string("math=2+2=4&simple=test")
        expected = {"math": "2+2=4", "simple": "test"}
        assert result == expected

    def test_parse_log_line_success(self):
        """测试成功解析日志行"""
        capturer = LogFileCapturer("/dummy/path")
        
        # 测试标准GET请求
        log_line = '192.168.1.100 - - [25/Dec/2023:10:00:00 +0800] "GET /index.php?id=1&name=test HTTP/1.1" 200 1234 "http://example.com/refer" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"'
        
        request = capturer._parse_log_line(log_line)
        
        assert request is not None
        assert isinstance(request, HTTPRequest)
        assert request.method == "GET"
        assert request.url == "/index.php?id=1&name=test"
        assert request.source_ip == "192.168.1.100"
        assert request.params == {"id": "1", "name": "test"}
        assert request.headers["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        assert request.headers["Referer"] == "http://example.com/refer"
        assert request.raw_data == log_line
        
        # 验证时间戳解析
        expected_time = datetime.strptime('25/Dec/2023:10:00:00 +0800', '%d/%b/%Y:%H:%M:%S %z')
        assert request.timestamp == expected_time

    def test_parse_log_line_with_sql_injection(self):
        """测试解析包含SQL注入的日志行"""
        capturer = LogFileCapturer("/dummy/path")
        
        log_line = '192.168.1.50 - - [25/Dec/2023:10:02:15 +0800] "GET /search.php?q=\' OR 1=1-- HTTP/1.1" 200 2048 "-" "sqlmap/1.6.12"'
        
        request = capturer._parse_log_line(log_line)
        
        assert request is not None
        assert request.method == "GET"
        assert request.url == "/search.php?q=' OR 1=1--"
        assert request.params == {"q": "' OR 1=1--"}
        assert request.user_agent == "sqlmap/1.6.12"

    def test_parse_log_line_with_xss(self):
        """测试解析包含XSS的日志行"""
        capturer = LogFileCapturer("/dummy/path")
        
        log_line = '203.0.113.10 - - [25/Dec/2023:10:03:00 +0800] "GET /comment.php?msg=<script>alert(1)</script> HTTP/1.1" 200 512 "http://evil.com" "curl/7.68.0"'
        
        request = capturer._parse_log_line(log_line)
        
        assert request is not None
        assert request.method == "GET"
        assert request.params == {"msg": "<script>alert(1)</script>"}

    def test_parse_log_line_invalid_format(self):
        """测试解析无效格式的日志行"""
        capturer = LogFileCapturer("/dummy/path")
        
        # 无效的日志格式
        invalid_lines = [
            "这不是一个有效的日志行",
            "192.168.1.1 invalid format",
            "",
            "GET /index.php HTTP/1.1"  # 缺少其他字段
        ]
        
        for invalid_line in invalid_lines:
            result = capturer._parse_log_line(invalid_line)
            assert result is None

    @pytest.mark.asyncio
    async def test_capture_single_success(self, capturer, temp_log_file):
        """测试成功捕获单个请求"""
        # 启动捕获器
        await capturer.start_capture()
        
        # 捕获第一个请求
        request = await capturer.capture_single()
        
        assert request is not None
        assert isinstance(request, HTTPRequest)
        assert request.method == "GET"
        assert request.url == "/index.php?id=1&name=test"
        assert request.source_ip == "192.168.1.100"
        
        # 捕获第二个请求
        request2 = await capturer.capture_single()
        assert request2 is not None
        assert request2.method == "POST"
        assert request2.url == "/admin/login.php"

    @pytest.mark.asyncio
    async def test_capture_single_end_of_file(self, temp_log_file):
        """测试文件读取完毕的情况"""
        capturer = LogFileCapturer(temp_log_file, follow=False)
        await capturer.start_capture()
        
        # 读取所有行
        requests = []
        while True:
            request = await capturer.capture_single()
            if request is None:
                break
            requests.append(request)
        
        # 应该捕获到5个请求（对应sample_log_lines中的5行）
        assert len(requests) == 5
        
        # 再次尝试读取应该返回None
        request = await capturer.capture_single()
        assert request is None

    @pytest.mark.asyncio
    async def test_capture_single_file_not_found(self):
        """测试文件不存在的情况"""
        capturer = LogFileCapturer("/nonexistent/file.log", follow=False)
        await capturer.start_capture()
        
        with pytest.raises(CaptureException) as exc_info:
            await capturer.capture_single()
        
        assert "读取日志文件失败" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_capture_stream_batch_mode(self, capturer, temp_log_file):
        """测试批量模式的流式捕获"""
        await capturer.start_capture()
        
        requests = []
        async for request in capturer.capture_stream():
            requests.append(request)
        
        # 应该捕获到所有有效的请求
        assert len(requests) == 5
        
        # 验证第一个请求
        first_request = requests[0]
        assert first_request.method == "GET"
        assert first_request.source_ip == "192.168.1.100"
        
        # 验证包含SQL注入的请求
        sql_injection_request = requests[2]
        assert "' OR 1=1--" in sql_injection_request.url

    @pytest.mark.asyncio
    async def test_capture_stream_follow_mode(self, temp_log_file):
        """测试实时跟踪模式（简化版）"""
        capturer = LogFileCapturer(temp_log_file, follow=True)
        await capturer.start_capture()
        
        # 创建一个任务来捕获流
        requests = []
        
        async def capture_task():
            count = 0
            async for request in capturer.capture_stream():
                requests.append(request)
                count += 1
                if count >= 3:  # 只捕获前3个请求然后停止
                    await capturer.stop_capture()
                    break
        
        # 运行捕获任务，设置超时防止无限等待
        try:
            await asyncio.wait_for(capture_task(), timeout=2.0)
        except asyncio.TimeoutError:
            await capturer.stop_capture()
        
        # 应该至少捕获到一些请求
        assert len(requests) > 0

    @pytest.mark.asyncio
    async def test_start_stop_capture(self, capturer):
        """测试启动和停止捕获功能"""
        # 初始状态
        assert not capturer.is_running
        
        # 启动捕获
        await capturer.start_capture()
        assert capturer.is_running
        
        # 停止捕获
        await capturer.stop_capture()
        assert not capturer.is_running

    @pytest.mark.asyncio
    async def test_file_position_tracking(self, temp_log_file):
        """测试文件位置跟踪功能"""
        capturer = LogFileCapturer(temp_log_file, follow=False)
        await capturer.start_capture()
        
        # 初始位置应该是0
        assert capturer.file_position == 0
        
        # 读取第一行
        request1 = await capturer.capture_single()
        assert request1 is not None
        
        # 位置应该已经更新
        first_position = capturer.file_position
        assert first_position > 0
        
        # 读取第二行
        request2 = await capturer.capture_single()
        assert request2 is not None
        
        # 位置应该继续增加
        second_position = capturer.file_position
        assert second_position > first_position

    def test_initialization(self, temp_log_file):
        """测试初始化参数"""
        # 测试默认参数
        capturer1 = LogFileCapturer(temp_log_file)
        assert capturer1.log_file_path == temp_log_file
        assert capturer1.follow == False
        assert capturer1.file_position == 0
        
        # 测试自定义参数
        capturer2 = LogFileCapturer(temp_log_file, follow=True)
        assert capturer2.follow == True

    @pytest.mark.asyncio
    async def test_concurrent_capture_single(self, capturer, temp_log_file):
        """测试并发调用capture_single的情况"""
        await capturer.start_capture()
        
        # 并发执行多个capture_single调用
        tasks = [capturer.capture_single() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # 确保所有调用都成功返回
        valid_results = [r for r in results if r is not None]
        assert len(valid_results) >= 1  # 至少应该有一个有效结果

    # ================================
    # 静态文件测试部分
    # ================================
    
    @pytest.mark.asyncio
    async def test_static_file_capture_single(self, static_capturer):
        """测试使用静态样本文件的单个请求捕获"""
        await static_capturer.start_capture()
        
        # 捕获第一个请求
        request = await static_capturer.capture_single()
        
        assert request is not None
        assert isinstance(request, HTTPRequest)
        print(f"📄 静态文件捕获: {request.method} {request.url} from {request.source_ip}")
        
        # 捕获第二个请求
        request2 = await static_capturer.capture_single()
        assert request2 is not None
        print(f"📄 静态文件捕获: {request2.method} {request2.url} from {request2.source_ip}")

    @pytest.mark.asyncio
    async def test_static_file_capture_stream(self, static_capturer):
        """测试使用静态样本文件的流式捕获"""
        await static_capturer.start_capture()
        
        requests = []
        count = 0
        async for request in static_capturer.capture_stream():
            requests.append(request)
            count += 1
            print(f"📄 静态文件流式捕获 #{count}: {request.method} {request.url}")
            
            # 限制捕获数量避免无限循环
            if count >= 10:
                break
        
        # 应该捕获到一些请求
        assert len(requests) > 0
        print(f"📊 总共从静态文件捕获了 {len(requests)} 个请求")

    def test_static_vs_dynamic_comparison(self, static_log_file, temp_log_file):
        """对比静态文件和动态文件的区别"""
        # 静态文件路径
        print(f"📄 静态文件路径: {static_log_file}")
        print(f"📄 静态文件存在: {os.path.exists(static_log_file)}")
        
        # 动态文件路径
        print(f"🔄 动态文件路径: {temp_log_file}")
        print(f"🔄 动态文件存在: {os.path.exists(temp_log_file)}")
        
        # 检查文件大小
        if os.path.exists(static_log_file):
            static_size = os.path.getsize(static_log_file)
            print(f"📏 静态文件大小: {static_size} bytes")
        
        if os.path.exists(temp_log_file):
            temp_size = os.path.getsize(temp_log_file)
            print(f"📏 动态文件大小: {temp_size} bytes")
        
        # 两个文件都应该存在
        assert os.path.exists(static_log_file), "静态样本文件应该存在"
        assert os.path.exists(temp_log_file), "动态临时文件应该存在"

    @pytest.mark.asyncio
    async def test_real_world_log_parsing(self, static_capturer):
        """测试真实世界的日志解析能力（使用静态文件）"""
        await static_capturer.start_capture()
        
        # 统计不同类型的请求
        request_stats = {
            'GET': 0,
            'POST': 0,
            'PUT': 0,
            'other': 0,
            'potential_attacks': []
        }
        
        count = 0
        async for request in static_capturer.capture_stream():
            count += 1
            
            # 统计请求方法
            method = request.method.upper()
            if method in request_stats:
                request_stats[method] += 1
            else:
                request_stats['other'] += 1
            
            # 检查潜在的攻击模式
            url_lower = request.url.lower()
            if any(pattern in url_lower for pattern in ['script', 'or 1=1', '../', 'passwd', 'admin']):
                request_stats['potential_attacks'].append({
                    'url': request.url,
                    'method': request.method,
                    'source_ip': request.source_ip,
                    'user_agent': request.user_agent
                })
            
            # 限制处理数量
            if count >= 20:
                break
        
        # 输出统计结果
        print("\n📊 真实日志文件分析结果:")
        print(f"   总请求数: {count}")
        print(f"   GET请求: {request_stats['GET']}")
        print(f"   POST请求: {request_stats['POST']}")
        print(f"   PUT请求: {request_stats['PUT']}")
        print(f"   其他请求: {request_stats['other']}")
        print(f"   潜在攻击: {len(request_stats['potential_attacks'])}")
        
        if request_stats['potential_attacks']:
            print("\n🚨 发现潜在攻击:")
            for attack in request_stats['potential_attacks']:
                print(f"   - {attack['method']} {attack['url']} from {attack['source_ip']}")
        
        # 应该至少处理了一些请求
        assert count > 0, "应该从静态文件中读取到请求"


if __name__ == "__main__":
    # 运行测试的简单方法
    import subprocess
    import sys
    
    print("正在运行 LogFileCapturer 功能测试...")
    
    # 使用pytest运行测试
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v",  # 详细输出
        "--tb=short"  # 简短的错误追踪
    ], capture_output=True, text=True)
    
    print("测试输出:")
    print(result.stdout)
    if result.stderr:
        print("错误信息:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("✅ 所有测试通过!")
    else:
        print("❌ 某些测试失败")
        
    sys.exit(result.returncode) 