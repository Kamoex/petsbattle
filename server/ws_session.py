import os
import time
import json
import uuid
import shutil
import asyncio
import traceback
import tornado.websocket

from ws_handlers import ws_handlers
from utils.logger import logger
from my_proto import proto

class ws_session(tornado.websocket.WebSocketHandler):
    def init(self):
        self.handlers = ws_handlers(self)

    def check_origin(self, origin):
        # 允许跨域访问
        return True  
    
    async def open(self):
        try:
            self.request_id = str(uuid.uuid4())
            logger.info(f"request_id: {self.request_id} connect success")
            self.init()
            # 发送 connect_success
            resp = proto.connect_success_s2c(code=0, message="")
            self.send_data(resp.to_dict())
        except Exception as e:
            logger.error(f"request_id: {self.request_id}, open error: {str(e)}, traceback: {traceback.format_exc()}")
            self.close()

    async def on_message(self, message):
        try:
            if isinstance(message, str):
                if message == "ping":
                    logger.info(f"request_id: {self.request_id}, message: {message}")
                    return
                # 消息分发
                asyncio.create_task(self.handlers.handle(message))
            else:
                logger.error(f"request_id: {self.request_id}, on_message received non-string message: {message}")
        except Exception as e:
            logger.error(f"request_id: {self.request_id}, on_message error: {str(e)}")

    def on_pong(self, data: bytes) -> None:
        """Invoked when the response to a ping frame is received."""
        pass

    def on_ping(self, data: bytes) -> None:
        """Invoked when the a ping frame is received."""
        logger.info(f"request_id: {self.request_id}, on_ping: {str(data)}")
        pass

    def on_close(self):
        logger.info(f"request_id: {self.request_id}, on_close")
        self.handlers.cleanup()

    def send_data(self, content:dict):
        try:
            self.write_message(json.dumps(content, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"request_id: {self.request_id}, send_data error: {str(e)}, content: {content}")
            self.close()
