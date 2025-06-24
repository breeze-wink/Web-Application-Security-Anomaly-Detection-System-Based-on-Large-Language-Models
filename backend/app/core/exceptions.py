"""核心异常类定义"""

class SecurityManagerException(Exception):
    """安全管理系统基础异常"""
    pass

class CaptureException(SecurityManagerException):
    """HTTP请求捕获异常"""
    pass

class ParseException(SecurityManagerException):
    """HTTP请求解析异常"""
    pass

class DetectionException(SecurityManagerException):
    """安全检测异常"""
    pass

class LLMException(SecurityManagerException):
    """LLM分析异常"""
    pass

class StorageException(SecurityManagerException):
    """数据存储异常"""
    pass

class ConfigurationException(SecurityManagerException):
    """配置错误异常"""
    pass 