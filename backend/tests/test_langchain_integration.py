"""LangChain集成测试"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.llm.langchain_provider import LangChainProvider
from app.llm.prompt_templates import SecurityAnalysisPrompts, PromptBuilder
from app.llm.chain_factory import ChainManager, SecurityAnalysisChainFactory
from app.core.models import SecurityEvent, HTTPRequest, DetectionResult, AttackType
from app.core.exceptions import LLMException


class TestPromptTemplates:
    """测试提示词模板"""
    
    def test_get_threat_analysis_template(self):
        """测试获取威胁分析模板"""
        template = SecurityAnalysisPrompts.get_prompt_template("threat_analysis")
        assert template is not None
        assert "severity" in template.template
        assert "attack_intent" in template.template
    
    def test_get_sql_injection_template(self):
        """测试获取SQL注入分析模板"""
        template = SecurityAnalysisPrompts.get_prompt_template("sql_injection")
        assert template is not None
        assert "is_sql_injection" in template.template
        assert "injection_type" in template.template
    
    def test_get_unknown_template(self):
        """测试获取未知模板"""
        with pytest.raises(ValueError):
            SecurityAnalysisPrompts.get_prompt_template("unknown_template")
    
    def test_list_available_templates(self):
        """测试列出可用模板"""
        templates = SecurityAnalysisPrompts.list_available_templates()
        assert "threat_analysis" in templates
        assert "sql_injection" in templates
        assert "xss_analysis" in templates
    
    def test_prompt_builder(self):
        """测试提示词构建器"""
        builder = PromptBuilder()
        
        event_data = {
            "source_ip": "192.168.1.100",
            "target_url": "/admin/login",
            "http_method": "POST",
            "user_agent": "Mozilla/5.0",
            "detection_time": "2024-01-01 10:00:00",
            "threat_types": "SQL注入",
            "confidence": "0.95",
            "attack_payload": "' OR 1=1--",
            "raw_request": "POST /admin/login HTTP/1.1"
        }
        
        prompt = builder.build_threat_analysis_prompt(event_data)
        assert "192.168.1.100" in prompt
        assert "/admin/login" in prompt
        assert "SQL注入" in prompt


class TestChainFactory:
    """测试链工厂"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM"""
        llm = MagicMock()
        llm.arun = AsyncMock(return_value='{"severity": "HIGH", "attack_intent": "测试攻击"}')
        return llm
    
    @pytest.fixture
    def chain_factory(self, mock_llm):
        """创建链工厂"""
        return SecurityAnalysisChainFactory(mock_llm)
    
    def test_create_basic_analysis_chain(self, chain_factory):
        """测试创建基础分析链"""
        chain = chain_factory.create_basic_analysis_chain()
        assert chain is not None
        assert chain.output_key == "basic_analysis_result"
    
    def test_create_specialized_chain(self, chain_factory):
        """测试创建专项分析链"""
        chain = chain_factory.create_specialized_chain("sql_injection")
        assert chain is not None
        assert chain.output_key == "specialized_analysis_result"
    
    def test_create_unsupported_specialized_chain(self, chain_factory):
        """测试创建不支持的专项分析链"""
        with pytest.raises(LLMException):
            chain_factory.create_specialized_chain("unsupported_type")
    
    def test_create_parallel_analysis_chain(self, chain_factory):
        """测试创建并行分析链"""
        chains = chain_factory.create_parallel_analysis_chain(["sql_injection", "xss"])
        assert "basic_analysis" in chains
        assert "specialized_sql_injection" in chains
        assert "specialized_xss" in chains
        assert "assessment" in chains
    
    def test_get_supported_threat_types(self, chain_factory):
        """测试获取支持的威胁类型"""
        types = chain_factory.get_supported_threat_types()
        assert "sql_injection" in types
        assert "xss" in types
        assert "command_injection" in types
    
    def test_chain_cache(self, chain_factory):
        """测试链缓存"""
        # 创建两次相同的链
        chain1 = chain_factory.create_basic_analysis_chain()
        chain2 = chain_factory.create_basic_analysis_chain()
        
        # 应该是同一个对象（缓存）
        assert chain1 is chain2
        
        # 清除缓存
        chain_factory.clear_cache()
        chain3 = chain_factory.create_basic_analysis_chain()
        
        # 应该是新对象
        assert chain1 is not chain3


