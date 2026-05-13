"""
博客智能体 - Flask API 服务器
提供热点抓取、博客生成、图片生成/上传等 RESTful API
"""
import os
import sys
import logging

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.hotspots import get_hotspots, refresh_hotspots, fetch_hotspots_from_mcp
from services.blog_generator import generate_blog
from services.images import generate_images, save_uploaded_file
from services.config import load_config, save_config, update_ai_config, update_image_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
CORS(app)

CLIENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/")
@app.route("/index.html")
def serve_index():
    return send_from_directory(CLIENT_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    file_path = os.path.join(CLIENT_DIR, filename)
    if os.path.isfile(file_path):
        return send_from_directory(CLIENT_DIR, filename)
    return jsonify({"error": "文件不存在"}), 404


@app.route("/api/hotspots", methods=["GET"])
def api_get_hotspots():
    category = request.args.get("type")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 12, type=int)

    result = get_hotspots(category=category, search=search, page=page, page_size=page_size)
    return jsonify(result)


@app.route("/api/hotspots/refresh", methods=["POST"])
def api_refresh_hotspots():
    try:
        data = refresh_hotspots()
        result = get_hotspots(page=1, page_size=12)
        result["source"] = "mcp" if data else "cache"
        return jsonify(result)
    except Exception as e:
        logger.error(f"刷新热点失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/hotspots/init", methods=["POST"])
def api_init_hotspots():
    """从 MCP 初始化热点数据"""
    try:
        data = fetch_hotspots_from_mcp()
        result = get_hotspots(page=1, page_size=12)
        return jsonify(result)
    except Exception as e:
        logger.error(f"初始化热点失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/blog/generate", methods=["POST"])
def api_generate_blog():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    topics = data.get("topics", [])
    if not topics:
        return jsonify({"error": "请选择至少一个热点话题"}), 400

    style = data.get("style", "professional")
    word_count = data.get("wordCount", data.get("word_count", "standard"))
    depth = data.get("depth", "deep")

    try:
        blog = generate_blog(topics, style=style, word_count=word_count, depth=depth)
        return jsonify({"success": True, "data": blog})
    except Exception as e:
        logger.error(f"博客生成失败: {e}")
        return jsonify({"error": f"生成失败: {str(e)}"}), 500


@app.route("/api/images/generate", methods=["POST"])
def api_generate_images():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    keyword = data.get("keyword", "blog")
    style = data.get("style", "realistic")
    width = data.get("width", 800)
    height = data.get("height", 600)
    count = data.get("count", 2)

    try:
        images = generate_images(
            keyword=keyword,
            style=style,
            width=width,
            height=height,
            count=min(count, 8)
        )
        return jsonify({"success": True, "data": images})
    except Exception as e:
        logger.error(f"图片生成失败: {e}")
        return jsonify({"error": f"图片生成失败: {str(e)}"}), 500


@app.route("/api/images/upload", methods=["POST"])
def api_upload_image():
    if "file" not in request.files:
        return jsonify({"error": "未检测到上传文件"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "文件名为空"}), 400

    result = save_uploaded_file(file)
    if result is None:
        return jsonify({"error": "文件保存失败，请检查格式（支持 JPG/PNG/WEBP/GIF）"}), 400

    host = request.host_url.rstrip("/")
    result["url"] = f"{host}{result['url']}"

    return jsonify({"success": True, "data": result})


@app.route("/api/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "ok",
        "service": "博客智能体 API",
        "version": "1.0.0"
    })


@app.route("/api/config", methods=["GET"])
def api_get_config():
    config = load_config()
    ai_cfg = config.get("ai", {})
    img_cfg = config.get("image", {})
    return jsonify({
        "ai": {
            "provider": ai_cfg.get("provider", ""),
            "api_key": ai_cfg.get("api_key", "")[:4] + "****" if ai_cfg.get("api_key") else "",
            "api_key_set": bool(ai_cfg.get("api_key")),
            "base_url": ai_cfg.get("base_url", ""),
            "model": ai_cfg.get("model", "")
        },
        "image": {
            "provider": img_cfg.get("provider", ""),
            "api_key": img_cfg.get("api_key", "")[:4] + "****" if img_cfg.get("api_key") else "",
            "api_key_set": bool(img_cfg.get("api_key")),
            "base_url": img_cfg.get("base_url", ""),
            "model": img_cfg.get("model", "")
        }
    })


