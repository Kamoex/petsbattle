import time
import json
import asyncio
from proto.proto import sign_in_s2c_data
from utils.logger import logger


from tornado.httputil import HTTPHeaders
from tornado.httpclient import AsyncHTTPClient

MODEL_NAME = "gpt-5"
API_URL = "http://ai-service.tal.com/openai-compatible/v1/chat/completions"
API_KEY = "300000351:02a806dc4e00ecd697b7f6b41c4f6410"

async def req_gpt(system_prompt: str, user_ask:str):
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
    流式请求 GPT API，返回异步生成器，yield OpenAI API 的原始 chunk
    """
    http_client = AsyncHTTPClient()
    begin_time = time.time()
    queue = asyncio.Queue()
    
    def streaming_callback(chunk):
        """处理流式响应的回调函数"""
        try:
            if chunk:
                queue.put_nowait(("data", chunk))
        except Exception as e:
            queue.put_nowait(("error", e))
    
    try:
        # 准备请求数据
        request_data = {
            "model": "gpt-5",
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
            request_timeout=300.0,
            streaming_callback=streaming_callback
        )
        
        if response.code != 200:
            raise ValueError(f"request vision api failed code: {response.code}, msg: {response.body}")
        
        # 处理流式数据
        buffer = b""
        response_complete = False
        
        while not response_complete or not queue.empty():
            try:
                # 从队列获取数据，设置超时避免无限等待
                # 如果响应已完成且队列为空，则退出
                if response_complete and queue.empty():
                    break
                    
                item_type, item_data = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                if item_type == "error":
                    raise item_data
                
                buffer += item_data
                
                # 解析 SSE 格式的数据
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    # SSE 格式: data: {...} 或 data: [DONE]
                    if line.startswith(b"data: "):
                        data_str = line[6:].decode("utf-8")
                        
                        if data_str == "[DONE]":
                            cost_time = time.time() - begin_time
                            logger.info(f"vision api stream total cost time: {cost_time:.2f}s")
                            http_client.close()
                            return
                        
                        try:
                            chunk = json.loads(data_str)
                            yield chunk
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse chunk JSON: {e}, data: {data_str}")
                            continue
                
            except asyncio.TimeoutError:
                # fetch 返回后，标记响应已完成
                response_complete = True
                # 继续处理队列中剩余的数据
                if queue.empty():
                    break
                continue
        
        # 处理剩余的 buffer
        if buffer:
            for line in buffer.split(b"\n"):
                line = line.strip()
                if line.startswith(b"data: "):
                    data_str = line[6:].decode("utf-8")
                    if data_str != "[DONE]":
                        try:
                            chunk = json.loads(data_str)
                            print(data_str)
                            yield chunk
                        except json.JSONDecodeError:
                            pass
        
        cost_time = time.time() - begin_time
        logger.info(f"vision api stream total cost time: {cost_time:.2f}s")
        http_client.close()
        
    except Exception as e:
        logger.error(f"vision api stream error: {str(e)}")
        import traceback
        logger.error(f"vision api stream error traceback: {traceback.format_exc()}")
        http_client.close()
        raise


async def req_gpt_by_messages_stream(message_list):
    """
    流式请求 GPT API（使用消息列表），返回异步生成器，yield OpenAI API 的原始 chunk
    """
    http_client = AsyncHTTPClient()
    begin_time = time.time()
    queue = asyncio.Queue()
    
    def streaming_callback(chunk):
        """处理流式响应的回调函数"""
        try:
            if chunk:
                queue.put_nowait(("data", chunk))
        except Exception as e:
            queue.put_nowait(("error", e))
    
    try:
        # 准备请求数据
        request_data = {
            "model": MODEL_NAME,
            "messages": message_list,
            "stream": True
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
            request_timeout=300.0,
            streaming_callback=streaming_callback
        )
        
        if response.code != 200:
            raise ValueError(f"request vision api failed code: {response.code}, msg: {response.body}")
        
        # 处理流式数据
        buffer = b""
        response_complete = False
        
        while not response_complete or not queue.empty():
            try:
                # 从队列获取数据，设置超时避免无限等待
                # 如果响应已完成且队列为空，则退出
                if response_complete and queue.empty():
                    break
                    
                item_type, item_data = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                if item_type == "error":
                    raise item_data
                
                buffer += item_data
                
                # 解析 SSE 格式的数据
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    # SSE 格式: data: {...} 或 data: [DONE]
                    if line.startswith(b"data: "):
                        data_str = line[6:].decode("utf-8")
                        
                        if data_str == "[DONE]":
                            cost_time = time.time() - begin_time
                            logger.info(f"vision api stream total cost time: {cost_time:.2f}s")
                            http_client.close()
                            return
                        
                        try:
                            chunk = json.loads(data_str)
                            yield chunk
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse chunk JSON: {e}, data: {data_str}")
                            continue
                
            except asyncio.TimeoutError:
                # fetch 返回后，标记响应已完成
                response_complete = True
                # 继续处理队列中剩余的数据
                if queue.empty():
                    break
                continue
        
        # 处理剩余的 buffer
        if buffer:
            for line in buffer.split(b"\n"):
                line = line.strip()
                if line.startswith(b"data: "):
                    data_str = line[6:].decode("utf-8")
                    if data_str != "[DONE]":
                        try:
                            chunk = json.loads(data_str)
                            yield chunk
                        except json.JSONDecodeError:
                            pass
        
        cost_time = time.time() - begin_time
        logger.info(f"vision api stream total cost time: {cost_time:.2f}s")
        http_client.close()
        
    except Exception as e:
        logger.error(f"vision api stream error: {str(e)}")
        import traceback
        logger.error(f"vision api stream error traceback: {traceback.format_exc()}")
        http_client.close()
        raise

asyncio.run(req_gpt_stream("", "帮我写一首100字的关于狂的作文"))