class TestChainManager:
    """测试链管理器"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM"""
        llm = MagicMock()
        return llm
    
    @pytest.fixture
    def chain_manager(self, mock_llm):
        """创建链管理器"""
        return ChainManager(mock_llm)
    
    @pytest.mark.asyncio
    async def test_analyze_security_event_success(self, chain_manager):
        """测试成功分析安全事件"""
        event_data = {
            "source_ip": "192.168.1.100",
            "target_url": "/admin/login",
            "threat_types": "SQL注入"
        }
        
        # Mock链执行结果
        mock_result = {
            "success": True,
            "result": '{"severity": "HIGH", "attack_intent": "SQL注入攻击"}'
        }
        
        with patch.object(chain_manager.executor, 'execute_parallel_chains', 
                         return_value={"basic_analysis": mock_result}):
            result = await chain_manager.analyze_security_event(event_data, ["sql_injection"])
            
            assert result["success"] is True
            assert "analysis_results" in result
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_analyze_security_event_failure(self, chain_manager):
        """测试分析安全事件失败"""
        event_data = {}
        
        with patch.object(chain_manager.executor, 'execute_parallel_chains', 
                         side_effect=Exception("分析失败")):
            result = await chain_manager.analyze_security_event(event_data, [])
            
            assert result["success"] is False
            assert "error" in result
    
    def test_get_chain_statistics(self, chain_manager):
        """测试获取链统计信息"""
        stats = chain_manager.get_chain_statistics()
        assert "cached_chains" in stats
        assert "supported_threats" in stats
        assert "factory_status" in stats


class TestLangChainProvider:
    """测试LangChain提供者"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock配置"""
        return {
            "api_key": "test_api_key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.1
        }
    
    @pytest.fixture
    def mock_security_event(self):
        """Mock安全事件"""
        request = HTTPRequest(
            url="/admin/login?id=1' OR 1=1--",
            method="POST",
            headers={"User-Agent": "test"},
            params={"id": "1' OR 1=1--"},
            body=None,
            source_ip="192.168.1.100",
            timestamp=datetime.now(),
            raw_data="POST /admin/login?id=1' OR 1=1-- HTTP/1.1"
        )
        
        detection = DetectionResult(
            is_attack=True,
            attack_types=[AttackType.SQL_INJECTION],
            confidence=0.95,
            payload="1' OR 1=1--"
        )
        
        return SecurityEvent(
            event_id="test_event_001",
            request=request,
            detection=detection
        )
    
    @patch('app.llm.langchain_provider.ChatOpenAI')
    def test_provider_initialization(self, mock_chat_openai, mock_config):
        """测试提供者初始化"""
        provider = LangChainProvider(mock_config)
        
        assert provider.api_key == "test_api_key"
        assert provider.model == "gpt-3.5-turbo"
        assert provider.temperature == 0.1
        assert provider.llm is not None
        assert provider.chain_manager is not None
    
    def test_provider_initialization_without_api_key(self):
        """测试没有API key的初始化"""
        with pytest.raises(LLMException):
            LangChainProvider({})
    
    @patch('app.llm.langchain_provider.ChatOpenAI')
    @pytest.mark.asyncio
    async def test_analyze_security_event(self, mock_chat_openai, mock_config, mock_security_event):
        """测试分析安全事件"""
        provider = LangChainProvider(mock_config)
        
        # Mock链管理器结果
        mock_analysis_result = {
            "success": True,
            "analysis_results": {
                "basic_analysis": {
                    "success": True,
                    "result": '{"severity": "HIGH", "attack_intent": "SQL注入攻击", "confidence_score": 0.9}'
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        with patch.object(provider.chain_manager, 'analyze_security_event', 
                         return_value=mock_analysis_result):
            result = await provider.analyze_security_event(mock_security_event)
            
            assert result is not None
            assert hasattr(result, 'severity')
            assert hasattr(result, 'attack_intent')
            assert hasattr(result, 'confidence')
    
    @patch('app.llm.langchain_provider.ChatOpenAI')
    @pytest.mark.asyncio
    async def test_analyze_security_event_failure(self, mock_chat_openai, mock_config, mock_security_event):
        """测试分析安全事件失败"""
        provider = LangChainProvider(mock_config)
        
        # Mock链管理器失败
        mock_analysis_result = {
            "success": False,
            "error": "分析失败"
        }
        
        with patch.object(provider.chain_manager, 'analyze_security_event', 
                         return_value=mock_analysis_result):
            with pytest.raises(LLMException):
                await provider.analyze_security_event(mock_security_event)
    
    def test_extract_event_data(self, mock_config, mock_security_event):
        """测试提取事件数据"""
        with patch('app.llm.langchain_provider.ChatOpenAI'):
            provider = LangChainProvider(mock_config)
            event_data = provider._extract_event_data(mock_security_event)
            
            assert event_data["source_ip"] == "192.168.1.100"
            assert event_data["target_url"] == "/admin/login?id=1' OR 1=1--"
            assert event_data["http_method"] == "POST"
            assert "SQL注入" in event_data["threat_types"]
    
    def test_create_event_summary(self, mock_config, mock_security_event):
        """测试创建事件摘要"""
        with patch('app.llm.langchain_provider.ChatOpenAI'):
            provider = LangChainProvider(mock_config)
            summary = provider._create_event_summary(mock_security_event)
            
            assert "test_event_001" in summary
            assert "192.168.1.100" in summary
            assert "SQL注入" in summary


if __name__ == "__main__":
    # 运行基础测试
    pytest.main([__file__, "-v"]) 