"""安全分析提示词模板"""

from langchain.prompts import PromptTemplate
from typing import Dict, List

class SecurityAnalysisPrompts:
    """安全分析提示词模板集合"""
    
    # 基础威胁分析模板
    THREAT_ANALYSIS_TEMPLATE = """
你是一名专业的Web安全分析师，请分析以下安全事件：

=== 事件基本信息 ===
- 来源IP: {source_ip}
- 目标URL: {target_url}
- HTTP方法: {http_method}
- 用户代理: {user_agent}
- 检测时间: {detection_time}

=== 检测结果 ===
- 威胁类型: {threat_types}
- 置信度: {confidence}
- 攻击载荷: {attack_payload}
- 原始请求: {raw_request}

=== 分析要求 ===
请按以下格式返回JSON分析结果：
{{
    "severity": "HIGH|MEDIUM|LOW",
    "attack_intent": "攻击意图的详细描述",
    "technical_analysis": "技术层面的分析",
    "potential_impact": "可能造成的影响",
    "recommendations": [
        "具体的防护建议1",
        "具体的防护建议2",
        "具体的防护建议3"
    ],
    "confidence_score": 0.85
}}

请基于你的专业知识进行深入分析，重点关注攻击手法、威胁等级和防护策略。
"""

    # SQL注入专项分析模板
    SQL_INJECTION_TEMPLATE = """
你是SQL注入攻击分析专家，请分析以下疑似SQL注入事件：

=== 请求信息 ===
URL: {target_url}
参数: {request_params}
载荷: {attack_payload}

=== 分析重点 ===
1. 判断是否为真实的SQL注入攻击
2. 分析SQL注入的具体类型（Union-based、Boolean-based、Time-based等）
3. 评估攻击的危害程度
4. 提供针对性的防护建议

请返回JSON格式的分析结果：
{{
    "is_sql_injection": true/false,
    "injection_type": "Union-based|Boolean-based|Time-based|Error-based",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "attack_vector": "攻击向量分析",
    "data_at_risk": "可能泄露的数据类型",
    "recommendations": ["防护建议列表"]
}}
"""

    # XSS攻击专项分析模板
    XSS_ANALYSIS_TEMPLATE = """
你是XSS攻击分析专家，请分析以下疑似XSS事件：

=== 请求信息 ===
URL: {target_url}
参数: {request_params}
载荷: {attack_payload}

=== 分析重点 ===
1. 判断XSS攻击类型（Stored、Reflected、DOM-based）
2. 分析载荷的复杂程度和绕过技术
3. 评估对用户的威胁程度
4. 提供防护和修复建议

请返回JSON格式的分析结果：
{{
    "xss_type": "Stored|Reflected|DOM-based",
    "severity": "HIGH|MEDIUM|LOW",
    "payload_analysis": "载荷技术分析",
    "impact_assessment": "影响评估",
    "recommendations": ["防护建议列表"]
}}
"""

    # 命令注入专项分析模板
    COMMAND_INJECTION_TEMPLATE = """
你是命令注入攻击分析专家，请分析以下疑似命令注入事件：

=== 请求信息 ===
URL: {target_url}
参数: {request_params}
载荷: {attack_payload}

=== 分析重点 ===
1. 确认是否为真实的命令注入攻击
2. 分析注入的系统命令和意图
3. 评估系统被攻陷的风险
4. 提供紧急响应建议

请返回JSON格式的分析结果：
{{
    "is_command_injection": true/false,
    "injected_commands": ["命令列表"],
    "severity": "CRITICAL|HIGH|MEDIUM",
    "system_risk": "系统风险评估",
    "recommendations": ["紧急响应建议"]
}}
"""

    # 综合安全评估模板
    SECURITY_ASSESSMENT_TEMPLATE = """
你是首席安全官，请对以下安全事件进行综合评估：

=== 事件摘要 ===
{event_summary}

=== 初步分析结果 ===
{initial_analysis}

=== 评估要求 ===
1. 提供执行摘要（适合管理层查看）
2. 评估业务影响和风险等级
3. 制定响应优先级和时间表
4. 提供资源分配建议

请返回JSON格式的评估结果：
{{
    "executive_summary": "管理层摘要",
    "business_impact": "业务影响评估",
    "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
    "response_priority": "IMMEDIATE|URGENT|NORMAL",
    "timeline": "响应时间表",
    "resource_requirements": ["所需资源"]
}}
"""

    @classmethod
    def get_prompt_template(cls, template_type: str) -> PromptTemplate:
        """获取指定类型的提示词模板"""
        
        templates = {
            "threat_analysis": cls.THREAT_ANALYSIS_TEMPLATE,
            "sql_injection": cls.SQL_INJECTION_TEMPLATE,
            "xss_analysis": cls.XSS_ANALYSIS_TEMPLATE,
            "command_injection": cls.COMMAND_INJECTION_TEMPLATE,
            "security_assessment": cls.SECURITY_ASSESSMENT_TEMPLATE
        }
        
        if template_type not in templates:
            raise ValueError(f"未知的模板类型: {template_type}")
        
        return PromptTemplate.from_template(templates[template_type])
    
    @classmethod
    def list_available_templates(cls) -> List[str]:
        """列出所有可用的模板类型"""
        return [
            "threat_analysis",
            "sql_injection", 
            "xss_analysis",
            "command_injection",
            "security_assessment"
        ]

class PromptBuilder:
    """提示词构建器"""
    
    def __init__(self):
        self.prompts = SecurityAnalysisPrompts()
    
    def build_threat_analysis_prompt(self, event_data: Dict) -> str:
        """构建威胁分析提示词"""
        template = self.prompts.get_prompt_template("threat_analysis")
        return template.format(**event_data)
    
    def build_specialized_prompt(self, template_type: str, event_data: Dict) -> str:
        """构建专项分析提示词"""
        template = self.prompts.get_prompt_template(template_type)
        return template.format(**event_data)
    
    def build_assessment_prompt(self, event_summary: str, initial_analysis: str) -> str:
        """构建综合评估提示词"""
        template = self.prompts.get_prompt_template("security_assessment")
        return template.format(
            event_summary=event_summary,
            initial_analysis=initial_analysis
        ) 