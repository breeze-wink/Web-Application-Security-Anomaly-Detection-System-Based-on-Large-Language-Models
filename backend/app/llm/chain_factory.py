"""安全分析链工厂"""

from typing import Dict, Any, Optional, List
from langchain.chains import LLMChain, SequentialChain
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI

from .prompt_templates import SecurityAnalysisPrompts
from app.core.exceptions import LLMException


class SecurityAnalysisChainFactory:
    """安全分析链工厂"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompts = SecurityAnalysisPrompts()
        self._chains_cache = {}
    
    def create_basic_analysis_chain(self) -> LLMChain:
        """创建基础分析链"""
        if "basic_analysis" not in self._chains_cache:
            self._chains_cache["basic_analysis"] = LLMChain(
                llm=self.llm,
                prompt=self.prompts.get_prompt_template("threat_analysis"),
                output_key="basic_analysis_result",
                verbose=True
            )
        return self._chains_cache["basic_analysis"]
    
    def create_specialized_chain(self, threat_type: str) -> LLMChain:
        """创建专项分析链"""
        cache_key = f"specialized_{threat_type}"
        
        if cache_key not in self._chains_cache:
            template_map = {
                "sql_injection": "sql_injection",
                "xss": "xss_analysis", 
                "command_injection": "command_injection"
            }
            
            template_type = template_map.get(threat_type.lower())
            if not template_type:
                raise LLMException(f"不支持的威胁类型: {threat_type}")
            
            self._chains_cache[cache_key] = LLMChain(
                llm=self.llm,
                prompt=self.prompts.get_prompt_template(template_type),
                output_key="specialized_analysis_result",
                verbose=True
            )
        
        return self._chains_cache[cache_key]
    
    def create_assessment_chain(self) -> LLMChain:
        """创建综合评估链"""
        if "assessment" not in self._chains_cache:
            self._chains_cache["assessment"] = LLMChain(
                llm=self.llm,
                prompt=self.prompts.get_prompt_template("security_assessment"),
                output_key="assessment_result",
                verbose=True
            )
        return self._chains_cache["assessment"]
    
    def create_sequential_analysis_chain(self, threat_types: List[str]) -> SequentialChain:
        """创建顺序分析链"""
        chains = []
        input_variables = []
        output_variables = []
        
        # 基础分析链
        basic_chain = self.create_basic_analysis_chain()
        chains.append(basic_chain)
        input_variables.extend(basic_chain.input_keys)
        output_variables.append("basic_analysis_result")
        
        # 专项分析链
        for threat_type in threat_types:
            try:
                specialized_chain = self.create_specialized_chain(threat_type)
                chains.append(specialized_chain)
                output_variables.append(f"specialized_{threat_type}_result")
            except LLMException:
                # 跳过不支持的威胁类型
                continue
        
        # 综合评估链
        assessment_chain = self.create_assessment_chain()
        chains.append(assessment_chain)
        output_variables.append("assessment_result")
        
        return SequentialChain(
            chains=chains,
            input_variables=list(set(input_variables)),
            output_variables=output_variables,
            verbose=True
        )
    
    def create_parallel_analysis_chain(self, threat_types: List[str]) -> Dict[str, LLMChain]:
        """创建并行分析链（用于同时运行多个分析）"""
        chains = {
            "basic_analysis": self.create_basic_analysis_chain()
        }
        
        for threat_type in threat_types:
            try:
                chains[f"specialized_{threat_type}"] = self.create_specialized_chain(threat_type)
            except LLMException:
                continue
        
        chains["assessment"] = self.create_assessment_chain()
        
        return chains
    
    def clear_cache(self):
        """清除链缓存"""
        self._chains_cache.clear()
    
    def get_supported_threat_types(self) -> List[str]:
        """获取支持的威胁类型"""
        return ["sql_injection", "xss", "command_injection"]


class ChainExecutor:
    """链执行器"""
    
    def __init__(self, chain_factory: SecurityAnalysisChainFactory):
        self.chain_factory = chain_factory
    
    async def execute_single_chain(self, chain: LLMChain, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个链"""
        try:
            result = await chain.arun(**input_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_parallel_chains(self, chains: Dict[str, LLMChain], 
                                    input_data: Dict[str, Any]) -> Dict[str, Any]:
        """并行执行多个链"""
        import asyncio
        
        # 创建并行任务
        tasks = {}
        for chain_name, chain in chains.items():
            if chain_name == "assessment":
                # 评估链需要等待其他链完成
                continue
            tasks[chain_name] = asyncio.create_task(
                self.execute_single_chain(chain, input_data)
            )
        
        # 等待并行任务完成
        results = {}
        for chain_name, task in tasks.items():
            results[chain_name] = await task
        
        # 执行评估链
        if "assessment" in chains:
            # 准备评估链的输入
            assessment_input = self._prepare_assessment_input(results, input_data)
            results["assessment"] = await self.execute_single_chain(
                chains["assessment"], assessment_input
            )
        
        return results
    
    def _prepare_assessment_input(self, analysis_results: Dict[str, Any], 
                                original_input: Dict[str, Any]) -> Dict[str, Any]:
        """准备评估链的输入"""
        # 创建事件摘要
        event_summary = f"""
安全事件摘要：
- 来源IP: {original_input.get('source_ip', '未知')}
- 目标URL: {original_input.get('target_url', '未知')}
- 威胁类型: {original_input.get('threat_types', '未知')}
- 检测时间: {original_input.get('detection_time', '未知')}
"""
        
        # 整合分析结果
        initial_analysis = ""
        for chain_name, result in analysis_results.items():
            if result.get("success") and "result" in result:
                initial_analysis += f"\n{chain_name}: {result['result']}\n"
        
        return {
            "event_summary": event_summary,
            "initial_analysis": initial_analysis
        }


class ChainManager:
    """链管理器"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.factory = SecurityAnalysisChainFactory(llm)
        self.executor = ChainExecutor(self.factory)
    
    async def analyze_security_event(self, event_data: Dict[str, Any], 
                                   threat_types: List[str]) -> Dict[str, Any]:
        """分析安全事件"""
        try:
            # 创建并行分析链
            chains = self.factory.create_parallel_analysis_chain(threat_types)
            
            # 执行并行分析
            results = await self.executor.execute_parallel_chains(chains, event_data)
            
            return {
                "success": True,
                "analysis_results": results,
                "timestamp": self._get_current_timestamp()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_chain_statistics(self) -> Dict[str, Any]:
        """获取链统计信息"""
        return {
            "cached_chains": len(self.factory._chains_cache),
            "supported_threats": self.factory.get_supported_threat_types(),
            "factory_status": "active"
        } 