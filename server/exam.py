import os
import json
import random
import time
from proto import proto
from login import get_user_dir
from config.question_cfg import QUESTION_CFG
from utils.logger import logger

def get_exam_file_path(username: str) -> str:
    """获取试卷数据文件路径"""
    return os.path.join(get_user_dir(username), "exam.json")

def load_exam_data(username: str) -> dict:
    """加载试卷数据"""
    exam_file = get_exam_file_path(username)
    if os.path.exists(exam_file):
        try:
            with open(exam_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load exam data for {username}: {e}")
            return {}
    return {}

def save_exam_data(username: str, exam_data: dict):
    """保存试卷数据"""
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    exam_file = get_exam_file_path(username)
    try:
        with open(exam_file, 'w', encoding='utf-8') as f:
            json.dump(exam_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save exam data for {username}: {e}")
        raise

async def generate_exam(player: dict, msg_dict: dict):
    """生成试卷"""
    try:
        # 检查玩家是否已登录
        if not player or not player.get("username"):
            resp = proto.pet_exam_generate_s2c(code=-1, message="请先登录")
            return resp.to_dict()
        
        # 获取请求参数
        pet_id = msg_dict.get("pet_id", -1)
        exam_type = msg_dict.get("exam_type", -1)
        
        if pet_id == -1:
            resp = proto.pet_exam_generate_s2c(code=-1, message="宠物ID不能为空")
            return resp.to_dict()
        
        if exam_type == -1:
            resp = proto.pet_exam_generate_s2c(code=-1, message="试卷类型不能为空")
            return resp.to_dict()
        
        # 检查宠物是否存在
        pets_data = player.get("pets", [])
        pet_exists = False
        for pet in pets_data:
            if pet.get("id") == pet_id:
                pet_exists = True
                break
        
        if not pet_exists:
            resp = proto.pet_exam_generate_s2c(code=-1, message="宠物不存在")
            return resp.to_dict()
        
        # 从配置中获取对应类型的题目
        exam_type_str = str(exam_type)
        if exam_type_str not in QUESTION_CFG:
            resp = proto.pet_exam_generate_s2c(code=-1, message=f"试卷类型 {exam_type} 不存在")
            return resp.to_dict()
        
        question_list = QUESTION_CFG[exam_type_str]
        if len(question_list) < 10:
            resp = proto.pet_exam_generate_s2c(code=-1, message=f"题目数量不足，需要至少10道题")
            return resp.to_dict()
        
        # 随机选择10道题
        selected_questions = random.sample(question_list, 10)
        
        # 构建响应数据
        resp_data = proto.pet_exam_generate_s2c_data()
        exam_info = proto.pet_exam_generate_s2c_data_exam()
        exam_info.type = exam_type
        exam_info.submit = 0  # 未提交
        exam_info.fresh_time = int(time.time()) + 24 * 60 * 60  # 24小时后可重新生成
        
        # 构建题目列表
        exam_info.questions = []
        for q in selected_questions:
            question = proto.pet_exam_generate_s2c_data_exam_questions()
            question.content = q.get("content", "")
            question.options = q.get("options", [])
            question.right_answer = q.get("right_answer", -1)
            question.answer = -1  # 玩家未作答
            question.is_right = -1  # 未评判
            question.analysis = ""  # 解析为空
            exam_info.questions.append(question)
        
        resp_data.exam = [exam_info]
        
        # 保存试卷数据到本地
        username = player.get("username")
        exam_data = load_exam_data(username)
        
        # 试卷数据结构：{pet_id: {exam_type: exam_data}}
        # 使用字符串作为key以保持JSON兼容性
        pet_id_str = str(pet_id)
        if pet_id_str not in exam_data:
            exam_data[pet_id_str] = {}
        
        # 转换为可序列化的字典格式保存
        exam_data[pet_id_str][exam_type_str] = {
            "type": exam_info.type,
            "submit": exam_info.submit,
            "fresh_time": exam_info.fresh_time,
            "questions": [
                {
                    "content": q.content,
                    "options": q.options,
                    "right_answer": q.right_answer,
                    "answer": q.answer,
                    "is_right": q.is_right,
                    "analysis": q.analysis
                }
                for q in exam_info.questions
            ]
        }
        
        save_exam_data(username, exam_data)
        
        # 返回成功响应
        resp = proto.pet_exam_generate_s2c(code=0, message="")
        resp.data = resp_data
        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"generate_exam error: {e}")
        resp = proto.pet_exam_generate_s2c(code=-1, message=f"生成试卷失败: {str(e)}")
        return resp.to_dict()


async def submit_exam(player: dict, msg_dict: dict):
    pass

async def final_submit_exam(player: dict, msg_dict: dict):
    pass