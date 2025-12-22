import os
import json
import random
import time
import asyncio
import traceback
from my_proto import proto
from login import get_user_dir
from config.question_cfg import QUESTION_CFG
from agent.agent import agent
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
    """提交单题答案"""
    try:
        # 获取请求参数
        pet_id = msg_dict.get("pet_id", -1)
        exam_type = msg_dict.get("exam_type", -1)
        question_data = msg_dict.get("question", {})
        
        if pet_id == -1:
            resp = proto.pet_exam_submit_s2c(code=-1, message="宠物ID不能为空")
            return resp.to_dict()
        
        if exam_type == -1:
            resp = proto.pet_exam_submit_s2c(code=-1, message="试卷类型不能为空")
            return resp.to_dict()
        
        if not question_data:
            resp = proto.pet_exam_submit_s2c(code=-1, message="题目信息不能为空")
            return resp.to_dict()
        
        question_id = question_data.get("id", -1)
        answer = question_data.get("answer", -1)
        
        if question_id == -1:
            resp = proto.pet_exam_submit_s2c(code=-1, message="题目ID不能为空")
            return resp.to_dict()
        
        # 加载试卷数据
        username = player.get("username")
        exam_data = load_exam_data(username)
        
        pet_id_str = str(pet_id)
        exam_type_str = str(exam_type)
        
        # 检查试卷是否存在
        if pet_id_str not in exam_data or exam_type_str not in exam_data[pet_id_str]:
            resp = proto.pet_exam_submit_s2c(code=-1, message="试卷不存在，请先生成试卷")
            return resp.to_dict()
        
        exam_info = exam_data[pet_id_str][exam_type_str]
        questions = exam_info.get("questions", [])
        
        # 检查题目索引是否有效
        if int(question_id) < 0 or int(question_id) >= len(questions):
            resp = proto.pet_exam_submit_s2c(code=-1, message="题目ID无效")
            return resp.to_dict()
        
        # 更新题目答案
        questions[question_id]["answer"] = answer
        
        # 保存试卷数据
        save_exam_data(username, exam_data)
        
        # 返回成功响应
        resp = proto.pet_exam_submit_s2c(code=0, message="")
        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"submit_exam error: {e}")
        resp = proto.pet_exam_submit_s2c(code=-1, message=f"提交答案失败: {str(e)}")
        return resp.to_dict()


