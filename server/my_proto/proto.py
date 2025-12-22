"""
自动生成的协议类
由 convert.py 从 proto.json 生成
"""

# from __future__ import annotations
from typing import List, Any, Optional


class sign_in_s2c_data:
    def __init__(self):
        self.player: sign_in_s2c_data_player = None
        self.pet: List[sign_in_s2c_data_pet] = []

    def to_dict(self) -> dict:
        result = {}
        result['player'] = self.player.to_dict() if self.player is not None else None
        result['pet'] = [item.to_dict() for item in self.pet] if self.pet is not None else None
        return result


class sign_in_s2c_data_player:
    def __init__(self):
        self.name: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['name'] = self.name
        return result


class sign_in_s2c_data_pet:
    def __init__(self):
        self.id: int = -1
        self.name: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['name'] = self.name
        return result


class pet_info_s2c_data:
    def __init__(self):
        self.pet: pet_info_s2c_data_pet = None

    def to_dict(self) -> dict:
        result = {}
        result['pet'] = self.pet.to_dict() if self.pet is not None else None
        return result


class pet_info_s2c_data_pet:
    def __init__(self):
        self.id: int = -1
        self.name: str = ""
        self.nickname: str = ""
        self.sex: int = -1
        self.type: str = ""
        self.character: List[str] = []
        self.attr: List[pet_info_s2c_data_pet_attr] = []

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['name'] = self.name
        result['nickname'] = self.nickname
        result['sex'] = self.sex
        result['type'] = self.type
        result['character'] = self.character
        result['attr'] = [item.to_dict() for item in self.attr] if self.attr is not None else None
        return result


class pet_info_s2c_data_pet_attr:
    def __init__(self):
        self.id: int = -1
        self.value: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['value'] = self.value
        return result


class pet_exam_generate_s2c_data:
    def __init__(self):
        self.exam: List[pet_exam_generate_s2c_data_exam] = []

    def to_dict(self) -> dict:
        result = {}
        result['exam'] = [item.to_dict() for item in self.exam] if self.exam is not None else None
        return result


class pet_exam_generate_s2c_data_exam:
    def __init__(self):
        self.type: int = -1
        self.questions: List[pet_exam_generate_s2c_data_exam_questions] = []
        self.submit: int = -1
        self.fresh_time: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['type'] = self.type
        result['questions'] = [item.to_dict() for item in self.questions] if self.questions is not None else None
        result['submit'] = self.submit
        result['fresh_time'] = self.fresh_time
        return result


class pet_exam_generate_s2c_data_exam_questions:
    def __init__(self):
        self.content: str = ""
        self.options: List[str] = []
        self.right_answer: int = -1
        self.answer: int = -1
        self.is_right: int = -1
        self.analysis: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['content'] = self.content
        result['options'] = self.options
        result['right_answer'] = self.right_answer
        result['answer'] = self.answer
        result['is_right'] = self.is_right
        result['analysis'] = self.analysis
        return result


class pet_exam_submit_c2s_question:
    def __init__(self):
        self.id: int = -1
        self.answer: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['answer'] = self.answer
        return result


class pet_exam_final_submit_s2c_data:
    def __init__(self):
        self.exam: pet_exam_final_submit_s2c_data_exam = None

    def to_dict(self) -> dict:
        result = {}
        result['exam'] = self.exam.to_dict() if self.exam is not None else None
        return result


class pet_exam_final_submit_s2c_data_exam:
    def __init__(self):
        self.pet_id: int = -1
        self.type: int = -1
        self.attr: pet_exam_final_submit_s2c_data_exam_attr = None
        self.questions: List[pet_exam_final_submit_s2c_data_exam_questions] = []

    def to_dict(self) -> dict:
        result = {}
        result['pet_id'] = self.pet_id
        result['type'] = self.type
        result['attr'] = self.attr.to_dict() if self.attr is not None else None
        result['questions'] = [item.to_dict() for item in self.questions] if self.questions is not None else None
        return result


class pet_exam_final_submit_s2c_data_exam_attr:
    def __init__(self):
        self.id: int = -1
        self.value: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['value'] = self.value
        return result


class pet_exam_final_submit_s2c_data_exam_questions:
    def __init__(self):
        self.is_right: int = -1
        self.analysis: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['is_right'] = self.is_right
        result['analysis'] = self.analysis
        return result


