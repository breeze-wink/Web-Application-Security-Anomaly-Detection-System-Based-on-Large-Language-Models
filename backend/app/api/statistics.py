"""统计相关API接口"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.storage.base import BaseStorage

# 导入事件API中的存储实例
from .events import get_storage

router = APIRouter(prefix="/statistics", tags=["statistics"])

class DashboardStats(BaseModel):
    """仪表板统计数据"""
    total_events: int
    attack_events: int
    attack_rate: float
    high_risk_events: int

class AttackDistribution(BaseModel):
    """攻击类型分布"""
    attack_type: str
    count: int
    percentage: float

class TrendData(BaseModel):
    """趋势数据"""
    timestamp: datetime
    total_events: int
    attack_events: int

class TopAttackSource(BaseModel):
    """攻击来源统计"""
    source_ip: str
    attack_count: int
    last_attack: datetime

class DashboardResponse(BaseModel):
    """仪表板响应"""
    stats: DashboardStats
    attack_distribution: List[AttackDistribution]
    trend_data: List[TrendData]
    top_attack_sources: List[TopAttackSource]

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_stats(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    storage: BaseStorage = Depends(get_storage)
):
    """获取仪表板统计数据"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # 获取基础统计
        stats_data = await storage.get_statistics(
            start_time=start_time,
            end_time=end_time
        )
        
        # 构建仪表板数据
        total_events = stats_data.get("total_events", 0)
        attack_events = stats_data.get("attack_events", 0)
        attack_rate = (attack_events / total_events * 100) if total_events > 0 else 0
        
        dashboard_stats = DashboardStats(
            total_events=total_events,
            attack_events=attack_events,
            attack_rate=round(attack_rate, 2),
            high_risk_events=stats_data.get("high_risk_events", 0)
        )
        
        # 攻击类型分布
        attack_dist_data = stats_data.get("attack_distribution", {})
        attack_distribution = [
            AttackDistribution(
                attack_type=attack_type,
                count=count,
                percentage=round(count / attack_events * 100, 2) if attack_events > 0 else 0
            )
            for attack_type, count in attack_dist_data.items()
        ]
        
        # 趋势数据
        trend_data = [
            TrendData(
                timestamp=item["timestamp"],
                total_events=item["total_events"],
                attack_events=item["attack_events"]
            )
            for item in stats_data.get("trend_data", [])
        ]
        
        # 攻击来源TOP
        top_sources_data = stats_data.get("top_attack_sources", [])
        top_attack_sources = [
            TopAttackSource(
                source_ip=item["source_ip"],
                attack_count=item["attack_count"],
                last_attack=item["last_attack"]
            )
            for item in top_sources_data
        ]
        
        return DashboardResponse(
            stats=dashboard_stats,
            attack_distribution=attack_distribution,
            trend_data=trend_data,
            top_attack_sources=top_attack_sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@router.get("/trends")
async def get_trend_data(
    period: str = Query("hour", regex="^(hour|day|week)$", description="统计周期"),
    limit: int = Query(24, ge=1, le=168, description="数据点数量"),
    storage: BaseStorage = Depends(get_storage)
):
    """获取趋势数据"""
    try:
        # 根据周期计算时间范围
        if period == "hour":
            delta = timedelta(hours=limit)
        elif period == "day":
            delta = timedelta(days=limit)
        else:  # week
            delta = timedelta(weeks=limit)
            
        end_time = datetime.now()
        start_time = end_time - delta
        
        stats_data = await storage.get_statistics(
            start_time=start_time,
            end_time=end_time,
            period=period
        )
        
        return {
            "period": period,
            "data": stats_data.get("trend_data", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@router.get("/attack-types")
async def get_attack_type_stats(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    storage: BaseStorage = Depends(get_storage)
):
    """获取攻击类型统计"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        stats_data = await storage.get_statistics(
            start_time=start_time,
            end_time=end_time
        )
        
        return {
            "time_range": {
                "start": start_time,
                "end": end_time,
                "hours": hours
            },
            "attack_distribution": stats_data.get("attack_distribution", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取攻击类型统计失败: {str(e)}")

@router.get("/sources")
async def get_attack_sources(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    storage: BaseStorage = Depends(get_storage)
):
    """获取攻击来源统计"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        stats_data = await storage.get_statistics(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "time_range": {
                "start": start_time,
                "end": end_time,
                "hours": hours
            },
            "top_sources": stats_data.get("top_attack_sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取攻击来源统计失败: {str(e)}") 