async def final_submit_exam(player: dict, msg_dict: dict):
    """最终提交试卷，使用agent并发获取题目解析"""
    try:
        # 获取请求参数
        pet_id = msg_dict.get("pet_id", -1)
        exam_type = msg_dict.get("exam_type", -1)
        
        if pet_id == -1:
            resp = proto.pet_exam_final_submit_s2c(code=-1, message="宠物ID不能为空")
            return resp.to_dict()
        
        if exam_type == -1:
            resp = proto.pet_exam_final_submit_s2c(code=-1, message="试卷类型不能为空")
            return resp.to_dict()
        
        # 加载试卷数据
        username = player.get("username")
        exam_data = load_exam_data(username)
        
        pet_id_str = str(pet_id)
        exam_type_str = str(exam_type)
        
        # 检查试卷是否存在
        if pet_id_str not in exam_data or exam_type_str not in exam_data[pet_id_str]:
            resp = proto.pet_exam_final_submit_s2c(code=-1, message="试卷不存在，请先生成试卷")
            return resp.to_dict()
        
        exam_info = exam_data[pet_id_str][exam_type_str]
        questions = exam_info.get("questions", [])
        
        if len(questions) != 10:
            resp = proto.pet_exam_final_submit_s2c(code=-1, message="试卷题目数量不正确")
            return resp.to_dict()
        
        # 创建agent的system prompt
        system_prompt = """你是一个专业的语文题目解析助手。请根据给定的题目、选项、正确答案和玩家答案，判断玩家答案是否正确，并提供详细的解析。

要求：
1. 判断玩家答案是否正确（is_right: 0表示错误，1表示正确）
2. 提供详细的题目解析（analysis），包括：
   - 正确答案的解释
   - 如果玩家答错，说明错误原因
   - 相关知识点说明

请以JSON格式返回结果，格式如下：
{
    "is_right": 0或1,
    "analysis": "详细的解析内容"
}

只返回JSON，不要返回其他内容。"""
        
        # 创建10个agent并发执行
        async def process_question(question_idx: int, question: dict):
            """处理单道题目"""
            try:
                # 构建content字符串
                content = f"""题目：{question.get('content', '')}

选项：
"""
                options = question.get('options', [])
                for i, option in enumerate(options):
                    content += f"{i}. {option}\n"
                
                right_answer_idx = int(question.get('right_answer', -1))
                player_answer_idx = int(question.get('answer', -1))
                
                if right_answer_idx >= 0 and right_answer_idx < len(options):
                    content += f"\n正确答案：{right_answer_idx} ({options[right_answer_idx]})"
                
                if player_answer_idx >= 0 and player_answer_idx < len(options):
                    content += f"\n玩家答案：{player_answer_idx} ({options[player_answer_idx]})"
                else:
                    content += f"\n玩家答案：未作答"
                
                # 创建agent并执行
                ag = agent(system_prompt=system_prompt, stream=False)
                result = await ag.execute(content)
                
                # 解析JSON结果
                try:
                    # 尝试提取JSON部分（可能包含markdown代码块）
                    result = result.strip()
                    if result.startswith("```json"):
                        result = result[7:]
                    if result.startswith("```"):
                        result = result[3:]
                    if result.endswith("```"):
                        result = result[:-3]
                    result = result.strip()
                    
                    result_json = json.loads(result)
                    is_right = result_json.get("is_right", 0)
                    analysis = result_json.get("analysis", "")
                    
                    # 验证is_right的值
                    if is_right not in [0, 1]:
                        # 如果玩家答案等于正确答案，则正确
                        is_right = 1 if player_answer_idx == right_answer_idx else 0
                    
                    return {
                        "index": question_idx,
                        "is_right": is_right,
                        "analysis": analysis
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent result for question {question_idx}: {result}, error: {e}")
                    # 如果解析失败，根据答案判断是否正确
                    is_right = 1 if player_answer_idx == right_answer_idx else 0
                    return {
                        "index": question_idx,
                        "is_right": is_right,
                        "analysis": "解析生成失败，请稍后再试。"
                    }
            except Exception as e:
                logger.error(f"Error processing question {question_idx}: {e} {traceback.format_exc()}")
                # 出错时根据答案判断是否正确
                right_answer_idx = question.get('right_answer', -1)
                player_answer_idx = question.get('answer', -1)
                is_right = 1 if player_answer_idx == right_answer_idx else 0
                return {
                    "index": question_idx,
                    "is_right": is_right,
                    "analysis": f"处理出错: {str(e)}"
                }
        
        # 并发执行所有题目
        tasks = [process_question(i, q) for i, q in enumerate(questions)]
        results = await asyncio.gather(*tasks)
        
        # 整理结果，按索引排序
        results.sort(key=lambda x: x["index"])
        
        # 计算答对题数和属性增加值
        correct_count = sum(1 for r in results if r["is_right"] == 1)
        attr_increase = correct_count  # 答对1题+1，答对10题+10
        
        # 更新试卷数据
        for i, result in enumerate(results):
            questions[i]["is_right"] = result["is_right"]
            questions[i]["analysis"] = result["analysis"]
        
        exam_info["submit"] = 1  # 标记为已提交
        exam_data[pet_id_str][exam_type_str] = exam_info
        save_exam_data(username, exam_data)
        
        # 更新宠物属性（需要加载宠物数据）
        from login import load_pets_data, save_pets_data
        pets_data = player.get("pets", [])
        if not pets_data:
            pets_data = load_pets_data(username)
            player["pets"] = pets_data
        
        # 找到对应的宠物并更新属性
        pet_data = None
        for pet in pets_data:
            if pet.get("id") == pet_id:
                pet_data = pet
                break
        
        if pet_data:
            # 更新对应类型的属性
            for attr in pet_data.get("attr", []):
                if attr.get("id") == exam_type:
                    attr["value"] = attr.get("value", 0) + attr_increase
                    break
            
            # 保存宠物数据
            save_pets_data(username, pets_data)
            player["pets"] = pets_data
        
        # 构建响应数据
        resp_data = proto.pet_exam_final_submit_s2c_data()
        exam_result = proto.pet_exam_final_submit_s2c_data_exam()
        exam_result.pet_id = pet_id
        exam_result.type = exam_type
        
        # 设置属性增加值
        attr_info = proto.pet_exam_final_submit_s2c_data_exam_attr()
        attr_info.id = exam_type
        attr_info.value = attr_increase
        exam_result.attr = attr_info
        
        # 设置题目结果
        exam_result.questions = []
        for result in results:
            question_result = proto.pet_exam_final_submit_s2c_data_exam_questions()
            question_result.is_right = result["is_right"]
            question_result.analysis = result["analysis"]
            exam_result.questions.append(question_result)
        
        resp_data.exam = exam_result
        
        # 返回成功响应
        resp = proto.pet_exam_final_submit_s2c(code=0, message="")
        resp.data = resp_data
        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"final_submit_exam error: {e}")
        logger.error(f"traceback: {traceback.format_exc()}")
        resp = proto.pet_exam_final_submit_s2c(code=-1, message=f"提交试卷失败: {str(e)}")
        return resp.to_dict()