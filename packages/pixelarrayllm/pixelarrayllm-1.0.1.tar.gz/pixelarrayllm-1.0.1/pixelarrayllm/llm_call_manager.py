from pixelarrayllm.client import AsyncClient
from typing import Union, List, Dict, Any, AsyncGenerator
import json
import aiohttp


class LLMCallManagerAsync:
    """
    异步LLM模型调用管理器
    
    用于调用各种云服务厂商的LLM模型，支持文本生成、图片生成、图片编辑等多种功能。
    支持流式响应，可以实时获取模型生成的内容。
    """

    def __init__(self, api_key: str, base_url: str = "https://llm.pixelarrayai.com"):
        """
        初始化LLM调用管理器
        
        Args:
            api_key (str): API密钥，用于身份验证
            base_url (str): 服务端基础URL，默认为 "https://llm.pixelarrayai.com"
        """
        self.api_key = api_key
        self.base_url = base_url
        self.async_client = AsyncClient(api_key, base_url)

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的模型列表
        
        Returns:
            List[Dict[str, Any]]: 模型列表，每个模型包含以下字段：
                - provider (str): 云服务厂商，如 "google", "aliyun"
                - model (str): 模型名称，如 "gemini-2.0-flash", "qwen3-max"
                - type (str): API类型，如 "text_generation", "image_generation"
                - accept_parameters (dict): 接受的参数配置
                - default_parameters (dict, 可选): 默认参数
                - modelKey (str): 唯一标识符，格式为 "{provider}-{model}"
        
        Raises:
            Exception: 当获取模型列表失败时抛出异常
        
        Example:
            >>> manager = LLMCallManagerAsync(api_key="your_api_key")
            >>> models = await manager.list_models()
            >>> print(models)
            [
                {
                    "provider": "google",
                    "model": "gemini-2.0-flash",
                    "type": "text_generation",
                    "accept_parameters": {...},
                    "modelKey": "google-gemini-2.0-flash"
                },
                ...
            ]
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
        调用LLM模型（流式响应）
        
        该方法会向服务端发送请求，并返回一个异步生成器，用于接收流式响应数据。
        响应以JSON格式逐行返回，每行是一个完整的JSON对象。
        
        Args:
            provider (str): 云服务厂商名称
                - "google": Google云服务
                - "aliyun": 阿里云服务
            
            model (str): 模型名称，具体可用的模型请通过 list_models() 方法获取
                常见模型示例：
                - "gemini-2.0-flash": Google文本生成模型
                - "gemini-2.5-flash-image": Google图片生成模型
                - "qwen3-max": 阿里云文本生成模型
                - "qwen-image-plus": 阿里云图片生成模型
                - "qwen-image-edit-plus": 阿里云图片编辑模型
            
            input (Dict[str, Any]): 模型输入参数，格式如下：
                {
                    # 文本输入（可选，根据模型要求）
                    "text": {
                        "type": "text",
                        "content": "用户输入的文本内容"
                    },
                    
                    # 图片输入（可选，根据模型要求）
                    "images": {
                        "type": "base64",  # 或 "url"
                        "content": [  # base64类型时为字符串数组，url类型时为URL字符串数组
                            "base64编码的图片数据",  # 不包含data URI前缀（如data:image/png;base64,）
                            ...
                        ]
                    },
                    
                    # 音频输入（可选，仅部分模型支持）
                    "audios": {
                        "type": "base64", # 或 "url"
                        "content": [  # base64类型时为字符串数组，url类型时为URL字符串数组
                            "base64编码的音频数据",  # 不包含data URI前缀（如data:audio/mpeg;base64,）
                            ...
                        ]
                    },
                    
                    # 视频输入（可选，仅部分模型支持）
                    "videos": {
                        "type": "base64", # 或 "url"
                        "content": [  # base64类型时为字符串数组，url类型时为URL字符串数组
                            "base64编码的视频数据",  # 不包含data URI前缀（如data:video/mp4;base64,）
                            ...
                        ]
                    }
                }
                
                参数说明：
                - text: 文本类型参数，type固定为"text"，content为字符串
                - images: 图片类型参数
                    * type为"base64"时，content为base64字符串数组（不包含data URI前缀）
                    * type为"url"时，content为图片URL字符串数组
                - audios: 音频类型参数，type固定为"base64"，content为base64字符串数组
                - videos: 视频类型参数，type固定为"base64"，content为base64字符串数组
                
                注意：
                - 不同模型接受的参数不同，请根据模型配置提供相应的参数
                - 必填参数必须提供，否则会返回错误
                - base64编码的数据不应包含data URI前缀（如"data:image/png;base64,"）
        
        Yields:
            Dict[str, Any]: 流式响应数据块，每个chunk是一个字典，格式如下：
            
            1. 内容响应chunk（流式生成过程中）:
                {
                    "response": {
                        # 文本响应（文本生成模型）
                        "text": {
                            "content": "模型生成的文本片段",
                            "type": "text"
                        },
                        # 或图片响应（图片生成/编辑模型）
                        "images": {
                            "content": ["图片数据1", "图片数据2", ...],  # base64字符串数组或URL字符串数组
                            "type": "base64"  # 或 "url"
                        }
                    }
                }
                
                注意：流式响应中，文本内容会分多次返回，每次返回一个文本片段。
                需要将所有chunk中的text.content拼接起来才能得到完整文本。
            
            2. 完成响应chunk（最后一个chunk，包含使用统计）:
                {
                    "request_id": "请求唯一标识符",
                    "success": True,  # 布尔值，表示请求是否成功
                    "usage": {  # 使用统计信息
                        "prompt_tokens": 100,  # 输入token数量
                        "completion_tokens": 200,  # 输出token数量
                        "total_tokens": 300,  # 总token数量
                        # 其他可能的字段根据不同的云服务厂商可能有所不同
                    }
                }
                
                注意：最后一个chunk同时包含request_id和usage字段，用于标识请求完成和统计使用情况。
        
        Raises:
            Exception: 当HTTP状态码不是200时抛出异常，异常信息包含状态码
        
        Example:
            >>> manager = LLMCallManagerAsync(api_key="your_api_key")
            >>> 
            >>> # 示例1: 文本生成
            >>> async for chunk in manager.call_model(
            ...     provider="google",
            ...     model="gemini-2.0-flash",
            ...     input={
            ...         "text": {
            ...             "content": "Hello, please tell me a joke",
            ...             "type": "text"
            ...         }
            ...     }
            ... ):
            ...     if "response" in chunk:
            ...         # 处理内容响应
            ...         if "text" in chunk["response"]:
            ...             print(chunk["response"]["text"]["content"], end="")
            ...     elif "request_id" in chunk:
            ...         # 处理完成响应
            ...         print(f"\\n请求ID: {chunk['request_id']}")
            ...         print(f"使用统计: {chunk['usage']}")
            >>> 
            >>> # 示例2: 图片生成（带图片输入）
            >>> async for chunk in manager.call_model(
            ...     provider="google",
            ...     model="gemini-2.5-flash-image",
            ...     input={
            ...         "images": {
            ...             "type": "base64",
            ...             "content": [base64_image_data]  # base64字符串，不包含data URI前缀
            ...         },
            ...         "text": {
            ...             "content": "把照片改为白底",
            ...             "type": "text"
            ...         }
            ...     }
            ... ):
            ...     if "response" in chunk:
            ...         if "images" in chunk["response"]:
            ...             # 处理图片响应
            ...             images = chunk["response"]["images"]["content"]
            ...             for img in images:
            ...                 # 如果是base64，需要添加data URI前缀才能显示
            ...                 img_data_uri = f"data:image/png;base64,{img}"
            >>> 
            >>> # 示例3: 图片编辑（使用URL）
            >>> async for chunk in manager.call_model(
            ...     provider="aliyun",
            ...     model="qwen-image-edit-plus",
            ...     input={
            ...         "images": {
            ...             "type": "url",
            ...             "content": [
            ...                 "https://example.com/image1.png",
            ...                 "https://example.com/image2.png"
            ...             ]
            ...         },
            ...         "text": {
            ...             "content": "图1中的女生穿着图2中的黑色裙子按图3的姿势坐下",
            ...             "type": "text"
            ...         }
            ...     }
            ... ):
            ...     # 处理响应...
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
