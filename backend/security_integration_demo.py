#!/usr/bin/env python3
"""
安全监控集成演示
演示如何使用SecurityCapturer进行日志采集+攻击检测
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security_capturer import SecurityCapturer

async def demo_single_analysis():
    """演示单次分析功能"""
    print("\n" + "="*60)
    print("🔍 单次分析演示")
    print("="*60)
    
    # 使用测试日志文件
    log_file = "tests/sample_logs/access.log"
    capturer = SecurityCapturer(log_file, follow=False)
    
    # 分析单个请求
    event = await capturer.capture_and_analyze_single()
    
    if event:
        print("✅ 分析完成")
        print(f"事件ID: {event.event_id}")
        print(f"风险级别: {event.risk_level}")
        print(f"请求URL: {event.request.url}")
        print(f"来源IP: {event.request.source_ip}")
        print(f"是否攻击: {event.detection_result.is_attack}")
        if event.detection_result.is_attack:
            print(f"攻击类型: {[t.value for t in event.detection_result.attack_types]}")
            print(f"置信度: {event.detection_result.confidence:.2f}")
            print(f"匹配规则: {event.detection_result.matched_rules}")
    else:
        print("❌ 没有找到可分析的请求")

async def demo_stream_analysis():
    """演示流式分析功能"""
    print("\n" + "="*60)
    print("🌊 流式分析演示")
    print("="*60)
    
    log_file = "tests/sample_logs/access.log"
    capturer = SecurityCapturer(log_file, follow=False)
    
    event_count = 0
    attack_count = 0
    max_events = 5  # 最多处理5个事件
    
    print(f"📊 开始处理，最多分析{max_events}个事件...")
    
    async for event in capturer.capture_and_analyze_stream():
        event_count += 1
        
        print(f"\n📦 事件 {event_count}: {event.event_id}")
        print(f"   URL: {event.request.url}")
        print(f"   方法: {event.request.method}")
        print(f"   IP: {event.request.source_ip}")
        print(f"   风险: {event.risk_level}")
        
        if event.detection_result.is_attack:
            attack_count += 1
            print(f"   🚨 攻击检测: {[t.value for t in event.detection_result.attack_types]}")
            print(f"   置信度: {event.detection_result.confidence:.2f}")
            
            if event.detection_result.payload:
                print(f"   载荷: {event.detection_result.payload}")
        else:
            print("   ✅ 正常请求")
        
        if event_count >= max_events:
            break
    
    print(f"\n📈 流式分析完成:")
    print(f"总事件数: {event_count}")
    print(f"攻击事件: {attack_count}")
    if event_count > 0:
        print(f"攻击率: {attack_count/event_count*100:.1f}%")

async def demo_batch_analysis():
    """演示批量分析功能"""
    print("\n" + "="*60)
    print("📊 批量分析演示")
    print("="*60)
    
    log_file = "tests/sample_logs/access.log"
    capturer = SecurityCapturer(log_file, follow=False)
    
    print("🔄 开始批量分析日志文件...")
    
    # 批量分析（最多处理10个请求）
    report = await capturer.batch_analyze_log(max_requests=10)
    
    print(f"\n📈 分析报告:")
    print(f"总结: {report['summary']}")
    print(f"总事件数: {report['total_events']}")
    print(f"攻击事件: {report['attack_events']}")
    print(f"攻击率: {report['attack_rate']:.1f}%")
    
    print(f"\n🎯 风险分布:")
    for risk, count in report['risk_distribution'].items():
        print(f"   {risk}: {count} 个")
    
    if report['top_attack_types']:
        print(f"\n🔥 主要攻击类型:")
        for attack_type, count in report['top_attack_types'][:3]:
            print(f"   {attack_type}: {count} 次")
    
    if report['top_attack_ips']:
        print(f"\n🌐 主要攻击IP:")
        for ip, count in report['top_attack_ips'][:3]:
            print(f"   {ip}: {count} 次")

def show_usage_examples():
    """显示使用示例"""
    print("\n" + "="*60)
    print("💡 使用示例代码")
    print("="*60)
    
    examples = """
# 1. 基本使用 - 单次分析
from security_capturer import SecurityCapturer

capturer = SecurityCapturer("/path/to/access.log")
event = await capturer.capture_and_analyze_single()

if event and event.detection_result.is_attack:
    print(f"发现攻击: {event.detection_result.attack_types}")

# 2. 流式监控 - 实时分析
capturer = SecurityCapturer("/path/to/access.log", follow=True)

async for event in capturer.capture_and_analyze_stream():
    if event.detection_result.is_attack:
        print(f"攻击警报: {event.event_id}")
        # 发送告警、记录到数据库等

# 3. 攻击事件流 - 只关注攻击
async for attack_event in capturer.analyze_attack_only_stream():
    print(f"高风险事件: {attack_event.risk_level}")
    # 立即处理攻击事件

# 4. 批量分析 - 生成报告
report = await capturer.batch_analyze_log(max_requests=1000)
print(f"攻击率: {report['attack_rate']:.1f}%")

# 5. 获取统计信息
stats = capturer.get_stats()
print(f"检测性能: {stats.get('requests_per_second', 0):.1f} 请求/秒")
    """
    
    print(examples)

def show_integration_info():
    """显示集成信息"""
    print("\n" + "="*60)
    print("🔧 集成架构信息")
    print("="*60)
    
    print("🏗️ 架构优势:")
    print("   ✅ 采集+检测一体化")
    print("   ✅ 异步高性能处理")
    print("   ✅ 企业级WAF检测能力")
    print("   ✅ 灵活的使用模式")
    print("   ✅ 详细的统计报告")
    print("   ✅ 实时监控支持")
    
    print("\n📦 主要组件:")
    print("   🔍 LogFileCapturer - 日志文件解析")
    print("   🛡️ CorazaDetector - 企业级WAF检测")
    print("   ⚙️ DetectionEngine - 检测引擎聚合")
    print("   📊 SecurityCapturer - 完整集成方案")

async def main():
    """主函数"""
    print("🚀 安全监控集成演示")
    print("演示如何使用SecurityCapturer进行完整的安全监控")
    
    try:
        # 1. 单次分析
        await demo_single_analysis()
        
        # 2. 流式分析
        await demo_stream_analysis()
        
        # 3. 批量分析
        await demo_batch_analysis()
        
        # 4. 使用示例
        show_usage_examples()
        
        # 5. 集成信息
        show_integration_info()
        
        print("\n" + "="*60)
        print("🎉 演示完成！SecurityCapturer已成功集成capture+detector功能")
        print("="*60)
        
        print("\n📋 总结:")
        print("✅ 删除了旧的检测器文件（sql_injection_detector.py等）")
        print("✅ 创建了CorazaDetector企业级检测器")
        print("✅ 创建了SecurityCapturer集成方案")
        print("✅ 实现了完整的采集+检测+分析流程")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 