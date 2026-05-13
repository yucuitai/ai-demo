"""
热点数据服务 - 从 MCP hotnews 获取真实热点，失败时回退到模拟数据
"""
import json
import os
import random
import logging
from services.mcp_client import mcp_client

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
HOTSPOTS_FILE = os.path.join(DATA_DIR, "hotspots.json")

MOCK_HOTSPOTS = [
    {"id": "1",  "title": "AI大模型最新进展：GPT-5发布时间曝光",      "content": "OpenAI即将发布新一代大模型，性能提升显著，多模态能力大幅增强，业界高度关注",          "hotValue": 98765, "type": "tech",         "time": "2小时前"},
    {"id": "2",  "title": "2025年最值得关注的10个AI工具",              "content": "从文本生成到视频制作，这些AI工具正在改变我们的工作方式，提升创作效率",                    "hotValue": 87654, "type": "tech",         "time": "3小时前"},
    {"id": "3",  "title": "远程办公成为主流：如何保持高效工作",        "content": "后疫情时代，越来越多的企业采用混合办公模式，如何平衡工作与生活成为新课题",              "hotValue": 76543, "type": "career",       "time": "5小时前"},
    {"id": "4",  "title": "健康生活新趋势：植物性饮食的科学依据",      "content": "越来越多的研究表明，植物性饮食对健康有诸多益处，全球掀起绿色饮食潮流",                  "hotValue": 65432, "type": "life",         "time": "6小时前"},
    {"id": "5",  "title": "年度大片票房破纪录：国产电影崛起",          "content": "今年春节档电影票房再创新高，多部国产佳作获得口碑票房双丰收，文化自信不断增强",          "hotValue": 54321, "type": "entertainment", "time": "8小时前"},
    {"id": "6",  "title": "程序员职业发展：从初级到架构师的成长之路",  "content": "分享10年编程经验，聊聊技术成长路上的那些坑与收获，给年轻开发者一些借鉴",                "hotValue": 43210, "type": "career",       "time": "10小时前"},
    {"id": "7",  "title": "智能家居全面普及：你家升级了吗？",          "content": "从智能音箱到全屋智能，智能家居正在走进千家万户，生活变得更便捷更舒适",                  "hotValue": 32109, "type": "tech",         "time": "12小时前"},
    {"id": "8",  "title": "断舍离生活方式：极简主义的艺术",            "content": "通过整理物品来整理内心，极简主义生活带来的改变远超想象，越来越多年轻人开始践行",          "hotValue": 21098, "type": "life",         "time": "1天前"},
    {"id": "9",  "title": "新能源汽车价格战：消费者迎来购车好时机",    "content": "各大车企纷纷降价促销，新能源汽车市场竞争白热化，消费者选择空间前所未有",                "hotValue": 45678, "type": "tech",         "time": "4小时前"},
    {"id": "10", "title": "面试技巧大揭秘：大厂面试官亲述",             "content": "资深面试官分享面试中的关键考察点，如何在众多候选人中脱颖而出",                          "hotValue": 38901, "type": "career",       "time": "7小时前"},
    {"id": "11", "title": "城市露营风潮：都市人的诗意栖息",            "content": "无需远行就能感受自然，城市露营成为年轻人休闲新宠，重新定义都市生活方式",                "hotValue": 29876, "type": "life",         "time": "9小时前"},
    {"id": "12", "title": "热门综艺背后的制作故事",                     "content": "综艺节目如何制造话题与热度？揭秘综艺制作的幕后团队和创意过程",                          "hotValue": 18765, "type": "entertainment", "time": "11小时前"},
]

_mcp_available = None


def init_mcp():
    global _mcp_available
    if _mcp_available is None:
        _mcp_available = mcp_client.start()
        if _mcp_available:
            tools = mcp_client.list_tools()
            logger.info(f"MCP hotnews 可用工具: {[t.get('name') for t in tools]}")
    return _mcp_available

def _normalize_item(item, index):
    """统一 MCP 返回的数据格式"""
    return {
        "id": str(item.get("id", index)),
        "title": item.get("title", item.get("name", item.get("hotWord", ""))),
        "content": item.get("content", item.get("desc", item.get("abstract", item.get("summary", "")))),
        "hotValue": int(item.get("hotValue", item.get("heat", item.get("score", item.get("popularity", random.randint(10000, 99999)))))),
        "type": item.get("type", item.get("category", item.get("tag", "tech"))),
        "time": item.get("time", item.get("updateTime", item.get("publishTime", "刚刚")))
    }


