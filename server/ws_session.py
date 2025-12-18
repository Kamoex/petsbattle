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
from app.manus.schema import Memory

class ws_session(tornado.websocket.WebSocketHandler):
    def init(self):
        self.handlers = ws_handlers(self)
        os.makedirs(f"workspace/{self.request_id}", exist_ok=True)

    def check_origin(self, origin):
        # 允许跨域访问
        return True  
    
    async def open(self):
        try:
            self.request_id = str(uuid.uuid4())
            logger.info(f"request_id: {self.request_id} connect success")
            self.init()
            # asyncio.create_task(self.process())
            resp = msg_resp(server.ws_proto.PROTO.MSG_CONNECT_SUCCESS, self.request_id, {}, CODE.SUCCESS)
            self.send_data(resp.to_str())
        except Exception as e:
            logger.error(f"request_id: {self.request_id}, open error: {str(e)}, traceback: {traceback.format_exc()}")
            self.close()

    async def on_message(self, message):
        try:
            if isinstance(message, str):
                if message == "ping":
                    logger.info(f"request_id: {self.request_id}, message: {message}")
                    return
                if self.my_test(message):
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
        # self.timer.stop()
        self.handlers.cleanup()
        # if os.path.exists(f"workspace/{self.request_id}"):
        #     shutil.rmtree(f"workspace/{self.request_id}")

    def send_data(self, content:str):
        try:
            self.write_message(content)
        except Exception as e:
            logger.warning(f"request_id: {self.request_id}, send_data error: {str(e)}, content: {content}")
            self.close()




    def my_test(self, message) -> bool:
        try:
            msg_dict = json.loads(message)
            if msg_dict.get("content", "") == "一":
                res_json = {}
                res_json["text"] = "报告生成完成，请点击以下链接进行查看：\nObserved output of cmd `markdown_to_pdf` executed:\nhttps://aigc-plat-test.oss-cn-beijing.aliyuncs.com/manus/14959552-d3e1-4b05-8470-e07dc606bf56.pdf"
                res_json["text_type"] = "text"
                res_json["flow"] = "data_analysis_flow"
                self.send_data(msg_resp(1000101, self.request_id, res_json, CODE.SUCCESS).to_str())
            elif msg_dict.get("content", "") == "二":
                res_json = {}
                res_json["text"] = {
                    "title": "天津五日游",
                    "train_ticket": {
                        "goto": {
                            "from": "北京",
                            "to": "天津",
                            "departure_date": "2025-08-19 06:00",
                            "arrival_date": "2025-08-19 06:30",
                            "train_number": "C2551",
                            "price": "54.5",
                            "seat_type": "二等座"
                        },
                        "goback": {
                            "from": "天津",
                            "to": "北京",
                            "departure_date": "2025-08-23 18:00",
                            "arrival_date": "2025-08-23 18:30",
                            "train_number": "C2552",
                            "price": "54.5",
                            "seat_type": "二等座"
                        },
                        "ticket_url": "https://www.12306.cn/index/"
                    },
                    "weather": {
                        "天津": [
                            {
                                "date": "2025-08-19",
                                "temperature": "无法获取",
                                "condition": "无法获取",
                                "wind": "无法获取",
                                "tips": "请根据实际天气情况准备衣物。"
                            }
                        ]
                    },
                    "plan_list": [
                        {
                            "date": "2025-08-19",
                            "title": "天津市区游",
                            "introduction": "第一天游览天津市区的著名景点。",
                            "scenic_spot_list": [
                                {
                                    "name": "天津之眼",
                                    "introduction": "天津之眼是位于天津市的摩天轮，享有国家级景点的美誉。",
                                    "image_url": "http://store.is.autonavi.com/showpic/5aff6d3ff23183316cbf3705b47d2398",
                                    "reference_url": "https://baike.baidu.com/item/%E5%A4%A9%E6%B4%A5%E4%B9%8B%E7%9C%BC",
                                    "tour_duration": "2小时",
                                    "map_mark": {}
                                },
                                {
                                    "name": "古文化街旅游区",
                                    "introduction": "古文化街是天津市的著名旅游景点，拥有丰富的文化底蕴。",
                                    "image_url": "http://aos-cdn-image.amap.com/sns/ugccomment/ff7b454f-3bbe-4b79-b4f0-e423ee85ccbc.jpg",
                                    "reference_url": "https://baike.baidu.com/item/%E5%8F%A4%E6%96%87%E5%8C%96%E8%A1%97",
                                    "tour_duration": "3小时",
                                    "map_mark": {
                                        "lat": 39.143888,
                                        "lng": 117.192187
                                    }
                                }
                            ],
                            "transportation_between_scenic_spots": "景点之间可步行或打车，单程约10-15分钟。"
                        },
                        {
                            "date": "2025-08-20",
                            "title": "天津文化体验",
                            "introduction": "第二天体验天津的文化和历史。",
                            "scenic_spot_list": [
                                {
                                    "name": "五大道文化旅游区",
                                    "introduction": "五大道是天津市的文化旅游区，展示了丰富的历史文化。",
                                    "image_url": "http://store.is.autonavi.com/showpic/3138223e49d8298d3b62d0b2105acc6b",
                                    "reference_url": "https://baike.baidu.com/item/%E4%BA%94%E5%A4%A7%E9%81%93",
                                    "tour_duration": "3小时",
                                    "map_mark": {
                                        "lat": 39.110567,
                                        "lng": 117.203601
                                    }
                                },
                                {
                                    "name": "意大利风情旅游区",
                                    "introduction": "意大利风情区是天津市的特色旅游区，充满异国风情。",
                                    "image_url": "http://store.is.autonavi.com/showpic/52d1de4e7ea0cc8f42dce4c12dd3a3cc",
                                    "reference_url": "https://baike.baidu.com/item/%E6%84%8F%E5%A4%A7%E5%88%A9%E9%A3%8E%E6%83%85%E5%8C%BA",
                                    "tour_duration": "2小时",
                                    "map_mark": {
                                        "lat": 39.134543,
                                        "lng": 117.197435
                                    }
                                }
                            ],
                            "transportation_between_scenic_spots": "景点之间可步行或打车，单程约10-15分钟。"
                        },
                        {
                            "date": "2025-08-21",
                            "title": "天津美食之旅",
                            "introduction": "第三天品尝天津的特色美食。",
                            "scenic_spot_list": [
                                {
                                    "name": "南市食品街",
                                    "introduction": "南市食品街是天津市的特色商业街，提供各种美食。",
                                    "image_url": "http://store.is.autonavi.com/showpic/d586b6770bdc8b5e3445a3d4b108ac93",
                                    "reference_url": "https://baike.baidu.com/item/%E5%8D%97%E5%B8%82%E9%A3%9F%E5%93%81%E8%A1%97",
                                    "tour_duration": "3小时",
                                    "map_mark": {
                                        "lat": 39.132956,
                                        "lng": 117.183938
                                    }
                                }
                            ],
                            "transportation_between_scenic_spots": "建议步行游览，体验街头美食。"
                        },
                        {
                            "date": "2025-08-22",
                            "title": "天津休闲购物",
                            "introduction": "第四天在天津购物和休闲。",
                            "scenic_spot_list": [],
                            "transportation_between_scenic_spots": "可选择在市区购物中心购物，交通便利。"
                        },
                        {
                            "date": "2025-08-23",
                            "title": "天津自由活动",
                            "introduction": "最后一天自由活动，享受天津的城市风光。",
                            "scenic_spot_list": [],
                            "transportation_between_scenic_spots": "可选择在市区自由活动，交通便利。"
                        }
                    ],
                    "hotel_list": [
                        {
                            "name": "天津橄榄绿酒店",
                            "address": "一经路馨月湾59号",
                            "introduction": "天津橄榄绿酒店是一家经济型连锁酒店，提供舒适的住宿环境。",
                            "image_url": "http://store.is.autonavi.com/showpic/ff68675582cadd86156cf123be8d824d",
                            "reference_url": "https://baike.baidu.com/item/%E6%A9%84%E6%A6%84%E7%BB%BF%E9%85%92%E5%BA%97",
                            "price": "200/晚",
                            "map_mark": {
                                "lat": 39.242945,
                                "lng": 117.798961
                            }
                        },
                        {
                            "name": "7天连锁酒店(天津机场空港1号桥店)",
                            "address": "华明街华兴路10号1号楼",
                            "introduction": "7天连锁酒店提供经济实惠的住宿选择，靠近湿地公园。",
                            "image_url": "http://store.is.autonavi.com/showpic/243724c649496c32a9d76e5aeaed8a7f",
                            "reference_url": "https://baike.baidu.com/item/7%E5%A4%A9%E9%85%92%E5%BA%97",
                            "price": "150/晚",
                            "map_mark": {
                                "lat": 39.168069,
                                "lng": 117.362649
                            }
                        }
                    ],
                    "restaurant_list": [
                        {
                            "name": "狗不理(水上旗舰店)",
                            "address": "水上公园北道金龙公寓16号(天塔地铁站C口步行190米)",
                            "introduction": "狗不理包子是天津的传统名吃，以其独特的口味和制作工艺闻名。",
                            "image_url": "http://store.is.autonavi.com/showpic/29e00dd63229169a2dd19ee8796ecc1f",
                            "reference_url": "https://baike.baidu.com/item/%E7%8B%97%E4%B8%8D%E7%90%86",
                            "price_range": "人均消费约80元",
                            "map_mark": {
                                "lat": 39.095944,
                                "lng": 117.174665
                            }
                        }
                    ],
                    "tips": {
                        "最佳旅游季节": "天津四季分明，春秋季节气候宜人，适合旅游。",
                        "交通建议": "天津市内交通便利，建议使用地铁和公交车出行。"
                    }
                }
                res_json["text_type"] = "travel_flow"
                res_json["flow"] = "travel_flow"
                self.send_data(msg_resp(1000101, self.request_id, res_json, CODE.SUCCESS).to_str())
            elif msg_dict.get("content", "") == "三":
                    res_json = {}
                    res_json["text"] = f"北京 -> 天津 日期：2025-08-26 车次：G666：订单已成功生成！请在12306网站上查看订单详情并进行付款。"
                    res_json["text_type"] = "ticket_flow"
                    res_json["flow"] = "ticket_flow"
                    self.send_data(msg_resp(1000101, self.request_id, res_json, CODE.SUCCESS).to_str())
            else:
                return False
            return True
        except Exception as e:
            logger.error(f"request_id: {self.request_id}, my_test error: {str(e)}, traceback: {traceback.format_exc()}")
            return False