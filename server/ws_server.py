import os
import sys
import tornado.ioloop
import tornado.web
from pathlib import Path
from utils.logger import logger
# sys.path.append(str(Path(os.path.dirname(__file__)).parent))
# print(sys.path)
import ws_session

# 全局变量存储子服务进程
sub_service_process = None

app = tornado.web.Application([
    # WebSocket 路由
    (r'/', ws_session.ws_session),
    
    # HTTP API 路由
    # (r'/agentic-test/agentic/chat/history', ChatHistoryHandler),
    # (r'/agentic-test/agentic/chat/detail', ChatDetailHandler),
    # (r'/agentic-test/agentic/chat/delete', ChatDeleteHandler),
])


# 运行服务器
if __name__ == "__main__":
    
    # 启动WebSocket服务器
    app.listen(9160, address="0.0.0.0")
    logger.info("server start ws://localhost:9160")
    tornado.ioloop.IOLoop.current().start()