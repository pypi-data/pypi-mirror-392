from nonebot.plugin import PluginMetadata

from . import bullet_search

__plugin_meta__ = PluginMetadata(
    name="DeltaForce物品价格搜索",
    description="搜索DeltaForce游戏中的枪械、头盔、护甲、配件、子弹、收集品、消耗品、钥匙等物品价格",
    usage="使用'价格 [关键词]'或'分类 [分类名]'命令来搜索相关物品",
    type="application",
    homepage="https://github.com/orzice/DeltaForcePrice",
    supported_adapters=None,
)

from .bullet_search import *