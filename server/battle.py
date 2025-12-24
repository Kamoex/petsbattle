import asyncio
import random
from my_proto import proto
from utils.logger import logger
import login
import traceback
from agent.agent import agent
import json

async def match_battle(player: dict, msg_dict: dict):
    """宠物战斗匹配"""
    try:
        # 获取请求的宠物ID
        pet_id = msg_dict.get("pet_id", -1)
        if pet_id == -1:
            resp = proto.pet_battle_match_s2c(code=-1, message="宠物ID不能为空")
            return resp.to_dict()
        
        # 查找该玩家的宠物
        pets_data = player.get("pets", [])
        my_pet = None
        for pet in pets_data:
            if pet.get("id") == pet_id:
                my_pet = pet
                break
        
        if my_pet is None:
            resp = proto.pet_battle_match_s2c(code=-1, message="宠物不存在")
            return resp.to_dict()
        
        # 设置当前玩家的匹配状态
        player["battle_matching"] = True
        player["battle_my_pet_id"] = pet_id
        
        # 在 PLAYER_LIST 中查找其他正在匹配的玩家
        enemy_player = None
        for username, p in login.PLAYER_LIST.items():
            if username != player["username"] and p.get("battle_matching") == True:
                enemy_player = p
                break
        
        # 如果没有找到对手，等待其他玩家
        if enemy_player is None:
            resp = proto.pet_battle_match_s2c(code=0, message="")
            resp_data = proto.pet_battle_match_s2c_data()
            resp_data.status = 1
            resp.data = resp_data
            return resp.to_dict()
        
        # 找到对手，配对成功
        enemy_pet_id = enemy_player.get("battle_my_pet_id")
        enemy_pets = enemy_player.get("pets", [])
        enemy_pet = None
        for pet in enemy_pets:
            if pet.get("id") == enemy_pet_id:
                enemy_pet = pet
                break
        
        if enemy_pet is None:
            resp = proto.pet_battle_match_s2c(code=-1, message="对手宠物数据异常")
            return resp.to_dict()
        
        # 双方都设置匹配状态为False，并保存对手信息
        player["battle_matching"] = False
        player["battle_enemy_username"] = enemy_player["username"]
        player["battle_enemy_pet_id"] = enemy_pet_id
        
        enemy_player["battle_matching"] = False
        enemy_player["battle_enemy_username"] = player["username"]
        enemy_player["battle_enemy_pet_id"] = pet_id
        
        # 给当前玩家发送匹配成功消息
        resp_data = proto.pet_battle_match_s2c_data()
        resp_data.status = 2
        resp_data.enemy_player_name = enemy_player.get("name", "")
        resp_data.enemy_pet_id = enemy_pet_id
        resp_data.enemy_pet_name = enemy_pet.get("name", "")
        resp_data.enemy_pet_sex = enemy_pet.get("sex", 0)
        
        resp = proto.pet_battle_match_s2c(code=0, message="匹配成功")
        resp.data = resp_data
        
        # 给对手玩家发送匹配成功消息
        enemy_resp_data = proto.pet_battle_match_s2c_data()
        enemy_resp_data.status = 2
        enemy_resp_data.enemy_player_name = player.get("name", "")
        enemy_resp_data.enemy_pet_id = pet_id
        enemy_resp_data.enemy_pet_name = my_pet.get("name", "")
        enemy_resp_data.enemy_pet_sex = my_pet.get("sex", 0)
        
        enemy_resp = proto.pet_battle_match_s2c(code=0, message="匹配成功")
        enemy_resp.data = enemy_resp_data
        
        # 广播消息给对手
        if "session" in enemy_player:
            enemy_player["session"].send_data(enemy_resp.to_dict())
        
        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"match_battle error: {e}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")
        resp = proto.pet_battle_match_s2c(code=-1, message=f"匹配失败: {str(e)}")
        return resp.to_dict()


