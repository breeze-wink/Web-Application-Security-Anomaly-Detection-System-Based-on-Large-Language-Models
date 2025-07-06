#!/usr/bin/env python3
"""
Coraza WAF检测器集成测试
验证新的企业级WAF检测能力
"""

import sys
import os
from datetime import datetime
from typing import List, Tuple

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.detector import DetectionEngine, CorazaDetector
from app.core.models import HTTPRequest, AttackType

class CorazaIntegrationTest:
    """Coraza集成测试类"""
    
    def __init__(self):
        self.engine = DetectionEngine()
        self.coraza_detector = CorazaDetector()
        
    def create_test_request(self, url: str, method: str = "GET", 
                          headers: dict = None, params: dict = None, 
                          body: str = None) -> HTTPRequest:
        """创建测试请求"""
        return HTTPRequest(
            url=url,
            method=method,
            headers=headers or {},
            params=params or {},
            body=body,
            source_ip="192.168.1.100",
            timestamp=datetime.now(),
            raw_data=f"{method} {url}"
        )
    
    def run_test_case(self, name: str, request: HTTPRequest) -> Tuple[bool, dict]:
        """运行单个测试用例"""
        print(f"\n🔍 测试用例: {name}")
        print(f"   URL: {request.url}")
        print(f"   Method: {request.method}")
        if request.params:
            print(f"   Params: {request.params}")
        if request.body:
            print(f"   Body: {request.body}")
        
        try:
            result = self.engine.detect_all(request)
            
            print(f"   结果: {'🚨 检测到攻击' if result.is_attack else '✅ 正常请求'}")
            if result.is_attack:
                print(f"   攻击类型: {[t.value for t in result.attack_types]}")
                print(f"   置信度: {result.confidence:.2f}")
                print(f"   匹配规则: {result.matched_rules}")
                if result.payload:
                    print(f"   攻击载荷: {result.payload}")
            
            return result.is_attack, result.details
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False, {"error": str(e)}
    
    def test_sql_injection_attacks(self):
        """测试SQL注入攻击检测"""
        print("\n" + "="*60)
        print("🛡️  SQL注入攻击检测测试")
        print("="*60)
        
        test_cases = [
            # Union-based注入
            ("Union-based SQL注入", self.create_test_request(
                "/api/users",
                params={"id": "1 UNION SELECT username,password FROM users"}
            )),
            
            # Boolean-based盲注
            ("Boolean-based盲注", self.create_test_request(
                "/login",
                params={"username": "admin' AND 1=1--", "password": "test"}
            )),
            
            # Time-based盲注
            ("Time-based盲注", self.create_test_request(
                "/search",
                params={"q": "test'; WAITFOR DELAY '00:00:05'--"}
            )),
            
            # 编码绕过
            ("URL编码绕过", self.create_test_request(
                "/api/data",
                params={"filter": "id=1%20UNION%20SELECT%20*%20FROM%20admin"}
            )),
            
            # 注释绕过
            ("注释绕过", self.create_test_request(
                "/products",
                params={"category": "1'/**/OR/**/1=1--"}
            )),
        ]
        
        detected = 0
        for name, request in test_cases:
            is_attack, _ = self.run_test_case(name, request)
            if is_attack:
                detected += 1
        
        print(f"\n📊 SQL注入检测统计: {detected}/{len(test_cases)} 个攻击被检测到")
        return detected, len(test_cases)
    
    def test_xss_attacks(self):
        """测试XSS攻击检测"""
        print("\n" + "="*60)
        print("🛡️  XSS攻击检测测试")
        print("="*60)
        
        test_cases = [
            # Script标签注入
            ("Script标签注入", self.create_test_request(
                "/comment",
                method="POST",
                body="content=<script>alert('XSS')</script>"
            )),
            
            # 事件处理器注入
            ("事件处理器注入", self.create_test_request(
                "/profile",
                params={"name": "<img src=x onerror=alert('XSS')>"}
            )),
            
            # JavaScript伪协议
            ("JavaScript伪协议", self.create_test_request(
                "/redirect",
                params={"url": "javascript:alert('XSS')"}
            )),
            
            # HTML标签注入
            ("HTML标签注入", self.create_test_request(
                "/message",
                params={"msg": "<iframe src=//evil.com></iframe>"}
            )),
            
            # 编码XSS
            ("编码XSS", self.create_test_request(
                "/search",
                params={"q": "%3Cscript%3Ealert('XSS')%3C/script%3E"}
            )),
        ]
        
        detected = 0
        for name, request in test_cases:
            is_attack, _ = self.run_test_case(name, request)
            if is_attack:
                detected += 1
        
        print(f"\n📊 XSS检测统计: {detected}/{len(test_cases)} 个攻击被检测到")
        return detected, len(test_cases)
    
    def test_command_injection_attacks(self):
        """测试命令注入攻击检测"""
        print("\n" + "="*60)
        print("🛡️  命令注入攻击检测测试")  
        print("="*60)
        
        test_cases = [
            # Unix命令注入
            ("Unix命令注入", self.create_test_request(
                "/api/system",
                params={"cmd": "ls -la /etc/passwd"}
            )),
            
            # Windows命令注入
            ("Windows命令注入", self.create_test_request(
                "/admin/exec",
                params={"command": "dir c:\\windows\\system32"}
            )),
            
            # 命令分隔符
            ("命令分隔符注入", self.create_test_request(
                "/ping",
                params={"host": "8.8.8.8; cat /etc/passwd"}
            )),
            
            # 反引号执行
            ("反引号执行", self.create_test_request(
                "/backup",
                params={"path": "/tmp/`whoami`.log"}
            )),
        ]
        
        detected = 0
        for name, request in test_cases:
            is_attack, _ = self.run_test_case(name, request)
            if is_attack:
                detected += 1
        
        print(f"\n📊 命令注入检测统计: {detected}/{len(test_cases)} 个攻击被检测到")
        return detected, len(test_cases)
    
    def test_path_traversal_attacks(self):
        """测试路径遍历攻击检测"""
        print("\n" + "="*60)
        print("🛡️  路径遍历攻击检测测试")
        print("="*60)
        
        test_cases = [
            # 目录遍历
            ("目录遍历", self.create_test_request(
                "/download",
                params={"file": "../../etc/passwd"}
            )),
            
            # Windows路径遍历
            ("Windows路径遍历", self.create_test_request(
                "/view",
                params={"path": "..\\..\\windows\\system32\\config\\sam"}
            )),
            
            # 文件包含
            ("文件包含", self.create_test_request(
                "/include",
                params={"page": "php://filter/read=convert.base64-encode/resource=index.php"}
            )),
        ]
        
        detected = 0
        for name, request in test_cases:
            is_attack, _ = self.run_test_case(name, request)
            if is_attack:
                detected += 1
        
        print(f"\n📊 路径遍历检测统计: {detected}/{len(test_cases)} 个攻击被检测到")
        return detected, len(test_cases)
    
    def test_normal_requests(self):
        """测试正常请求（应该不被误报）"""
        print("\n" + "="*60)
        print("✅ 正常请求测试（误报率测试）")
        print("="*60)
        
        test_cases = [
            # 正常搜索
            ("正常搜索", self.create_test_request(
                "/search",
                params={"q": "python programming tutorial"}
            )),
            
            # 正常登录
            ("正常登录", self.create_test_request(
                "/login",
                method="POST",
                body="username=admin&password=secretpass123"
            )),
            
            # 正常API调用
            ("正常API调用", self.create_test_request(
                "/api/users/123",
                headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"}
            )),
            
            # 正常文件下载
            ("正常文件下载", self.create_test_request(
                "/download",
                params={"file": "report.pdf"}
            )),
        ]
        
        false_positives = 0
        for name, request in test_cases:
            is_attack, _ = self.run_test_case(name, request)
            if is_attack:
                false_positives += 1
        
        print(f"\n📊 误报统计: {false_positives}/{len(test_cases)} 个正常请求被误报")
        return false_positives, len(test_cases)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Coraza WAF检测器集成测试")
        print("=" * 60)
        
        # 检测器信息
        print(f"检测引擎信息: {self.engine.get_detector_info()}")
        
        # 运行各类测试
        sql_detected, sql_total = self.test_sql_injection_attacks()
        xss_detected, xss_total = self.test_xss_attacks()
        cmd_detected, cmd_total = self.test_command_injection_attacks()
        path_detected, path_total = self.test_path_traversal_attacks()
        false_positives, normal_total = self.test_normal_requests()
        
        # 汇总统计
        total_attacks = sql_total + xss_total + cmd_total + path_total
        total_detected = sql_detected + xss_detected + cmd_detected + path_detected
        
        print("\n" + "="*60)
        print("📈 整体测试统计")
        print("="*60)
        print(f"总攻击检测: {total_detected}/{total_attacks} ({total_detected/total_attacks*100:.1f}%)")
        print(f"SQL注入检测: {sql_detected}/{sql_total} ({sql_detected/sql_total*100:.1f}%)")
        print(f"XSS攻击检测: {xss_detected}/{xss_total} ({xss_detected/xss_total*100:.1f}%)")
        print(f"命令注入检测: {cmd_detected}/{cmd_total} ({cmd_detected/cmd_total*100:.1f}%)")
        print(f"路径遍历检测: {path_detected}/{path_total} ({path_detected/path_total*100:.1f}%)")
        print(f"误报率: {false_positives}/{normal_total} ({false_positives/normal_total*100:.1f}%)")
        
        # 性能评估
        coverage_rate = total_detected / total_attacks
        false_positive_rate = false_positives / normal_total
        
        print(f"\n🏆 性能评估:")
        print(f"  覆盖率: {coverage_rate*100:.1f}% ({'优秀' if coverage_rate >= 0.9 else '良好' if coverage_rate >= 0.8 else '需改进'})")
        print(f"  误报率: {false_positive_rate*100:.1f}% ({'优秀' if false_positive_rate <= 0.05 else '良好' if false_positive_rate <= 0.1 else '需改进'})")
        
        if coverage_rate >= 0.85 and false_positive_rate <= 0.1:
            print("✅ Coraza WAF集成成功！检测性能达到企业级标准")
        else:
            print("⚠️  检测性能需要进一步调优")

def main():
    """主函数"""
    try:
        tester = CorazaIntegrationTest()
        tester.run_all_tests()
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 