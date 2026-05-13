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


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("  博客智能体 API 服务器启动中...")
    logger.info(f"  前端地址: http://localhost:3000")
    logger.info(f"  API 地址: http://localhost:3000/api")
    logger.info("=" * 50)
    app.run(host="0.0.0.0", port=3000, debug=True)
