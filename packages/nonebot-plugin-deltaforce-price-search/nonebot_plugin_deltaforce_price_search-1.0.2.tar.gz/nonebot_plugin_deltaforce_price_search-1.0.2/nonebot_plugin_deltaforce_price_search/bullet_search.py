import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import httpx
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.qq import Message, MessageEvent  # 修改为QQ适配器
from nonebot.plugin import PluginMetadata
from nonebot.exception import FinishedException  # 导入FinishedException

from .config import config

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="DeltaForce物品价格搜索",
    description="搜索DeltaForce游戏中的枪械、头盔、护甲、配件、子弹、收集品、消耗品、钥匙等物品价格",
    usage="使用'价格 [关键词]'或'分类 [分类名]'命令来搜索相关物品",
    type="application",
    homepage="https://github.com/orzice/DeltaForcePrice",
)

# 创建命令处理器
item_search = on_command("价格", aliases={"search", "物品价格", "搜价格", "查价"}, priority=10, block=True)
category_search = on_command("分类", aliases={"category", "物品分类", "种类"}, priority=10, block=True)

async def fetch_price_data() -> List[Dict[str, Any]]:
    """获取价格数据，优先使用缓存"""
    cache_file = Path(config.cache_file)
    
    # 检查缓存是否存在且未过期
    if cache_file.exists():
        cache_time = cache_file.stat().st_mtime
        if time.time() - cache_time < config.cache_expire:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass  # 缓存文件损坏，重新获取
    
    # 从网络获取数据
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(config.price_data_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 保存到缓存
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return data
        except Exception as e:
            # 如果网络请求失败但缓存存在，使用缓存
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            raise e

def parse_search_keyword(keyword: str) -> Tuple[Optional[str], str]:
    """解析搜索关键词，返回分类和具体关键词"""
    keyword_lower = keyword.lower()
    
    # 检查是否是分类搜索
    for category, keywords in config.category_keywords.items():
        for kw in keywords:
            if keyword_lower == kw.lower() or keyword_lower.startswith(f"{kw} "):
                # 提取分类后的具体关键词
                remaining = keyword[len(kw):].strip()
                return category, remaining
    
    return None, keyword

def search_items(data: List[Dict[str, Any]], category: Optional[str], keyword: str) -> List[Dict[str, Any]]:
    """搜索物品"""
    results = []
    keyword_lower = keyword.lower()
    
    for item in data:
        # 提取物品信息
        item_name = item.get('name', '').lower()
        item_category = item.get('secondClassCN', '').lower()
        item_price = item.get('price', 0)
        
        # 如果有分类限制，先检查分类
        if category and category.lower() not in item_category:
            continue
            
        # 搜索匹配
        name_match = keyword_lower in item_name if keyword else True
        category_match = keyword_lower in item_category if keyword else True
        
        if name_match or category_match:
            # 只提取需要的字段
            simplified_item = {
                'id': item.get('id', 'N/A'),
                'name': item.get('name', '未知物品'),
                'price': item_price,
                'secondClassCN': item.get('secondClassCN', '未知分类')
            }
            results.append(simplified_item)
    
    return results

def format_item_list(items: List[Dict[str, Any]], limit: int = 10) -> str:  # 减少显示数量避免消息过长
    """格式化物品列表"""
    if not items:
        return "未找到相关物品。"
    
    # 限制结果数量
    limited_items = items[:limit]
    
    messages = []
    for i, item in enumerate(limited_items, 1):
        item_id = item.get('id', 'N/A')
        name = item.get('name', '未知物品')
        price = item.get('price', 0)
        category = item.get('secondClassCN', '未知分类')
        
        # 格式化价格（添加千位分隔符）
        formatted_price = f"{price:,}"
        
        messages.append(f"{i}. ID:{item_id} | {name} | 价格:{formatted_price} | 分类:{category}")
    
    result_msg = "\n".join(messages)
    
    if len(items) > limit:
        result_msg += f"\n... 还有 {len(items) - limit} 个结果未显示，请使用更具体的关键词。"
    
    return result_msg

def get_category_items(data: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """获取指定分类的所有物品"""
    category_lower = category.lower()
    results = []
    
    for item in data:
        item_category = item.get('secondClassCN', '').lower()
        
        # 检查分类匹配
        if category_lower in item_category:
            # 只提取需要的字段
            simplified_item = {
                'id': item.get('id', 'N/A'),
                'name': item.get('name', '未知物品'),
                'price': item.get('price', 0),
                'secondClassCN': item.get('secondClassCN', '未知分类')
            }
            results.append(simplified_item)
    
    return results

def get_available_categories(data: List[Dict[str, Any]]) -> Dict[str, int]:
    """获取可用的分类及其物品数量"""
    categories = {}
    
    for item in data:
        category = item.get('secondClassCN', '未知分类')
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1
    
    return categories

@item_search.handle()
async def handle_item_search(event: MessageEvent, args: Message = CommandArg()):  # 添加event参数
    """处理物品搜索命令 - 修正版"""
    keyword = args.extract_plain_text().strip()
    
    if not keyword:
        # 使用send而不是finish来避免FinishedException
        await item_search.send("请提供搜索关键词，例如：价格 M4 或 价格 头盔 三级")
        return
    
    try:
        # 获取数据
        data = await fetch_price_data()
        
        # 解析关键词
        category, search_keyword = parse_search_keyword(keyword)
        
        # 搜索物品
        if category:
            results = search_items(data, category, search_keyword)
            search_info = f"分类【{category}】"
            if search_keyword:
                search_info += f" + 关键词【{search_keyword}】"
        else:
            results = search_items(data, None, search_keyword)
            search_info = f"关键词【{search_keyword}】"
        
        # 格式化结果
        if results:
            result_count = len(results)
            result_message = f"搜索{search_info}，找到{result_count}个物品：\n\n"
            result_message += format_item_list(results)
        else:
            result_message = f"搜索{search_info}未找到相关物品。"
        
        # 使用send而不是finish
        await item_search.send(result_message)
        
    except httpx.RequestError:
        await item_search.send("网络连接失败，请检查网络后重试。")
    except json.JSONDecodeError:
        await item_search.send("数据解析失败，请稍后重试。")
    except FinishedException:
        # 忽略FinishedException，这是正常的行为
        return
    except Exception as e:
        await item_search.send(f"搜索过程中出现错误：{str(e)}")

@category_search.handle()
async def handle_category_search(event: MessageEvent, args: Message = CommandArg()):  # 添加event参数
    """处理分类搜索命令 - 修正版"""
    category_keyword = args.extract_plain_text().strip()
    
    if not category_keyword:
        # 显示所有可用分类
        try:
            data = await fetch_price_data()
            categories = get_available_categories(data)
            
            if categories:
                category_list = []
                for cat, count in sorted(categories.items()):
                    category_list.append(f"{cat} ({count}个物品)")
                
                message = "可用分类列表：\n" + "\n".join(category_list)
                message += "\n\n使用命令：分类 [分类名称] 查看具体物品"
            else:
                message = "未找到分类信息。"
                
            await category_search.send(message)  # 使用send
        except Exception as e:
            await category_search.send(f"获取分类列表失败：{str(e)}")  # 使用send
        return
    
    try:
        # 获取数据
        data = await fetch_price_data()
        
        # 查找匹配的分类
        matched_category = None
        for category in get_available_categories(data).keys():
            if category_keyword.lower() in category.lower():
                matched_category = category
                break
        
        if not matched_category:
            await category_search.send(f"未找到分类【{category_keyword}】，请使用'分类'命令查看可用分类。")  # 使用send
            return
        
        # 获取该分类的所有物品
        items = get_category_items(data, matched_category)
        
        if items:
            # 按价格排序（可选）
            items_sorted = sorted(items, key=lambda x: x.get('price', 0), reverse=True)
            
            result_message = f"分类【{matched_category}】共有{len(items)}个物品：\n\n"
            result_message += format_item_list(items_sorted)
        else:
            result_message = f"分类【{matched_category}】中没有物品。"
        
        await category_search.send(result_message)  # 使用send
        
    except FinishedException:
        # 忽略FinishedException
        return
    except Exception as e:
        await category_search.send(f"分类搜索过程中出现错误：{str(e)}")  # 使用send

# 帮助命令
help_cmd = on_command("搜索帮助", aliases={"searchhelp", "物品搜索帮助", "救命"}, priority=5, block=True)

@help_cmd.handle()
async def handle_help(event: MessageEvent):  # 添加event参数
    help_text = """物品搜索插件使用说明：

🔍 搜索命令：
- "search", "物品价格", "搜价格", "查价"  等均可触发搜索命令。
- 价格 [关键词] - 搜索物品（如：价格 M4）
- 价格 [分类] [关键词] - 在指定分类中搜索（如：搜价格 头盔 三级）

📂 分类命令：
- "category", "物品分类", "种类" 等均可触发分类命令。
- 分类 - 显示所有可用分类
- 分类 [分类名] - 查看指定分类的所有物品

🎯 支持的主要分类关键词：
• 枪械 - 步枪、手枪、冲锋枪等
• 头盔 - 各种头盔
• 护甲 - 护甲、背心、防弹衣
• 配件 - 瞄具、枪口、枪管、弹匣等
• 子弹 - 弹药
• 收集品 - 稀有物品
• 消耗品 - 医疗、食物等
• 钥匙 - 门卡钥匙

💡 搜索示例：
- 价格 M4弹匣
- 价格 头盔
- 价格 配件 扩容
- 分类 弹匣

如需要查看每日破译密码，请使用“每日密码”命令。

数据来源于DeltaForce游戏社区，如有任何问题或建议，欢迎反馈！
"""
    await help_cmd.send(help_text)  # 使用send