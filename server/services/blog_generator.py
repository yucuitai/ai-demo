"""
博客内容生成服务 - 支持 AI API 调用 + 模板回退
"""
import json
import logging
import random
from urllib import request, error

from services.config import get_ai_config, is_ai_configured

logger = logging.getLogger(__name__)

STYLE_CONFIG = {
    "professional": {"tone": "严谨专业、逻辑清晰", "intro": "深入剖析", "prefix": "从专业视角审视"},
    "casual":       {"tone": "轻松活泼、通俗易懂", "intro": "聊聊",     "prefix": "今天咱们来聊聊"},
    "educational":  {"tone": "干货满满、知识性强", "intro": "科普",     "prefix": "本篇文章带你全面了解"},
    "emotional":    {"tone": "温暖真诚、有共鸣感", "intro": "感悟",     "prefix": "让我们一同感受"},
}

DEPTH_CONFIG = {
    "basic": {"sections": 2, "label": "基础简述", "analysis": "从表面现象入手"},
    "deep":  {"sections": 3, "label": "深度解析", "analysis": "深入剖析背后逻辑与影响"},
}

SECTION_TEMPLATES = [
    {
        "heading": "热点背景与现状",
        "template": "当前，{topics}已成为备受瞩目的热点话题。随着信息传播速度的加快，这些话题迅速进入公众视野，引发了广泛讨论。从社交媒体到主流新闻，从线下交流到线上互动，这些热点正在以一种前所未有的方式影响着人们的思考和行为方式。"
    },
    {
        "heading": "核心要素分析",
        "template": "深入探究{topics}，我们可以从以下几个维度理解其重要性：首先，这些热点反映了当前阶段大众最关心的议题；其次，它们往往与技术变革、社会转型或文化演变密切相关；最后，热点的爆发并非偶然，而是多种因素共同作用的结果。从数据来看，相关话题的搜索指数和讨论量持续攀升，表明公众对此有着强烈的好奇心和求知欲。"
    },
    {
        "heading": "深度解读与思考",
        "template": "从更宏观的角度来看，{topics}揭示了更深层次的社会现象。不同立场的观点碰撞，让我们得以从多角度审视同一问题。值得注意的是，在信息高度碎片化的今天，保持理性判断尤为关键。我们既要关注热点的表面信息，更要洞察其背后的本质。每一个热点话题，都是时代发展的一个切片，折射出社会的变迁与大众的心声。"
    },
]

EXTRA_SECTION = {
    "heading": "延伸阅读与观点碰撞",
    "template": "除了上述分析，我们还关注到业内专家学者对此话题的多元解读。有观点认为，{topics}所代表的趋势将持续深化，成为推动行业变革的重要力量；也有声音指出，我们需要警惕其中可能存在的泡沫和过度炒作。无论如何，保持学习和思辨的心态，是应对变化的最佳策略。在这个过程中，多元化的视角和批判性思维显得尤为重要。"
}


def _call_ai_api(topic_titles, topic_content, style, word_count, depth):
    """调用 AI API 生成博客内容"""
    cfg = get_ai_config()
    base_url = cfg.get("base_url", "").rstrip("/")
    api_key = cfg.get("api_key", "")
    model = cfg.get("model", "gpt-3.5-turbo")

    st = STYLE_CONFIG.get(style, STYLE_CONFIG["professional"])
    dp = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["deep"])

    word_ranges = {"short": "300-500", "standard": "800-1200", "long": "1500-2000"}
    wc = word_ranges.get(word_count, "800-1200")

    system_prompt = (
        f"你是一个专业的博客写手。请根据以下热点话题创作一篇高质量的博客文章。"
        f"写作风格：{st['tone']}。字数范围：{wc}字。"
    )

    user_prompt = (
        f"热点话题：{topic_titles}\n"
        f"话题摘要：{topic_content}\n\n"
        f"请以 JSON 格式返回以下结构（不要包含其他内容）：\n"
        f'{{"title":"文章主标题","subtitle":"副标题",'
        f'"introduction":"引言段落",'
        f'"sections":[{{"heading":"小标题","content":"段落内容"}}, ...],'
        f'"conclusion":"结语段落"}}'
    )

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 3000
    }).encode("utf-8")

    url = f"{base_url}/chat/completions"
    req = request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            return _parse_ai_response(content)
    except error.HTTPError as e:
        logger.error(f"AI API HTTP 错误: {e.code} - {e.read().decode('utf-8', errors='replace')[:300]}")
    except Exception as e:
        logger.error(f"AI API 调用失败: {e}")
    return None


def _parse_ai_response(text):
    """解析 AI 返回的 JSON 文本"""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:]) if lines[0].startswith("```") else text
        if text.endswith("```"):
            text = text[:-3]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass

    return None


def generate_blog(topics, style="professional", word_count="standard", depth="deep"):
    if not topics:
        return None

    topic_titles = "、".join(t.get("title", "") for t in topics)
    topic_content = "。".join(t.get("content", "") for t in topics)

    st = STYLE_CONFIG.get(style, STYLE_CONFIG["professional"])
    dp = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["deep"])

    if is_ai_configured():
        logger.info(f"使用 AI API 生成博客: {topic_titles[:30]}...")
        ai_result = _call_ai_api(topic_titles, topic_content, style, word_count, depth)
        if ai_result:
            if isinstance(ai_result, dict) and "title" in ai_result:
                return ai_result

    logger.info("使用模板引擎生成博客")

    introduction = (
        f"在信息爆炸的时代，{topic_titles}等话题持续占据热搜榜单，引发了社会各界的广泛关注和讨论。"
        f"{dp['analysis']}，我们或许能从中发现时代的脉搏和未来的方向。"
        f"每一个热点背后，都折射出大众的关注焦点与价值取向，蕴含着丰富的信息和启示。"
    )

    if word_count == "short":
        introduction = f"{topic_titles}成为近期热门话题，引发了广泛关注。{dp['analysis']}。"

    num_sections = dp["sections"]
    sections = []
    for i in range(num_sections):
        sec = SECTION_TEMPLATES[i]
        sections.append({
            "heading": sec["heading"],
            "content": sec["template"].format(topics=topic_titles)
        })

    if word_count == "long":
        sections.append({
            "heading": EXTRA_SECTION["heading"],
            "content": EXTRA_SECTION["template"].format(topics=topic_titles)
        })

    conclusion = (
        f"综上所述，{topic_titles}不仅是当下热议的话题，更代表了社会发展的某种趋势。"
        f"我们应当保持开放的心态，在关注热点的同时，也要有自己的独立思考。"
        f"希望本文能为你提供有价值的参考，激发更多的思考与讨论。"
    )

    return {
        "title": f"{topic_titles}：{st['prefix']}前沿话题",
        "subtitle": f"基于{dp['label']} | {st['tone']} | 目标字数：{word_count}字",
        "introduction": introduction,
        "sections": sections,
        "conclusion": conclusion,
        "source": "template"
    }
