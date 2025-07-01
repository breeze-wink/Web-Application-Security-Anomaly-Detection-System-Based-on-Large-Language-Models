"""从日志文件捕获HTTP请求"""

import asyncio  # Python异步编程库，用于处理并发任务
import aiofiles  # 异步文件操作库，可以非阻塞地读写文件
import re  # 正则表达式库，用于模式匹配和文本解析
from typing import AsyncGenerator, Optional  # 类型提示，帮助IDE和开发者理解函数参数和返回值类型
from datetime import datetime  # 日期时间处理库
from .base import BaseCapturer  # 导入基础捕获器类
from app.core.models import HTTPRequest  # HTTP请求数据模型
from app.core.exceptions import CaptureException  # 自定义异常类

class LogFileCapturer(BaseCapturer):
    """从日志文件捕获HTTP请求
    
    这个类专门用于从Web服务器的访问日志文件中读取和解析HTTP请求
    支持实时监控模式和批量读取模式
    """
    
    def __init__(self, log_file_path: str, follow: bool = False):
        """初始化日志文件捕获器
        
        Args:
            log_file_path: 日志文件的完整路径
            follow: 是否启用实时跟踪模式（类似tail -f命令）
        """
        super().__init__()  # 调用父类的初始化方法
        self.log_file_path = log_file_path  # 保存日志文件路径
        self.follow = follow  # 是否跟踪新写入的日志（实时监控）
        self.file_position = 0  # 记录文件读取位置，避免重复读取同一行
        
    async def capture_single(self) -> Optional[HTTPRequest]:
        """捕获单个HTTP请求
        
        从日志文件中读取一行，解析为HTTPRequest对象
        这是一个异步函数，不会阻塞主程序
        
        Returns:
            HTTPRequest对象或None（如果没有更多数据或解析失败）
        """
        try:
            # 使用aiofiles异步打开文件，避免阻塞
            async with aiofiles.open(self.log_file_path, 'r') as f:
                # 移动文件指针到上次读取的位置
                # seek()方法用于定位文件指针，类似书签的作用
                await f.seek(self.file_position)
                
                # 异步读取一行文本
                # readline()读取到换行符为止的一行
                line = await f.readline()
                
                if line:  # 如果成功读取到内容
                    # 更新文件位置，tell()返回当前文件指针位置
                    self.file_position = await f.tell()
                    # 解析这一行日志，strip()去除首尾空白字符
                    return self._parse_log_line(line.strip())
                return None  # 文件已读取完毕
        except Exception as e:
            # 捕获所有异常并转换为自定义异常类型
            raise CaptureException(f"读取日志文件失败: {e}")
    
    async def capture_stream(self) -> AsyncGenerator[HTTPRequest, None]:
        """捕获HTTP请求流
        
        持续监控日志文件，实时获取新的HTTP请求
        这是一个异步生成器函数，可以逐个产生结果
        
        Yields:
            HTTPRequest: 解析成功的HTTP请求对象
        """
        try:
            # 异步打开日志文件
            async with aiofiles.open(self.log_file_path, 'r') as f:
                # 根据模式设置初始读取位置
                if self.follow:
                    # 实时模式：移动到文件末尾，只读取新增内容
                    # seek(0, 2)：0是偏移量，2表示从文件末尾开始
                    await f.seek(0, 2)
                else:
                    # 批量模式：从上次读取位置继续
                    await f.seek(self.file_position)
                
                # 持续循环读取，直到停止信号
                while self.is_running:
                    # 读取一行日志
                    line = await f.readline()
                    
                    if line:  # 如果读取到内容
                        # 解析日志行为HTTPRequest对象
                        request = self._parse_log_line(line.strip())
                        if request:
                            # yield关键字：生成器函数的核心
                            # 它会返回一个值，但保持函数状态，等待下次调用
                            yield request
                    else:  # 没有读取到新内容
                        if not self.follow:
                            # 批量模式：文件读完就退出
                            break
                        # 实时模式：等待新数据写入
                        # asyncio.sleep()异步等待，不阻塞其他协程
                        await asyncio.sleep(0.1)
        except Exception as e:
            raise CaptureException(f"读取日志流失败: {e}")
    
    async def start_capture(self):
        """开始捕获
        
        设置运行标志，启动捕获过程
        """
        self.is_running = True
        
    async def stop_capture(self):
        """停止捕获
        
        清除运行标志，停止捕获过程
        """
        self.is_running = False
    
    def _parse_log_line(self, line: str) -> Optional[HTTPRequest]:
        """解析日志行
        
        将一行Web服务器日志解析为结构化的HTTPRequest对象
        支持常见的Web服务器日志格式:
        - Apache Combined Log Format
        - Nginx访问日志
        
        日志格式示例：
        192.168.1.1 - - [25/Dec/2023:10:00:00 +0800] "GET /index.php?id=1 HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0..."
        
        Args:
            line: 一行日志文本
            
        Returns:
            解析成功返回HTTPRequest对象，失败返回None
        """
        # 定义正则表达式模式，用于匹配Apache Combined Log Format
        # 正则表达式分组说明：
        # (\S+) - 第1组：客户端IP地址（非空白字符）
        # \S+ - 远程用户标识（忽略）
        # \S+ - 认证用户名（忽略）
        # \[([^\]]+)\] - 第2组：请求时间戳，[]包围的内容
        # "(\S+) (\S+) \S+" - 第3,4组：HTTP方法和URL路径
        # (\d+) - 第5组：HTTP状态码（数字）
        # (\d+) - 第6组：响应大小（数字）
        # "([^"]*)" - 第7组：引用页面（Referer）
        # "([^"]*)" - 第8组：用户代理字符串
        pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+) "([^"]*)" "([^"]*)"'
        
        # 使用正则表达式匹配日志行
        match = re.match(pattern, line)
        if not match:
            # 如果不匹配，说明日志格式不正确
            return None
            
        try:
            # 从正则匹配结果中提取各个字段
            source_ip = match.group(1)     # 客户端IP地址
            timestamp_str = match.group(2) # 时间戳字符串
            method = match.group(3)        # HTTP方法（GET/POST等）
            url = match.group(4)           # 请求URL
            status_code = match.group(5)   # HTTP状态码
            response_size = match.group(6) # 响应大小
            referer = match.group(7)       # 引用页面
            user_agent = match.group(8)    # 用户代理
            
            # 解析时间戳字符串为datetime对象
            # strptime()根据指定格式解析时间字符串
            # %d/%b/%Y:%H:%M:%S %z 对应 25/Dec/2023:10:00:00 +0800
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            
            # 解析URL和查询参数
            # split('?', 1)：按?分割，最多分割1次，分为路径和参数部分
            url_parts = url.split('?', 1)
            base_url = url_parts[0]  # URL路径部分
            params = {}  # 初始化参数字典
            
            if len(url_parts) > 1:
                # 如果存在查询参数，解析为字典格式
                params = self._parse_query_string(url_parts[1])
            
            # 创建并返回HTTPRequest对象
            return HTTPRequest(
                url=url,                    # 完整URL
                method=method,              # HTTP方法
                headers={                   # HTTP头部信息
                    'User-Agent': user_agent,
                    'Referer': referer
                },
                params=params,              # 查询参数字典
                body=None,                  # 请求体（日志中通常没有）
                source_ip=source_ip,        # 客户端IP
                timestamp=timestamp,        # 请求时间
                raw_data=line,              # 原始日志行
                user_agent=user_agent       # 用户代理
            )
        except Exception as e:
            # 解析失败时返回None，不抛出异常
            # 这样可以跳过格式错误的日志行，继续处理其他行
            return None
    
    def _parse_query_string(self, query_string: str) -> dict:
        """解析查询字符串
        
        将URL中的查询参数字符串转换为字典格式
        
        示例：
        输入: "id=1&name=test&page=2"
        输出: {"id": "1", "name": "test", "page": "2"}
        
        Args:
            query_string: URL查询参数字符串
            
        Returns:
            包含所有参数的字典
        """
        params = {}  # 初始化参数字典
        
        if not query_string:
            # 如果查询字符串为空，返回空字典
            return params
            
        # 按&符号分割参数对
        for pair in query_string.split('&'):
            if '=' in pair:
                # 如果包含=号，分割为键值对
                # split('=', 1)：最多分割1次，防止值中包含=号时出错
                key, value = pair.split('=', 1)
                params[key] = value
            else:
                # 如果没有=号，将整个字符串作为键，值为空字符串
                params[pair] = ''
        
        return params 