async def start_battle(player: dict, msg_dict: dict):
    """开始战斗"""
    try:
        # 获取请求的宠物ID
        pet_id = msg_dict.get("pet_id", -1)
        if pet_id == -1:
            resp = proto.pet_battle_turn_s2c()
            resp.data = proto.pet_battle_turn_s2c_data()
            return resp.to_dict()
        
        # 检查是否已经配对
        if "battle_enemy_username" not in player:
            resp = proto.pet_battle_turn_s2c()
            resp.data = proto.pet_battle_turn_s2c_data()
            return resp.to_dict()
        
        # 设置战斗准备状态
        player["battle_ready"] = True
        player["battle_hp"] = 100
        
        # 发送初始消息
        init_data = proto.pet_battle_turn_s2c_data()
        init_data.turn = 0
        init_data.hp = 100
        init_data.enemy_hp = 100
        init_data.question = ""
        init_data.answers = ""
        init_data.enemy_answers = ""
        init_data.correct_answer = ""
        init_data.winner_name = ""
        
        init_resp = proto.pet_battle_turn_s2c()
        init_resp.data = init_data
        
        # 先发送初始消息
        if "session" in player:
            player["session"].send_data(init_resp.to_dict())
        
        # 检查对手是否也准备好了
        enemy_username = player.get("battle_enemy_username")
        enemy_player = login.PLAYER_LIST.get(enemy_username)
        
        if enemy_player is None or not enemy_player.get("battle_ready"):
            # 对手还没准备好，等待
            return init_resp.to_dict()
        
        # 双方都准备好了，开始战斗
        await run_battle(player, enemy_player)
        
        return init_resp.to_dict()
        
    except Exception as e:
        logger.error(f"start_battle error: {e}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")
        resp = proto.pet_battle_turn_s2c()
        resp.data = proto.pet_battle_turn_s2c_data()
        return resp.to_dict()


async def generate_questions():
    """一次性生成10道题"""
    try:
        question_agent = agent(
            system_prompt="你是一个初中语文老师，负责出题。请出10道小学语文范围内的题目，每道题目总字数要在30字以内，题目不要重复。请严格按照JSON数组格式输出，例如：[\"题目一\",\"题目二\",\"题目三\"]。只输出题目内容，不要输出答案，不要有任何多余的内容。",
            stream=False
        )
        
        question_result = await question_agent.execute("请出10道小学语文题，以JSON数组格式返回")
        logger.info(f"出题结果: {question_result}")
        
        # 解析JSON数组
        question_result = question_result.strip()
        if question_result.startswith("```json"):
            question_result = question_result[7:]
        if question_result.startswith("```"):
            question_result = question_result[3:]
        if question_result.endswith("```"):
            question_result = question_result[:-3]
        question_result = question_result.strip()
        
        questions = json.loads(question_result)
        if not isinstance(questions, list):
            raise ValueError("返回的不是数组格式")
        
        logger.info(f"成功生成{len(questions)}道题")
        return questions
        
    except Exception as e:
        logger.error(f"generate_questions error: {e}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")
        # 返回默认题目列表
        return [f"题目{i+1}" for i in range(10)]


