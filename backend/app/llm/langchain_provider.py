"""基于LangChain的安全分析提供者"""

import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any

from langchain.chains import LLMChain, SequentialChain
from langchain.schema import BaseOutputParser
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

from .base import BaseLLMProvider
from .prompt_templates import SecurityAnalysisPrompts, PromptBuilder
from .chain_factory import ChainManager
from app.core.models import SecurityEvent, LLMAnalysis, Severity
from app.core.exceptions import LLMException


class SecurityAnalysisOutputParser(BaseOutputParser):
    """安全分析结果解析器"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """解析LLM输出为结构化数据"""
        try:
            # 尝试提取JSON
            start = text.find('{')
            end = text.rfind('}')
            if start >= 0 and end >= 0:
                json_text = text[start:end+1]
                return json.loads(json_text)
            else:
                # 如果没有JSON格式，返回原文本
                return {"raw_text": text}
        except json.JSONDecodeError:
            return {"raw_text": text, "parse_error": True}


class SecurityAnalysisChain:
    """安全分析链"""
    
    def __init__(self, llm: ChatOpenAI, prompt_builder: PromptBuilder):
        self.llm = llm
        self.prompt_builder = prompt_builder
        self.parser = SecurityAnalysisOutputParser()
        self._setup_chains()
    
    def _setup_chains(self):
        """设置分析链"""
        
        # 初步威胁分析链
        self.threat_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=SecurityAnalysisPrompts.get_prompt_template("threat_analysis"),
            output_key="threat_analysis",
            verbose=True
        )
        
        # 专项分析链（根据威胁类型选择）
        self.sql_injection_chain = LLMChain(
            llm=self.llm,
            prompt=SecurityAnalysisPrompts.get_prompt_template("sql_injection"),
            output_key="specialized_analysis",
            verbose=True
        )
        
        self.xss_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=SecurityAnalysisPrompts.get_prompt_template("xss_analysis"),
            output_key="specialized_analysis",
            verbose=True
        )
        
        self.command_injection_chain = LLMChain(
            llm=self.llm,
            prompt=SecurityAnalysisPrompts.get_prompt_template("command_injection"),
            output_key="specialized_analysis",
            verbose=True
        )
        
        # 综合评估链
        self.assessment_chain = LLMChain(
            llm=self.llm,
            prompt=SecurityAnalysisPrompts.get_prompt_template("security_assessment"),
            output_key="final_assessment",
            verbose=True
        )
    
    async def run_threat_analysis(self, event_data: Dict) -> Dict[str, Any]:
        """运行威胁分析"""
        try:
            result = await self.threat_analysis_chain.arun(**event_data)
            return self.parser.parse(result)
        except Exception as e:
            raise LLMException(f"威胁分析失败: {e}")
    
    async def run_specialized_analysis(self, threat_type: str, event_data: Dict) -> Dict[str, Any]:
        """运行专项分析"""
        try:
            chain_map = {
                "sql_injection": self.sql_injection_chain,
                "xss": self.xss_analysis_chain,
                "command_injection": self.command_injection_chain
            }
            
            chain = chain_map.get(threat_type.lower())
            if not chain:
                return {"message": f"未支持的威胁类型: {threat_type}"}
            
            result = await chain.arun(**event_data)
            return self.parser.parse(result)
        except Exception as e:
            raise LLMException(f"专项分析失败: {e}")
    
    async def run_assessment(self, event_summary: str, initial_analysis: str) -> Dict[str, Any]:
        """运行综合评估"""
        try:
            result = await self.assessment_chain.arun(
                event_summary=event_summary,
                initial_analysis=initial_analysis
            )
            return self.parser.parse(result)
        except Exception as e:
            raise LLMException(f"综合评估失败: {e}")


class LangChainProvider(BaseLLMProvider):
    """基于LangChain的安全分析提供者"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.temperature = self.config.get('temperature', 0.1)
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        if not self.api_key:
            raise LLMException("OpenAI API key未配置")
        
        self._init_components()
    
    def _init_components(self):
        """初始化组件"""
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # 初始化提示词构建器
        self.prompt_builder = PromptBuilder()
        
        # 初始化链管理器
        self.chain_manager = ChainManager(self.llm)
    
    async def analyze_security_event(self, event: SecurityEvent) -> LLMAnalysis:
        """分析安全事件 - 使用链式处理"""
        try:
            # 提取事件数据
            event_data = self._extract_event_data(event)
            
            # 获取威胁类型列表
            threat_types = [t.value for t in event.detection.attack_types]
            
            # 使用链管理器进行分析
            analysis_result = await self.chain_manager.analyze_security_event(
                event_data, threat_types
            )
            
            if not analysis_result.get("success"):
                raise LLMException(f"链式分析失败: {analysis_result.get('error', '未知错误')}")
            
            # 构建LLM分析结果
            return self._build_llm_analysis_from_chain_result(analysis_result)
            
        except Exception as e:
            raise LLMException(f"链式分析失败: {e}")
    
    async def generate_summary(self, prompt: str) -> str:
        """生成文本摘要"""
        try:
            response = await self.llm.agenerate([[{"role": "user", "content": prompt}]])
            return response.generations[0][0].text
        except Exception as e:
            raise LLMException(f"生成摘要失败: {e}")
    
    async def check_availability(self) -> bool:
        """检查服务可用性"""
        try:
            response = await self.llm.agenerate([[{"role": "user", "content": "test"}]])
            return True
        except:
            return False
    
    def _extract_event_data(self, event: SecurityEvent) -> Dict[str, Any]:
        """提取事件数据用于提示词"""
        attack_types = [t.value for t in event.detection.attack_types]
        
        return {
            "source_ip": event.request.source_ip,
            "target_url": event.request.url,
            "http_method": event.request.method,
            "user_agent": event.request.user_agent or "未知",
            "detection_time": event.request.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "threat_types": ", ".join(attack_types),
            "confidence": f"{event.detection.confidence:.2f}",
            "attack_payload": event.detection.payload or "未检测到明显载荷",
            "raw_request": event.request.raw_data or "原始请求数据不可用",
            "request_params": str(event.request.params) if event.request.params else "无参数"
        }
    
    def _create_event_summary(self, event: SecurityEvent) -> str:
        """创建事件摘要"""
        attack_types = [t.value for t in event.detection.attack_types]
        return f"""
安全事件摘要：
- 事件ID: {event.event_id}
- 检测时间: {event.request.timestamp}
- 来源IP: {event.request.source_ip}
- 目标URL: {event.request.url}
- 威胁类型: {', '.join(attack_types)}
- 置信度: {event.detection.confidence:.2f}
"""
    
    def _build_llm_analysis_from_chain_result(self, chain_result: Dict) -> LLMAnalysis:
        """从链管理器结果构建LLM分析"""
        analysis_results = chain_result.get("analysis_results", {})
        
        # 提取基础分析结果
        basic_result = analysis_results.get("basic_analysis", {})
        basic_data = self._parse_chain_result(basic_result)
        
        # 提取专项分析结果
        specialized_data = {}
        for key, result in analysis_results.items():
            if key.startswith("specialized_"):
                specialized_data[key] = self._parse_chain_result(result)
        
        # 提取评估结果
        assessment_result = analysis_results.get("assessment", {})
        assessment_data = self._parse_chain_result(assessment_result)
        
        # 解析严重程度
        severity_text = basic_data.get("severity", "MEDIUM")
        severity_map = {
            'CRITICAL': Severity.CRITICAL,
            'HIGH': Severity.HIGH, 
            'MEDIUM': Severity.MEDIUM, 
            'LOW': Severity.LOW
        }
        severity = severity_map.get(severity_text, Severity.MEDIUM)
        
        # 整合分析结果
        combined_analysis = {
            "基础威胁分析": basic_data,
            "专项分析": specialized_data,
            "综合评估": assessment_data,
            "链执行时间": chain_result.get("timestamp")
        }
        
        return LLMAnalysis(
            severity=severity,
            attack_intent=basic_data.get("attack_intent", ""),
            potential_impact=basic_data.get("potential_impact", ""),
            recommendations=basic_data.get("recommendations", []),
            confidence=basic_data.get("confidence_score", 0.5),
            analysis_time=datetime.now(),
            raw_analysis=json.dumps(combined_analysis, ensure_ascii=False, indent=2)
        )
    
    def _parse_chain_result(self, result: Dict) -> Dict:
        """解析链执行结果"""
        if not result.get("success"):
            return {"error": result.get("error", "分析失败")}
        
        result_text = result.get("result", "")
        parser = SecurityAnalysisOutputParser()
        return parser.parse(result_text)


class AsyncSecurityAnalysisCallback(BaseCallbackHandler):
    """异步安全分析回调处理器"""
    
    def __init__(self):
        self.start_time = None
        self.tokens_used = 0
    
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """LLM开始时的回调"""
        self.start_time = datetime.now()
        print(f"[LangChain] 开始分析，提示词数量: {len(prompts)}")
    
    async def on_llm_end(self, response, **kwargs) -> None:
        """LLM结束时的回调"""
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"[LangChain] 分析完成，耗时: {duration.total_seconds():.2f}秒")
    
    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """LLM错误时的回调"""
        print(f"[LangChain] 分析失败: {error}") 