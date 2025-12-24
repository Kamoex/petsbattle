import time
import json
import asyncio
import random
from utils.logger import logger


from tornado.httputil import HTTPHeaders
from tornado.httpclient import AsyncHTTPClient
import httpx

MODEL_NAME = "gpt-5"
API_URL = "http://ai-service.tal.com/openai-compatible/v1/chat/completions"
API_KEY = "300000351:02a806dc4e00ecd697b7f6b41c4f6410"

async def req_gpt(system_prompt: str, user_ask:str):
    # 随机一个10以内的整数
    x = random.randint(0, 10)
    y = random.randint(0, 10)
    if "请回答以下问题" in user_ask:
        return str(x * y)
    if "你是一个专业的语文题目解析助手" in system_prompt:
        return json.dumps({"is_right": random.randint(0, 1), "analysis": random.choice(["正确", "错误"])}, False)
    return f"{x} x {y} = ?"
    http_client = AsyncHTTPClient()
    result = ""
    begin_time = time.time()
    
    for i in range(3):
        try:
            # 准备请求数据 - 使用OpenAI Vision API标准格式
            request_data = {
                "model": "gpt-5",
                "messages": [
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text","text": user_ask}]
                    }
                ]
            }
            # 准备请求头
            headers = HTTPHeaders({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            })
            
            # 发送异步请求
            response = await http_client.fetch(
                API_URL,
                method="POST",
                headers=headers,
                body=json.dumps(request_data),
                validate_cert=False,
                request_timeout=300.0
            )
            
            if response.code != 200:
                raise ValueError(f"request vision api failed code: {response.code}, msg: {response.body}")

            # 解析响应
            resp_res = json.loads(response.body)
            gpt_result = resp_res["choices"][0]["message"]["content"]
            
            # 验证结果
            if not isinstance(gpt_result, str):
                logger.warning(f"vision api returned non-string result (attempt {i+1}/3)")
                continue
            if gpt_result.strip() == "":
                logger.warning(f"vision api returned empty result (attempt {i+1}/3)")
                continue
            
            # 直接返回纯文本结果
            result = gpt_result.strip()
            logger.info(f"vision api success, result length: {len(result)} chars")
            return result
            
        except Exception as e:
            logger.error(f"vision api error (attempt {i+1}/3): {str(e)}")
            if i == 2:  # 最后一次重试失败
                import traceback
                logger.error(f"vision api failed after 3 attempts, traceback: {traceback.format_exc()}")
    
    cost_time = time.time() - begin_time
    logger.info(f"vision api total cost time: {cost_time:.2f}s")
    http_client.close()
    
    return ""


async def req_gpt_by_messages(message_list):
    http_client = AsyncHTTPClient()
    result = ""
    begin_time = time.time()
    
    for i in range(3):
        try:
            # 准备请求数据 - 使用OpenAI Vision API标准格式
            request_data = {
                "model": MODEL_NAME,
                "messages": message_list
            }
            # 准备请求头
            headers = HTTPHeaders({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            })
            
            # 发送异步请求
            response = await http_client.fetch(
                API_URL,
                method="POST",
                headers=headers,
                body=json.dumps(request_data),
                validate_cert=False,
                request_timeout=300.0
            )
            
            if response.code != 200:
                raise ValueError(f"request vision api failed code: {response.code}, msg: {response.body}")

            # 解析响应
            resp_res = json.loads(response.body)
            gpt_result = resp_res["choices"][0]["message"]["content"]
            
            # 验证结果
            if not isinstance(gpt_result, str):
                logger.warning(f"vision api returned non-string result (attempt {i+1}/3)")
                continue
            if gpt_result.strip() == "":
                logger.warning(f"vision api returned empty result (attempt {i+1}/3)")
                continue
            
            # 直接返回纯文本结果
            result = gpt_result.strip()
            logger.info(f"vision api success, result length: {len(result)} chars")
            print(result)
            return result
            
        except Exception as e:
            logger.error(f"vision api error (attempt {i+1}/3): {str(e)}")
            if i == 2:  # 最后一次重试失败
                import traceback
                logger.error(f"vision api failed after 3 attempts, traceback: {traceback.format_exc()}")
    
    cost_time = time.time() - begin_time
    logger.info(f"vision api total cost time: {cost_time:.2f}s")
    http_client.close()
    
    return ""


async def req_gpt_stream(system_prompt: str, user_ask: str):
    """
    流式请求GPT API，通过yield返回SSE响应的JSON对象
    """
    begin_time = time.time()
    
    try:
        # 准备请求数据
        request_data = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_ask}]
                }
            ],
            "stream": True
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # 使用httpx发起流式请求
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
            async with client.stream('POST', API_URL, json=request_data, headers=headers) as response:
                if response.status_code != 200:
                    logger.error(f"stream request failed with code: {response.status_code}")
                    return
                
                # 逐行读取SSE响应
                async for line in response.aiter_lines():
                    line = line.strip()
                    
                    # 跳过空行
                    if not line:
                        continue
                    
                    # 解析SSE格式（以 "data: " 开头）
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        
                        # 检查是否是结束标记
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            # 解析JSON并yield
                            data_json = json.loads(data_str)
                            yield data_json
                        except json.JSONDecodeError as e:
                            logger.warning(f"failed to parse SSE data: {data_str}, error: {e}")
                            continue
        
        cost_time = time.time() - begin_time
        logger.info(f"stream api total cost time: {cost_time:.2f}s")
        
    except Exception as e:
        logger.error(f"stream api error: {str(e)}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")


async def req_gpt_by_messages_stream(message_list):
    """
    通过消息列表流式请求GPT API，通过yield返回SSE响应的JSON对象
    """
    begin_time = time.time()
    
    try:
        # 准备请求数据
        request_data = {
            "model": MODEL_NAME,
            "messages": message_list,
            "stream": True
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # 使用httpx发起流式请求
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
            async with client.stream('POST', API_URL, json=request_data, headers=headers) as response:
                if response.status_code != 200:
                    logger.error(f"stream request failed with code: {response.status_code}")
                    return
                
                # 逐行读取SSE响应
                async for line in response.aiter_lines():
                    line = line.strip()
                    
                    # 跳过空行
                    if not line:
                        continue
                    
                    # 解析SSE格式（以 "data: " 开头）
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        
                        # 检查是否是结束标记
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            # 解析JSON并yield
                            data_json = json.loads(data_str)
                            yield data_json
                        except json.JSONDecodeError as e:
                            logger.warning(f"failed to parse SSE data: {data_str}, error: {e}")
                            continue
        
        cost_time = time.time() - begin_time
        logger.info(f"stream api total cost time: {cost_time:.2f}s")
        
    except Exception as e:
        logger.error(f"stream api error: {str(e)}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")

# import asyncio
# asyncio.run(req_gpt("", "你好"))