async def run_battle(player: dict, enemy_player: dict):
    """执行战斗所有回合"""
    try:
        # 获取双方的宠物信息
        my_pet_id = player.get("battle_my_pet_id")
        enemy_pet_id = enemy_player.get("battle_my_pet_id")
        
        my_pet = None
        for pet in player.get("pets", []):
            if pet.get("id") == my_pet_id:
                my_pet = pet
                break
        
        enemy_pet = None
        for pet in enemy_player.get("pets", []):
            if pet.get("id") == enemy_pet_id:
                enemy_pet = pet
                break
        
        if my_pet is None or enemy_pet is None:
            logger.error("战斗宠物数据异常")
            return
        
        # 初始化血量
        my_hp = 100
        enemy_hp = 100
        turn = 1
        
        # 初始化题目列表，先出第一批10道题
        question_list = await generate_questions()
        
        # 战斗循环，直到一方血量为0
        while my_hp > 0 and enemy_hp > 0:
            # 如果题目列表为空，补充10道题
            if not question_list:
                question_list = await generate_questions()
            
            # 从列表中取一道题
            question_text = question_list.pop(0)
            
            # 执行一个回合
            turn_result = await execute_turn(my_pet, enemy_pet, question_text)
            # turn_result = {
            #     "question": turn_result_1["question"],
            #     "my_answer": turn_result_1["my_answer"],
            #     "enemy_answer": turn_result_1["enemy_answer"],
            #     "correct_answer": turn_result_1["correct_answer"],
            #     "my_pet_wrong": random.randint(0, 1),
            #     "enemy_pet_wrong": random.randint(0, 1)
            # }
            
            # 根据回合结果扣血
            if not turn_result["my_pet_right"]:
                my_hp -= 30
                if my_hp < 0:
                    my_hp = 0
            
            if not turn_result["enemy_pet_right"]:
                enemy_hp -= 30
                if enemy_hp < 0:
                    enemy_hp = 0
            
            # 发送回合消息给当前玩家
            turn_data = proto.pet_battle_turn_s2c_data()
            turn_data.turn = turn
            turn_data.hp = my_hp
            turn_data.enemy_hp = enemy_hp
            turn_data.question = turn_result["question"]
            turn_data.answers = turn_result["my_answer"]
            turn_data.enemy_answers = turn_result["enemy_answer"]
            turn_data.correct_answer = turn_result["correct_answer"]
            turn_data.my_pet_right = turn_result["my_pet_right"]
            turn_data.enemy_pet_right = turn_result["enemy_pet_right"]
            
            turn_resp = proto.pet_battle_turn_s2c()
            turn_resp.data = turn_data
            
            if "session" in player:
                player["session"].send_data(turn_resp.to_dict())
            
            # 发送回合消息给对手玩家（视角相反）
            enemy_turn_data = proto.pet_battle_turn_s2c_data()
            enemy_turn_data.turn = turn
            enemy_turn_data.hp = enemy_hp
            enemy_turn_data.enemy_hp = my_hp
            enemy_turn_data.question = turn_result["question"]
            enemy_turn_data.answers = turn_result["enemy_answer"]
            enemy_turn_data.enemy_answers = turn_result["my_answer"]
            enemy_turn_data.correct_answer = turn_result["correct_answer"]
            enemy_turn_data.my_pet_right = turn_result["enemy_pet_right"]
            enemy_turn_data.enemy_pet_right = turn_result["my_pet_right"]
            
            enemy_turn_resp = proto.pet_battle_turn_s2c()
            enemy_turn_resp.data = enemy_turn_data
            
            if "session" in enemy_player:
                enemy_player["session"].send_data(enemy_turn_resp.to_dict())
            
            turn += 1
            
            # 添加短暂延迟，避免消息发送过快
            # await asyncio.sleep(0.1)
        
        # 战斗结束，计算结果
        await send_battle_result(player, enemy_player, my_hp, enemy_hp, my_pet, enemy_pet)
        
    except Exception as e:
        logger.error(f"run_battle error: {e}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")


