import os
import json
import hashlib
import random
from proto import proto
from config.pet_cfg import PET_CFG
from config.character_cfg import CHARACTER_CFG
from utils.logger import logger

# 数据库目录
DB_DATA_DIR = os.path.join(os.path.dirname(__file__), "db_data")

def get_user_dir(username: str) -> str:
    """获取用户数据目录路径"""
    username_md5 = hashlib.md5(username.encode('utf-8')).hexdigest()
    return os.path.join(DB_DATA_DIR, username_md5)

def get_user_file_path(username: str) -> str:
    """获取用户数据文件路径"""
    return os.path.join(get_user_dir(username), "user.json")

def get_pets_file_path(username: str) -> str:
    """获取宠物数据文件路径"""
    return os.path.join(get_user_dir(username), "pets.json")

def load_user_data(username: str) -> dict:
    """加载用户数据"""
    user_file = get_user_file_path(username)
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user data for {username}: {e}")
            return None
    return None

def save_user_data(username: str, user_data: dict):
    """保存用户数据"""
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    user_file = get_user_file_path(username)
    try:
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save user data for {username}: {e}")
        raise

def load_pets_data(username: str) -> list:
    """加载宠物数据"""
    pets_file = get_pets_file_path(username)
    if os.path.exists(pets_file):
        try:
            with open(pets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load pets data for {username}: {e}")
            return []
    return []

def save_pets_data(username: str, pets_data: list):
    """保存宠物数据"""
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    pets_file = get_pets_file_path(username)
    try:
        with open(pets_file, 'w', encoding='utf-8') as f:
            json.dump(pets_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save pets data for {username}: {e}")
        raise

def create_initial_pet() -> dict:
    """创建初始宠物"""
    # 随机选择一个宠物配置
    pet_cfg = random.choice(PET_CFG)
    
    # 随机选择3个性格（不重复）
    characters = random.sample(CHARACTER_CFG, min(3, len(CHARACTER_CFG)))
    
    # 创建宠物数据
    pet = {
        "id": pet_cfg["id"],
        "name": pet_cfg["name"],
        "sex": random.randint(0, 1),
        "nickname": "",
        "type": pet_cfg["type"],
        "character": characters,
        "attr": pet_cfg["attr"].copy()  # 深拷贝属性
    }

    # 宠物的属性随机增加-3到3之间
    for attr in pet["attr"]:
        attr["value"] += random.randint(-3, 3)
    
    return pet

async def sign_in(player, msg_dict: dict):
    """登录"""
    try:
        username = msg_dict.get("username", "")
        password = msg_dict.get("password", "")
        
        if not username or not password:
            resp = proto.sign_in_s2c(code=-1, message="用户名或密码不能为空")
            return resp.to_dict()
        
        # 加载用户数据
        user_data = load_user_data(username)
        if user_data is None:
            resp = proto.sign_in_s2c(code=-1, message="用户名不存在")
            return resp.to_dict()
        
        # 验证密码
        if user_data.get("password") != password:
            resp = proto.sign_in_s2c(code=-1, message="密码错误")
            return resp.to_dict()
        
        # 加载宠物数据
        pets_data = load_pets_data(username)
        
        # 如果用户没有宠物，创建初始宠物
        if not pets_data:
            pet = create_initial_pet()
            pets_data = [pet]
            save_pets_data(username, pets_data)
        
        # 构建响应数据
        resp_data = proto.sign_in_s2c_data()
        
        # 设置玩家信息
        player_info = proto.sign_in_s2c_data_player()
        player_info.name = user_data.get("name", "")
        resp_data.player = player_info
        
        # 设置宠物信息
        resp_data.pet = []
        for pet in pets_data:
            pet_info = proto.sign_in_s2c_data_pet()
            pet_info.id = pet["id"]
            pet_info.name = pet["name"]
            resp_data.pet.append(pet_info)
        
        # 返回成功响应
        resp = proto.sign_in_s2c(code=0, message="登录成功")
        resp.data = resp_data

        # 更新 player 数据
        player["username"] = username
        player["password"] = password
        player["name"] = user_data.get("name", "")
        player["pets"] = pets_data

        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"sign_in error: {e}")
        resp = proto.sign_in_s2c(code=-1, message=f"登录失败: {str(e)}")
        return resp.to_dict()

async def sign_up(player, msg_dict: dict):
    """注册"""
    try:
        username = msg_dict.get("username", "")
        password = msg_dict.get("password", "")
        name = msg_dict.get("name", "")
        
        if not username or not password or not name:
            resp = proto.sign_up_s2c(code=-1, message="用户名、密码或名字不能为空")
            return resp.to_dict()
        
        # 检查用户是否已存在
        if load_user_data(username) is not None:
            resp = proto.sign_up_s2c(code=-1, message="用户名已存在")
            return resp.to_dict()
        
        # 创建用户数据
        user_data = {
            "username": username,
            "password": password,
            "name": name
        }
        
        # 保存用户数据
        save_user_data(username, user_data)
        
        # 返回成功响应
        resp = proto.sign_up_s2c(code=0, message="注册成功")
        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"sign_up error: {e}")
        resp = proto.sign_up_s2c(code=-1, message=f"注册失败: {str(e)}")
        return resp.to_dict()