class pet_battle_match_s2c_data:
    def __init__(self):
        self.enemy_player_name: str = ""
        self.enemy_pet_id: int = -1
        self.enemy_pet_name: str = ""
        self.enemy_pet_sex: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['enemy_player_name'] = self.enemy_player_name
        result['enemy_pet_id'] = self.enemy_pet_id
        result['enemy_pet_name'] = self.enemy_pet_name
        result['enemy_pet_sex'] = self.enemy_pet_sex
        return result


class pet_battle_turn_s2c_data:
    def __init__(self):
        self.turn: int = -1
        self.hp: int = -1
        self.enemy_hp: int = -1
        self.status: str = ""
        self.question: str = ""
        self.answers: str = ""
        self.enemy_answers: str = ""
        self.correct_answer: str = ""
        self.winner_name: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['turn'] = self.turn
        result['hp'] = self.hp
        result['enemy_hp'] = self.enemy_hp
        result['status'] = self.status
        result['question'] = self.question
        result['answers'] = self.answers
        result['enemy_answers'] = self.enemy_answers
        result['correct_answer'] = self.correct_answer
        result['winner_name'] = self.winner_name
        return result


class pet_battle_result_s2c_data:
    def __init__(self):
        self.attr: List[pet_battle_result_s2c_data_attr] = []

    def to_dict(self) -> dict:
        result = {}
        result['attr'] = [item.to_dict() for item in self.attr] if self.attr is not None else None
        return result


class pet_battle_result_s2c_data_attr:
    def __init__(self):
        self.id: int = -1
        self.value: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['value'] = self.value
        return result


class error_message_s2c:
    id: int = 1

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        return result


class connect_success_s2c:
    id: int = 1000

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        return result


class sign_in_c2s:
    id: int = 1001

    def __init__(self):
        self.username: str = ""
        self.password: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['username'] = self.username
        result['password'] = self.password
        return result


class sign_in_s2c:
    id: int = 1002

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message
        self.data: sign_in_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result


class sign_up_c2s:
    id: int = 1003

    def __init__(self):
        self.username: str = ""
        self.password: str = ""
        self.name: str = ""

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['username'] = self.username
        result['password'] = self.password
        result['name'] = self.name
        return result


class sign_up_s2c:
    id: int = 1004

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        return result


class pet_info_c2s:
    id: int = 1005

    def __init__(self):
        self.pet_id: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['pet_id'] = self.pet_id
        return result


class pet_info_s2c:
    id: int = 1006

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message
        self.data: pet_info_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result


class pet_question_generate_c2s:
    id: int = 1007

    def __init__(self):
        self.pet_id: int = -1
        self.exam_type: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['pet_id'] = self.pet_id
        result['exam_type'] = self.exam_type
        return result


class pet_exam_generate_s2c:
    id: int = 1008

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message
        self.data: pet_exam_generate_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result


class pet_exam_submit_c2s:
    id: int = 1009

    def __init__(self):
        self.pet_id: int = -1
        self.exam_type: int = -1
        self.question: pet_exam_submit_c2s_question = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['pet_id'] = self.pet_id
        result['exam_type'] = self.exam_type
        result['question'] = self.question.to_dict() if self.question is not None else None
        return result


class pet_exam_submit_s2c:
    id: int = 1010

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        return result


class pet_exam_final_submit_c2s:
    id: int = 1011

    def __init__(self):
        self.pet_id: int = -1
        self.exam_type: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['pet_id'] = self.pet_id
        result['exam_type'] = self.exam_type
        return result


class pet_exam_final_submit_s2c:
    id: int = 1012

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message
        self.data: pet_exam_final_submit_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result


class pet_battle_match_c2s:
    id: int = 1013

    def __init__(self):
        self.pet_id: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['pet_id'] = self.pet_id
        return result


class pet_battle_match_s2c:
    id: int = 1014

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message
        self.data: pet_battle_match_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result


class pet_battle_start_c2s:
    id: int = 1015

    def __init__(self):
        self.pet_id: int = -1

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['pet_id'] = self.pet_id
        return result


class pet_battle_turn_s2c:
    id: int = 1016

    def __init__(self):
        self.data: pet_battle_turn_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result


class pet_battle_result_s2c:
    id: int = 1017

    def __init__(self):
        self.data: pet_battle_result_s2c_data = None

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['data'] = self.data.to_dict() if self.data is not None else None
        return result

class pet_battle_match_cancel_c2s:
    id: int = 1018

    def __init__(self):
        pass

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        return result

class pet_battle_match_cancel_s2c:
    id: int = 1019

    def __init__(self, code: int = -1, message: str = ""):
        self.code: int = code
        self.message: str = message

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['message'] = self.message
        return result