from pixelarrayllm.client import AsyncClient
from typing import Union, List, Dict, Any, AsyncGenerator
import json
import aiohttp


class LLMCallManagerAsync:
    """异步LLM模型调用管理器"""

    def __init__(self, api_key: str, base_url: str = "https://llm.pixelarrayai.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.async_client = AsyncClient(api_key, base_url)

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        description:
            获取可用的模型列表
        returns:
            models(list): 模型列表
        """
        data, success = await self.async_client._request(
            "POST", "/api/llm/list_models", json={}
        )
        if not success:
            raise Exception("获取模型列表失败")
        return data

    async def call_model(
        self,
        provider: str,
        model: str,
        input: Dict[str, Any],
    ) -> AsyncGenerator:
        """
        description:
            调用模型
        parameters:
            provider: 云服务厂商，如 "google", "aliyun"
            model: 模型名称，如 "gemini-2.0-flash", "qwen3-max"
            input: 模型输入参数
        returns:
            AsyncGenerator: 模型响应结果流
        """
        timeout = aiohttp.ClientTimeout(total=300)  # 5分钟超时
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/api/llm/call_model",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                json={"provider": provider, "model": model, "input": input},
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"调用模型失败: {resp.status}")

                # 读取整个响应内容，然后按行分割
                # 这样可以避免 aiohttp 的 chunk 大小限制问题
                content = await resp.read()
                content_str = content.decode("utf-8")
                
                # 按行分割并处理每一行
                for line in content_str.split("\n"):
                    line = line.strip()
                    if line:
                        try:
                            chunk = json.loads(line)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