async def execute_turn(my_pet: dict, enemy_pet: dict, question_text: str):
    """执行一个战斗回合"""
    try:
        # 获取双方宠物的语文能力值
        my_chinese_value = 0
        enemy_chinese_value = 0
        
        for attr in my_pet.get("attr", []):
            if attr.get("id") == 1:  # 语文属性
                my_chinese_value = attr.get("value", 0)
                break
        
        for attr in enemy_pet.get("attr", []):
            if attr.get("id") == 1:  # 语文属性
                enemy_chinese_value = attr.get("value", 0)
                break
        
        attr_high = "你的语文能力非常强，有80%的概率能回答正确。"
        attr_middle = "你的语文能力还不错，有40%的概率能回答正确。"
        attr_low = "你的语文能力一般，有25%的概率能回答正确。"

        # Agent 2: 我的宠物答题
        my_pet_character = ", ".join(my_pet.get("character", []))
        my_pet_prompt = f"你是一只名叫{my_pet.get('name', '')}的宠物，你的性格特点是：{my_pet_character}。"
        my_pet_prompt += f"你的语文能力值是{my_chinese_value}（满分60分）。"
        
        if my_chinese_value >= 60:
            my_pet_prompt += attr_high
        elif my_chinese_value >= 40:
            my_pet_prompt += attr_middle
        else:
            my_pet_prompt += attr_low
        
        my_pet_prompt += f"请用符合你性格特点（{my_pet_character}）的语气和方式来回答问题。回答要简短，控制在20字以内。"
        
        my_pet_agent = agent(system_prompt=my_pet_prompt, stream=False)
        
        # Agent 3: 对手宠物答题
        enemy_pet_character = ", ".join(enemy_pet.get("character", []))
        enemy_pet_prompt = f"你是一只名叫{enemy_pet.get('name', '')}的宠物，你的性格特点是：{enemy_pet_character}。"
        enemy_pet_prompt += f"你的语文能力值是{enemy_chinese_value}（满分60分）。"
        
        if enemy_chinese_value >= 60:
            enemy_pet_prompt += attr_high
        elif enemy_chinese_value >= 40:
            enemy_pet_prompt += attr_middle
        else:
            enemy_pet_prompt += attr_low
        
        enemy_pet_prompt += f"请用符合你性格特点（{enemy_pet_character}）的语气和方式来回答问题。回答要简短，控制在20字以内。"
        
        enemy_pet_agent = agent(system_prompt=enemy_pet_prompt, stream=False)
        
        # 并行执行 Agent 2 和 Agent 3
        my_answer, enemy_answer = await asyncio.gather(
            my_pet_agent.execute(f"请回答以下问题：{question_text}"),
            enemy_pet_agent.execute(f"请回答以下问题：{question_text}")
        )
        logger.info(f"我的宠物答案: {my_answer}")
        logger.info(f"对手宠物答案: {enemy_answer}")
        
        # Agent 4: 判断答案
        judge_agent = agent(
            system_prompt=f"你是一个判题老师，负责判断学生的答案是否正确。你需要先推理出题目的正确答案，然后判断两个学生的回答是否正确。请严格按照以下JSON格式输出：\n{{\"correct_answer\": \"正确答案\", \"student1_is_right\": \"正确/错误\", \"student2_is_right\": \"正确/错误\"}}",
            stream=False
        )
        
        judge_prompt = f"题目：{question_text}\n\n学生1的回答：{my_answer}\n学生2的回答：{enemy_answer}\n\n请判断两个学生的答案是否正确。"
        
        # 重试逻辑：最多重试3次
        result_json = None
        for retry_count in range(3):
            try:
                judge_result = await judge_agent.execute(judge_prompt)
                logger.info(f"判题结果: {judge_result}")
                
                # 解析json结果
                judge_result = judge_result.strip()
                if judge_result.startswith("```json"):
                    judge_result = judge_result[7:]
                if judge_result.startswith("```"):
                    judge_result = judge_result[3:]
                if judge_result.endswith("```"):
                    judge_result = judge_result[:-3]
                judge_result = judge_result.strip()
                result_json = json.loads(judge_result)
                break  # 解析成功，跳出循环
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败 (第{retry_count + 1}次尝试): {e}")
                if retry_count == 2:  # 最后一次重试也失败
                    raise Exception(f"JSON解析失败，已重试3次: {e}")
                # 继续重试

        correct_answer = result_json.get("correct_answer", "")
        my_pet_right = result_json.get("student1_is_right", "") == "正确"
        enemy_pet_right = result_json.get("student2_is_right", "") == "正确"
        

        return {
            "question": question_text,
            "my_answer": my_answer,
            "enemy_answer": enemy_answer,
            "correct_answer": correct_answer,
            "my_pet_right": my_pet_right,
            "enemy_pet_right": enemy_pet_right
        }
        
    except Exception as e:
        logger.error(f"execute_turn error: {e}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")
        # 返回默认值
        return {
            "question": "题目加载失败",
            "my_answer": "",
            "enemy_answer": "",
            "correct_answer": "",
            "my_pet_right": False,
            "enemy_pet_right": False
        }


