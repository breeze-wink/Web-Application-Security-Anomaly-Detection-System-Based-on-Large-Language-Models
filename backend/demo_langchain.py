#!/usr/bin/env python3
"""LangChain安全分析演示脚本"""

import asyncio
import os
from datetime import datetime
from app.llm.langchain_provider import LangChainProvider
from app.llm.prompt_templates import SecurityAnalysisPrompts, PromptBuilder
from app.llm.chain_factory import ChainManager
from app.core.models import SecurityEvent, HTTPRequest, DetectionResult, AttackType


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🔒 LangChain安全分析演示")
    print("=" * 60)


def create_demo_security_events():
    """创建演示用的安全事件"""
    events = []
    
    # SQL注入事件
    sql_request = HTTPRequest(
        url="/admin/login?id=1' OR 1=1--",
        method="POST",
        headers={"User-Agent": "Mozilla/5.0"},
        params={"id": "1' OR 1=1--"},
        body=None,
        source_ip="192.168.1.100",
        timestamp=datetime.now(),
        raw_data="POST /admin/login?id=1' OR 1=1-- HTTP/1.1"
    )
    
    sql_detection = DetectionResult(
        is_attack=True,
        attack_types=[AttackType.SQL_INJECTION],
        confidence=0.95,
        payload="1' OR 1=1--"
    )
    
    sql_event = SecurityEvent(
        event_id="demo_sql_001",
        request=sql_request,
        detection=sql_detection
    )
    events.append(("SQL注入攻击", sql_event))
    
    # XSS攻击事件
    xss_request = HTTPRequest(
        url="/search?q=<script>alert('XSS')</script>",
        method="GET",
        headers={"User-Agent": "Mozilla/5.0"},
        params={"q": "<script>alert('XSS')</script>"},
        body=None,
        source_ip="10.0.0.50",
        timestamp=datetime.now(),
        raw_data="GET /search?q=<script>alert('XSS')</script> HTTP/1.1"
    )
    
    xss_detection = DetectionResult(
        is_attack=True,
        attack_types=[AttackType.XSS],
        confidence=0.88,
        payload="<script>alert('XSS')</script>"
    )
    
    xss_event = SecurityEvent(
        event_id="demo_xss_001",
        request=xss_request,
        detection=xss_detection
    )
    events.append(("XSS攻击", xss_event))
    
    return events


def demo_prompt_templates():
    """演示提示词模板功能"""
    print("\n📝 提示词模板演示")
    print("-" * 40)
    
    # 显示可用模板
    templates = SecurityAnalysisPrompts.list_available_templates()
    print(f"可用模板: {', '.join(templates)}")
    
    # 演示基础威胁分析模板
    print("\n🔍 基础威胁分析模板:")
    template = SecurityAnalysisPrompts.get_prompt_template("threat_analysis")
    print(f"模板变量: {template.input_variables}")
    
    # 演示SQL注入专项模板
    print("\n💉 SQL注入专项分析模板:")
    sql_template = SecurityAnalysisPrompts.get_prompt_template("sql_injection")
    print(f"模板变量: {sql_template.input_variables}")


def demo_prompt_builder():
    """演示提示词构建器"""
    print("\n🔧 提示词构建器演示")
    print("-" * 40)
    
    builder = PromptBuilder()
    
    # 模拟事件数据
    event_data = {
        "source_ip": "192.168.1.100",
        "target_url": "/admin/login?id=1' OR 1=1--",
        "http_method": "POST",
        "user_agent": "Mozilla/5.0",
        "detection_time": "2024-01-01 10:00:00",
        "threat_types": "SQL注入",
        "confidence": "0.95",
        "attack_payload": "1' OR 1=1--",
        "raw_request": "POST /admin/login HTTP/1.1"
    }
    
    # 构建威胁分析提示词
    prompt = builder.build_threat_analysis_prompt(event_data)
    print("构建的提示词片段:")
    print(prompt[:200] + "...")


async def demo_chain_factory():
    """演示链工厂功能"""
    print("\n⛓️ 链工厂演示")
    print("-" * 40)
    
    # 模拟LLM（在真实环境中会使用真实的ChatOpenAI）
    class MockLLM:
        async def arun(self, **kwargs):
            return '{"severity": "HIGH", "attack_intent": "演示攻击意图", "confidence_score": 0.9}'
    
    mock_llm = MockLLM()
    
    try:
        from app.llm.chain_factory import SecurityAnalysisChainFactory
        factory = SecurityAnalysisChainFactory(mock_llm)
        
        # 显示支持的威胁类型
        threat_types = factory.get_supported_threat_types()
        print(f"支持的威胁类型: {threat_types}")
        
        # 创建基础分析链
        basic_chain = factory.create_basic_analysis_chain()
        print(f"基础分析链输出键: {basic_chain.output_key}")
        
        # 创建并行分析链
        parallel_chains = factory.create_parallel_analysis_chain(["sql_injection", "xss"])
        print(f"并行分析链数量: {len(parallel_chains)}")
        print(f"并行分析链键: {list(parallel_chains.keys())}")
        
        print("✅ 链工厂功能正常")
        
    except Exception as e:
        print(f"❌ 链工厂演示失败: {e}")


async def demo_security_analysis(use_real_api=False):
    """演示安全分析功能"""
    print("\n🛡️ 安全分析演示")
    print("-" * 40)
    
    if use_real_api:
        # 使用真实API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ 需要设置OPENAI_API_KEY环境变量")
            return
        
        config = {
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
            "temperature": 0.1
        }
        
        print("🌐 使用真实OpenAI API")
    else:
        # 使用Mock模式演示
        print("🔄 使用Mock模式演示")
        return  # 在Mock模式下跳过这个演示
    
    # 创建演示事件
    events = create_demo_security_events()
    
    try:
        provider = LangChainProvider(config)
        
        for event_name, event in events:
            print(f"\n📊 分析 {event_name}:")
            print(f"   来源IP: {event.request.source_ip}")
            print(f"   目标URL: {event.request.url}")
            print(f"   攻击载荷: {event.detection.payload}")
            
            if use_real_api:
                # 执行真实分析
                result = await provider.analyze_security_event(event)
                
                print(f"   分析结果:")
                print(f"     威胁等级: {result.severity.value}")
                print(f"     攻击意图: {result.attack_intent[:100]}...")
                print(f"     置信度: {result.confidence:.2f}")
                print(f"     建议数量: {len(result.recommendations)}")
            else:
                print("   [Mock模式 - 跳过真实分析]")
            
    except Exception as e:
        print(f"❌ 安全分析演示失败: {e}")


async def main():
    """主函数"""
    print_banner()
    
    # 演示各个组件
    demo_prompt_templates()
    demo_prompt_builder()
    await demo_chain_factory()
    
    # 询问是否使用真实API
    print("\n" + "=" * 60)
    choice = input("是否使用真实OpenAI API进行演示? (需要API key) [y/N]: ").lower().strip()
    use_real_api = choice in ['y', 'yes']
    
    await demo_security_analysis(use_real_api)
    
    print("\n" + "=" * 60)
    print("✅ LangChain安全分析演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 