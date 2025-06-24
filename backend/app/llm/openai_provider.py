"""OpenAI LLM提供者"""

import json
import asyncio
from datetime import datetime
from typing import Optional
from .base import BaseLLMProvider
from app.core.models import SecurityEvent, LLMAnalysis, Severity
from app.core.exceptions import LLMException

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API实现"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.client = None
        
        if not self.api_key:
            raise LLMException("OpenAI API key未配置")
        
        self._init_client()
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise LLMException("请安装openai包: pip install openai")
    
    async def analyze_security_event(self, event: SecurityEvent) -> LLMAnalysis:
        """分析安全事件"""
        try:
            prompt = self._build_analysis_prompt(event)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是Web安全专家，请分析安全事件并返回JSON格式结果。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            return self._parse_analysis_result(result_text)
            
        except Exception as e:
            raise LLMException(f"OpenAI分析失败: {e}")
    
    async def generate_summary(self, prompt: str) -> str:
        """生成文本摘要"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是安全分析专家，请生成简洁的摘要。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise LLMException(f"生成摘要失败: {e}")
    
    async def check_availability(self) -> bool:
        """检查服务可用性"""
        try:
            # 发送一个简单的测试请求
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False
    
    def _build_analysis_prompt(self, event: SecurityEvent) -> str:
        """构建分析提示词"""
        attack_types = [t.value for t in event.detection.attack_types]
        
        return f"""
请分析以下Web安全事件：

基本信息:
- 来源IP: {event.request.source_ip}
- 请求URL: {event.request.url}
- 请求方法: {event.request.method}
- 时间: {event.request.timestamp}

检测结果:
- 检测到攻击: {event.detection.is_attack}
- 攻击类型: {attack_types}
- 置信度: {event.detection.confidence}
- 攻击载荷: {event.detection.payload}

请返回JSON格式分析结果:
{{
    "severity": "高/中/低",
    "attack_intent": "攻击意图描述",
    "potential_impact": "可能产生的影响", 
    "recommendations": ["防护建议1", "防护建议2"],
    "confidence": 0.8
}}
"""
    
    def _parse_analysis_result(self, result_text: str) -> LLMAnalysis:
        """解析分析结果"""
        try:
            # 尝试提取JSON
            start = result_text.find('{')
            end = result_text.rfind('}')
            if start >= 0 and end >= 0:
                json_text = result_text[start:end+1]
                data = json.loads(json_text)
            else:
                raise ValueError("未找到JSON格式")
            
            # 解析严重程度
            severity_map = {'高': Severity.HIGH, '中': Severity.MEDIUM, '低': Severity.LOW}
            severity = severity_map.get(data.get('severity', '低'), Severity.LOW)
            
            return LLMAnalysis(
                severity=severity,
                attack_intent=data.get('attack_intent', ''),
                potential_impact=data.get('potential_impact', ''),
                recommendations=data.get('recommendations', []),
                confidence=data.get('confidence', 0.5),
                analysis_time=datetime.now()
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 解析失败时返回默认结果
            return LLMAnalysis(
                severity=Severity.MEDIUM,
                attack_intent="LLM解析失败",
                potential_impact="需要手动分析",
                recommendations=["建议人工审核"],
                confidence=0.3,
                analysis_time=datetime.now()
            ) 