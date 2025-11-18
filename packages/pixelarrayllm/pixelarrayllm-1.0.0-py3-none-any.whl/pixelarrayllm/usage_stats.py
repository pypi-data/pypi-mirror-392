from pixelarrayllm.client import AsyncClient
from typing import Dict, Any, Optional, List
from datetime import datetime


class UsageStatsManagerAsync:
    """异步使用统计管理器"""

    def __init__(self, api_key: str, base_url: str = "https://llm.pixelarrayai.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.async_client = AsyncClient(api_key, base_url)

    async def get_user_stats(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        api_type: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取用户使用统计"""
        params = {}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if api_type:
            params["api_type"] = api_type
        if provider:
            params["provider"] = provider

        data, success = await self.async_client._request(
            "GET", "/api/usage/user_stats", params=params
        )
        if not success:
            raise Exception("获取用户使用统计失败")
        return data

    async def get_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """获取每日使用汇总"""
        params = {}
        if date:
            params["date"] = date

        data, success = await self.async_client._request(
            "GET", "/api/usage/daily_summary", params=params
        )
        if not success:
            raise Exception("获取每日使用汇总失败")
        return data

    async def get_recent_logs(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """获取最近的使用记录"""
        params = {"limit": limit, "offset": offset}

        data, success = await self.async_client._request(
            "GET", "/api/usage/recent_logs", params=params
        )
        if not success:
            raise Exception("获取最近使用记录失败")
        return data
