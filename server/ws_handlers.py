import json
import asyncio
import traceback
from utils.logger import logger
import login as login
import my_proto as proto
import pet as pet
import exam as exam
import battle as battle

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
        self.handlers[proto.pet_exam_submit_c2s.id] = exam.submit_exam
        self.handlers[proto.pet_exam_final_submit_c2s.id] = exam.final_submit_exam
        self.handlers[proto.pet_battle_match_c2s.id] = battle.match_battle
        self.handlers[proto.pet_battle_start_c2s.id] = battle.start_battle

    def cleanup(self):
        if self.player and "username" in self.player and self.player["username"] in login.PLAYER_LIST:
            login.PLAYER_LIST.pop(self.player["username"])
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
            # 设置玩家session
            if self.player and "session" not in self.player:
                self.player["session"] = self.session
            self.session.send_data(res)
        except Exception as e:
            logger.error(f"request_id: {self.session.request_id}, body: {body}, error: {str(e)}, traceback: {traceback.format_exc()}")
    