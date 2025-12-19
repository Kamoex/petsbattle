from proto import proto
from login import load_pets_data
from utils.logger import logger

async def get_pet_info(player: dict, msg_dict: dict):
    """获取宠物信息"""
    try:
        # 检查玩家是否已登录
        if not player or not player.get("username"):
            resp = proto.pet_info_s2c(code=-1, message="请先登录")
            return resp.to_dict()
        
        # 获取请求的宠物ID
        pet_id = msg_dict.get("pet_id", -1)
        if pet_id == -1:
            resp = proto.pet_info_s2c(code=-1, message="宠物ID不能为空")
            return resp.to_dict()
        
        # 从 player 中获取宠物列表，如果没有则从文件加载
        pets_data = player.get("pets", [])
        if not pets_data:
            username = player.get("username")
            pets_data = load_pets_data(username)
            # 更新 player 中的 pets 数据
            player["pets"] = pets_data
        
        # 查找对应的宠物
        pet_data = None
        for pet in pets_data:
            if pet.get("id") == pet_id:
                pet_data = pet
                break
        
        # 如果宠物不存在
        if pet_data is None:
            resp = proto.pet_info_s2c(code=-1, message="宠物不存在")
            return resp.to_dict()
        
        # 构建响应数据
        resp_data = proto.pet_info_s2c_data()
        pet_info = proto.pet_info_s2c_data_pet()
        
        # 设置宠物基本信息
        pet_info.id = pet_data.get("id", -1)
        pet_info.name = pet_data.get("name", "")
        pet_info.nickname = pet_data.get("nickname", "")
        pet_info.sex = pet_data.get("sex", 0)
        pet_info.type = pet_data.get("type", "")
        pet_info.character = pet_data.get("character", [])
        
        # 设置宠物属性
        pet_info.attr = []
        for attr_data in pet_data.get("attr", []):
            attr = proto.pet_info_s2c_data_pet_attr()
            attr.id = attr_data.get("id", -1)
            attr.value = attr_data.get("value", 0)
            pet_info.attr.append(attr)
        
        resp_data.pet = pet_info
        
        # 返回成功响应
        resp = proto.pet_info_s2c(code=0, message="")
        resp.data = resp_data
        return resp.to_dict()
        
    except Exception as e:
        logger.error(f"get_pet_info error: {e}")
        resp = proto.pet_info_s2c(code=-1, message=f"获取宠物信息失败: {str(e)}")
        return resp.to_dict()
