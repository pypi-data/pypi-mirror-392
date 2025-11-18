from pydantic import BaseModel
from typing import Dict, List

class Config(BaseModel):
    """插件配置"""
    # 价格数据URL
    price_data_url: str = "https://raw.githubusercontent.com/orzice/DeltaForcePrice/master/price.json"
    # 本地缓存文件路径
    cache_file: str = "bullet_price_cache.json"
    # 缓存过期时间（秒）
    cache_expire: int = 3600
    # 分类关键词映射
    category_keywords: Dict[str, List[str]] = {
        "枪械": ["步枪", "手枪", "冲锋枪", "狙击枪", "霰弹枪", "机枪", "枪械"],
        "头盔": ["头盔"],
        "护甲": ["护甲", "背心", "防弹衣"],
        "配件": ["配件", "瞄具", "枪口", "枪管", "护木", "枪托", "后握把", "前握把", "弹匣", "弹鼓"],
        "子弹": ["子弹", "弹药"],
        "收集品": ["收集品", "收藏品", "稀有物品"],
        "消耗品": ["消耗品", "医疗", "药品", "食物", "饮料"],
        "钥匙": ["钥匙", "门卡"]
    }

config = Config()