def _load_hotspots():
    if os.path.exists(HOTSPOTS_FILE):
        try:
            with open(HOTSPOTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_hotspots(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HOTSPOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_mcp_text_to_items(text):
    """解析 MCP 返回的热点文本为结构化列表"""
    if not text:
        return []

    # 尝试 JSON 解析
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ["data", "items", "hotNews", "news", "list"]:
                if key in data:
                    val = data[key]
                    return val if isinstance(val, list) else [val]
    except (json.JSONDecodeError, TypeError):
        pass

    # 按平台分隔符解析
    items = []
    current_platform = ""
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # 检测平台标题行
        if line.startswith("#") or line.startswith("##") or line.startswith("【"):
            current_platform = line.lstrip("#").strip()
            continue
        # 检测编号行如 "1. 标题 - 描述"
        if line[0].isdigit() and (". " in line or "、" in line or " " in line):
            parts = line.split(". ", 1) if ". " in line else line.split(" ", 1)
            if len(parts) >= 2:
                title_part = parts[1] if len(parts) > 1 else parts[0]
                items.append({
                    "title": title_part,
                    "content": title_part,
                    "type": "tech",
                    "platform": current_platform
                })
            continue
        # 普通行
        if len(line) > 4:
            items.append({
                "title": line,
                "content": line,
                "type": "tech",
                "platform": current_platform
            })

    return items


def fetch_hotspots_from_mcp():
    """从 MCP hotnews 服务器获取真实热点数据"""
    if not init_mcp():
        logger.info("MCP 不可用，使用本地缓存数据")
        return _load_hotspots() or MOCK_HOTSPOTS

    try:
        # 调用 get_hot_news 工具，获取多个平台的热点
        raw = mcp_client.call_tool("get_hot_news", {"sources": [1, 2, 3, 4, 5, 6, 7, 8, 9]})

        if not raw:
            logger.info("MCP 热点获取为空，使用本地缓存")
            return _load_hotspots() or MOCK_HOTSPOTS

        # 如果包含网络错误但仍返回了数据
        if "Failed to fetch" in str(raw) and len(raw) < 500:
            logger.warning("MCP 网络请求失败（DNS/网络不可达），使用本地缓存")
            return _load_hotspots() or MOCK_HOTSPOTS

        items = _parse_mcp_text_to_items(raw)

        if not items:
            logger.info("MCP 热点数据解析为空，使用本地缓存")
            return _load_hotspots() or MOCK_HOTSPOTS

        normalized = [_normalize_item(item, i + 1) for i, item in enumerate(items)]

        # 按热度降序排列
        normalized.sort(key=lambda x: x.get("hotValue", 0), reverse=True)
        _save_hotspots(normalized)
        logger.info(f"MCP 热点获取成功: {len(normalized)} 条")
        return normalized

    except Exception as e:
        logger.warning(f"MCP 热点获取异常: {e}，使用本地缓存")
        return _load_hotspots() or MOCK_HOTSPOTS


def refresh_hotspots():
    """刷新热点数据"""
    if init_mcp():
        try:
            return fetch_hotspots_from_mcp()
        except Exception as e:
            logger.warning(f"MCP 刷新失败: {e}")

    cached = _load_hotspots()
    if cached:
        for item in cached:
            delta = random.randint(-5000, 15000)
            item["hotValue"] = max(1000, min(99999, item["hotValue"] + delta))
        random.shuffle(cached)
        _save_hotspots(cached)
        return cached
    return MOCK_HOTSPOTS


def get_hotspots(category=None, search=None, page=1, page_size=12):
    """获取热点列表，支持分类筛选、搜索、分页"""
    all_data = _load_hotspots() or MOCK_HOTSPOTS

    if category and category != "all":
        all_data = [h for h in all_data if h.get("type") == category]

    if search:
        q = search.lower()
        all_data = [h for h in all_data if q in h.get("title", "").lower() or q in h.get("content", "").lower()]

    total = len(all_data)
    start = (page - 1) * page_size
    items = all_data[start:start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "pageSize": page_size
    }