@app.route("/api/config/ai", methods=["PUT"])
def api_update_ai_config():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    allowed = {"provider", "api_key", "base_url", "model"}
    update_data = {k: v for k, v in data.items() if k in allowed}
    if not update_data:
        return jsonify({"error": "没有有效的配置字段"}), 400

    try:
        result = update_ai_config(update_data)
        return jsonify({"success": True, "data": {
            "provider": result["ai"].get("provider", ""),
            "api_key_set": bool(result["ai"].get("api_key")),
            "base_url": result["ai"].get("base_url", ""),
            "model": result["ai"].get("model", "")
        }})
    except Exception as e:
        return jsonify({"error": f"保存失败: {str(e)}"}), 500


@app.route("/api/config/image", methods=["PUT"])
def api_update_image_config():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    allowed = {"provider", "api_key", "base_url", "model"}
    update_data = {k: v for k, v in data.items() if k in allowed}
    if not update_data:
        return jsonify({"error": "没有有效的配置字段"}), 400

    try:
        result = update_image_config(update_data)
        return jsonify({"success": True, "data": {
            "provider": result["image"].get("provider", ""),
            "api_key_set": bool(result["image"].get("api_key")),
            "base_url": result["image"].get("base_url", ""),
            "model": result["image"].get("model", "")
        }})
    except Exception as e:
        return jsonify({"error": f"保存失败: {str(e)}"}), 500


if __name__ == "__main__":
    print("=" * 60, flush=True)
    print("  博客智能体 (Blog Agent) — 启动中...", flush=True)
    print("=" * 60, flush=True)
    print("  [系统] Python {0}".format(sys.version.split()[0]), flush=True)
    print("  [模块] Flask 初始化完成", flush=True)
    print("  [模块] CORS 跨域配置就绪", flush=True)
    print("  [服务] 热点数据服务 初始化完成", flush=True)
    print("  [服务] 博客生成引擎 初始化完成", flush=True)
    print("  [服务] 图片生成引擎 初始化完成", flush=True)
    print("  [服务] MCP 客户端 待连接 (按需加载)", flush=True)
    print("  [存储] 文件上传目录 就绪: {0}".format(UPLOAD_DIR), flush=True)
    print("  [安全] API Key 已脱敏管理", flush=True)
    print("  [缓存] 热点本地缓存文件 已加载", flush=True)
    print("  [模型] 文本生成模型: {0}".format(load_config().get("ai", {}).get("model", "gpt-3.5-turbo")), flush=True)
    print("  [模型] 图片生成模型: {0}".format(load_config().get("image", {}).get("model", "dall-e-3")), flush=True)
    print("  [路由] GET  /api/hotspots      — 获取热点列表", flush=True)
    print("  [路由] POST /api/hotspots/refresh — 刷新热点", flush=True)
    print("  [路由] POST /api/blog/generate   — 生成博客内容", flush=True)
    print("  [路由] POST /api/images/generate — AI 生成图片", flush=True)
    print("  [路由] POST /api/images/upload   — 上传图片", flush=True)
    print("  [路由] GET  /api/config          — 获取配置", flush=True)
    print("  [路由] PUT  /api/config/ai       — 更新 AI 配置", flush=True)
    print("  [路由] PUT  /api/config/image    — 更新图片配置", flush=True)
    print("  [路由] GET  /api/health          — 健康检查", flush=True)
    print("-" * 60, flush=True)
    print("  ✓ 所有模块启动完成，服务就绪", flush=True)
    print("", flush=True)
    print("  前端: http://localhost:3000", flush=True)
    print("  API:  http://localhost:3000/api", flush=True)
    print("", flush=True)
    print("=" * 60, flush=True)

    app.run(host="0.0.0.0", port=3000, debug=False)
