"""从日志文件捕获HTTP请求"""

import asyncio
import aiofiles
import re
from typing import AsyncGenerator, Optional
from datetime import datetime
from .base import BaseCapturer
from app.core.models import HTTPRequest
from app.core.exceptions import CaptureException

class LogFileCapturer(BaseCapturer):
    """从日志文件捕获HTTP请求"""
    
    def __init__(self, log_file_path: str, follow: bool = False):
        super().__init__()
        self.log_file_path = log_file_path
        self.follow = follow  # 是否跟踪新写入的日志
        self.file_position = 0
        
    async def capture_single(self) -> Optional[HTTPRequest]:
        """捕获单个HTTP请求"""
        try:
            async with aiofiles.open(self.log_file_path, 'r') as f:
                await f.seek(self.file_position)
                line = await f.readline()
                if line:
                    self.file_position = await f.tell()
                    return self._parse_log_line(line.strip())
                return None
        except Exception as e:
            raise CaptureException(f"读取日志文件失败: {e}")
    
    async def capture_stream(self) -> AsyncGenerator[HTTPRequest, None]:
        """捕获HTTP请求流"""
        try:
            async with aiofiles.open(self.log_file_path, 'r') as f:
                # 移动到文件末尾（如果是跟踪模式）
                if self.follow:
                    await f.seek(0, 2)  # 移动到文件末尾
                else:
                    await f.seek(self.file_position)
                
                while self.is_running:
                    line = await f.readline()
                    if line:
                        request = self._parse_log_line(line.strip())
                        if request:
                            yield request
                    else:
                        if not self.follow:
                            break
                        # 等待新数据
                        await asyncio.sleep(0.1)
        except Exception as e:
            raise CaptureException(f"读取日志流失败: {e}")
    
    async def start_capture(self):
        """开始捕获"""
        self.is_running = True
        
    async def stop_capture(self):
        """停止捕获"""
        self.is_running = False
    
    def _parse_log_line(self, line: str) -> Optional[HTTPRequest]:
        """解析日志行
        
        支持常见的Web服务器日志格式:
        - Apache Combined Log Format
        - Nginx访问日志
        """
        # 简化的日志解析正则 (Apache Combined Log Format)
        # 192.168.1.1 - - [25/Dec/2023:10:00:00 +0800] "GET /index.php?id=1 HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0..."
        pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+) "([^"]*)" "([^"]*)"'
        
        match = re.match(pattern, line)
        if not match:
            return None
            
        try:
            source_ip = match.group(1)
            timestamp_str = match.group(2)
            method = match.group(3)
            url = match.group(4)
            status_code = match.group(5)
            response_size = match.group(6)
            referer = match.group(7)
            user_agent = match.group(8)
            
            # 解析时间戳
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            
            # 解析URL和参数
            url_parts = url.split('?', 1)
            base_url = url_parts[0]
            params = {}
            if len(url_parts) > 1:
                params = self._parse_query_string(url_parts[1])
            
            return HTTPRequest(
                url=url,
                method=method,
                headers={'User-Agent': user_agent, 'Referer': referer},
                params=params,
                body=None,
                source_ip=source_ip,
                timestamp=timestamp,
                raw_data=line,
                user_agent=user_agent
            )
        except Exception as e:
            # 解析失败时返回None，不抛出异常
            return None
    
    def _parse_query_string(self, query_string: str) -> dict:
        """解析查询字符串"""
        params = {}
        if not query_string:
            return params
            
        for pair in query_string.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
            else:
                params[pair] = ''
        return params 