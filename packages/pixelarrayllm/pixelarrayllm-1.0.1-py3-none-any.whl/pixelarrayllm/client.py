import aiohttp
from typing import Dict, Any, Tuple


class AsyncClient:
    """异步客户端基类"""

    def __init__(self, api_key: str, base_url: str = "https://llm.pixelarrayai.com"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    async def _request(
        self, method: str, url: str, **kwargs
    ) -> Tuple[Dict[str, Any], bool]:
        """统一的异步请求方法"""
        async with aiohttp.ClientSession() as session:
            req_method = getattr(session, method.lower())
            
            # 处理params参数
            params = kwargs.pop("params", None)
            json_data = kwargs.pop("json", None)
            
            async with req_method(
                f"{self.base_url}{url}",
                headers=self.headers,
                params=params,
                json=json_data,
                **kwargs
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("status_code") == 200:
                        return result.get("data", {}), True
                return {}, False