async def send_battle_result(player: dict, enemy_player: dict, my_hp: int, enemy_hp: int, my_pet: dict, enemy_pet: dict):
    """发送战斗结果并更新属性"""
    try:
        # 判断胜负
        i_win = my_hp > enemy_hp
        
        # 计算属性变化
        if i_win:
            # 我胜利
            my_attr_change = my_hp // 10
            enemy_attr_change = -(my_hp // 10)
        else:
            # 对手胜利
            my_attr_change = -(enemy_hp // 10)
            enemy_attr_change = enemy_hp // 10
        
        # 更新我的宠物属性
        for attr in my_pet.get("attr", []):
            if attr.get("id") == 1:  # 语文属性
                attr["value"] += my_attr_change
                if attr["value"] < 0:
                    attr["value"] = 0
                break
        
        # 更新对手宠物属性
        for attr in enemy_pet.get("attr", []):
            if attr.get("id") == 1:  # 语文属性
                attr["value"] += enemy_attr_change
                if attr["value"] < 0:
                    attr["value"] = 0
                break
        
        # 保存到文件
        login.save_pets_data(player.get("username"), player.get("pets", []))
        login.save_pets_data(enemy_player.get("username"), enemy_player.get("pets", []))
        
        # 发送结果消息给我
        my_result_data = proto.pet_battle_result_s2c_data()
        my_result_data.attr = []
        
        my_attr_item = proto.pet_battle_result_s2c_data_attr()
        my_attr_item.id = 1
        my_attr_item.value = my_attr_change
        my_result_data.attr.append(my_attr_item)
        
        my_result_resp = proto.pet_battle_result_s2c()
        my_result_resp.data = my_result_data
        
        if "session" in player:
            player["session"].send_data(my_result_resp.to_dict())
        
        # 发送结果消息给对手
        enemy_result_data = proto.pet_battle_result_s2c_data()
        enemy_result_data.attr = []
        
        enemy_attr_item = proto.pet_battle_result_s2c_data_attr()
        enemy_attr_item.id = 1
        enemy_attr_item.value = enemy_attr_change
        enemy_result_data.attr.append(enemy_attr_item)
        
        enemy_result_resp = proto.pet_battle_result_s2c()
        enemy_result_resp.data = enemy_result_data
        
        if "session" in enemy_player:
            enemy_player["session"].send_data(enemy_result_resp.to_dict())
        
        # 清理临时战斗信息
        cleanup_battle_info(player)
        cleanup_battle_info(enemy_player)
        
    except Exception as e:
        logger.error(f"send_battle_result error: {e}")
        import traceback
        logger.error(f"traceback: {traceback.format_exc()}")

async def match_cancel_battle(player: dict, msg_dict: dict):
    """取消战斗匹配"""
    try:
        # 清理临时战斗信息
        cleanup_battle_info(player)
        resp = proto.pet_battle_match_cancel_s2c(code=0, message="取消战斗匹配成功")
        return resp.to_dict()
    except Exception as e:
        logger.error(f"match_cancel_battle error: {e}")
        logger.error(f"traceback: {traceback.format_exc()}")
        resp = proto.pet_battle_match_cancel_s2c(code=-1, message=f"取消战斗匹配失败: {str(e)}")
        return resp.to_dict()

def cleanup_battle_info(player: dict):
    """清理玩家的临时战斗信息"""
    keys_to_remove = [
        "battle_matching",
        "battle_my_pet_id",
        "battle_enemy_username",
        "battle_enemy_pet_id",
        "battle_ready",
        "battle_hp"
    ]
    for key in keys_to_remove:
        if key in player:
            del player[key]