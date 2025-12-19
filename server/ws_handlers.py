import json
import asyncio
import traceback
from utils.logger import logger
import login as login
import proto as proto
import pet as pet
import exam as exam

class ws_handlers:
    def __init__(self, session):
        self.player: dict = {}
        self.session = session
        self.handlers = {}
        self.register_handlers()

    def register_handlers(self):
        self.handlers[proto.sign_in_c2s.id] = login.sign_in
        self.handlers[proto.sign_up_c2s.id] = login.sign_up
        self.handlers[proto.pet_info_c2s.id] = pet.get_pet_info
        self.handlers[proto.pet_question_generate_c2s.id] = exam.generate_exam
        self.handlers[proto.pet_question_submit_c2s.id] = exam.submit_exam
        self.handlers[proto.pet_question_final_submit_c2s.id] = exam.final_submit_exam

    def cleanup(self):
        if self.session is not None:
            self.session = None
        self.handlers.clear()

    async def handle(self, body):
        try:
            msg_dict = json.loads(body)
            if "id" not in msg_dict:
                logger.error(f"request_id: {self.session.request_id}, msg_id not found in {msg_dict}")
                self.session.send_data(proto.error_message_s2c(-1, "msg_id not found in {msg_dict}").to_dict())
                return
            if msg_dict["id"] not in self.handlers:
                logger.error(f"request_id: {self.session.request_id}, msg_id {msg_dict['id']} not found in handlers")
                self.session.send_data(proto.error_message_s2c(-1, "msg_id {msg_dict['id']} not found in handlers").to_dict())
                return
            res = await self.handlers[msg_dict["id"]](self.player, msg_dict)
            self.session.send_data(res)
        except Exception as e:
            logger.error(f"request_id: {self.session.request_id}, body: {body}, error: {str(e)}, traceback: {traceback.format_exc()}")
    
    async def chat(self, msg_dict):
        try:
            logger.info(f"request_id: {self.session.request_id}, body: {json.dumps(msg_dict, ensure_ascii=False)}")
            msg = msg_proto.msg_chat()
            msg.build_c2s_msg(msg_dict)
            # 创建意图分析工作流
            analysis_flow:chat_analysis_flow = chat_analysis_flow(session=self.session, agents=[chat_analysis_agent(session=self.session)])
            create_type, create_list = await analysis_flow.execute(msg.content)
            result = ""
            if create_type == "flow":
                flow_list = []
                for flow_name in create_list:
                    flow_list.append(flow_manager.build_flow(self.session, name=flow_name, agents=[]))
                for flow in flow_list:
                    result = await flow.execute(msg.content)
                    break
            elif create_type == "agent":
                flow:PlanningFlow = PlanningFlow(session=self.session, agents=create_list)
                result = await flow.execute(msg.content)
            else:
                logger.error(f"request_id: {self.session.request_id}, chat_analysis_flow process none")
                result = "抱歉，我没有理解到您的需求，是否可以再详细描述一下？"
            if not result:
                return base_proto.msg_resp(msg_dict["msg_id"], self.session.request_id, {}, base_proto.CODE.PROCESS_ERROR).to_str()
            logger.info(f"request_id: {self.session.request_id}, result: {json.dumps(result, ensure_ascii=False)}")
            return base_proto.msg_resp(msg_dict["msg_id"], self.session.request_id, result, base_proto.CODE.SUCCESS).to_str()
        except Exception as e:
            logger.error(f"request_id: {self.session.request_id}, body: {msg_dict}, error: {str(e)}, traceback: {traceback.format_exc()}")
            return "抱歉，处理过程中出现错误，请稍后再试。"
  