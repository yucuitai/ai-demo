# 博客智能体 (Blog Agent)

AI 驱动的图文博客生成工具，前后端分离架构，支持热点抓取、AI 内容生成、图片生成、图文混排、多格式导出。

---

## 项目架构

```
blog-agent/
├── client/                        # 前端 (SPA)
│   ├── index.html                 # 主页面 — 热点面板 + 编辑区 + 预览区
│   ├── app.js                     # 核心逻辑 — API 调用、状态管理、交互
│   └── styles.css                 # 样式 — 含标准/杂志/紧凑三种排版
│
├── server/                        # 后端 (Python Flask)
│   ├── app.py                     # Flask 主应用 — 路由注册、静态文件服务
│   ├── requirements.txt           # Python 依赖
│   ├── config.json                # API 配置 — AI 模型 endpoint、key
│   ├── services/                  # 业务逻辑层
│   │   ├── mcp_client.py          # MCP 客户端 — 与 hotnews MCP 服务器通信
│   │   ├── hotspots.py            # 热点数据服务 — MCP 抓取 / 本地缓存回退
│   │   ├── blog_generator.py      # 博客生成服务 — 结构化内容生成
│   │   └── images.py              # 图片服务 — AI 生成 / 本地上传
│   └── data/                      # 文件存储
│       ├── hotspots.json          # 热点缓存
│       └── uploads/               # 用户上传图片
│
├── start.ps1                      # 启动脚本
├── deploy.ps1                     # GitHub 一键部署脚本
└── .gitignore
```

## 数据流

```
┌──────────┐   HTTP (Fetch)   ┌──────────────┐   MCP (stdio)   ┌─────────────┐
│  client/ │ ◄──────────────► │  server/app.py│ ◄──────────────►│ MCP hotnews │
│  浏览器   │   RESTful API    │   Flask :3000  │                  │  npx server │
└──────────┘                  └──────┬───────┘                  └─────────────┘
                                     │
                              ┌──────┴───────┐
                              │   services/   │
                              │  · hotspots   │
                              │  · blog_gen   │
                              │  · images     │
                              └──────────────┘
```

## API 接口

| 方法   | 路径                    | 说明               |
|--------|-------------------------|--------------------|
| GET    | `/api/hotspots`         | 获取热点列表（支持分类/搜索/分页） |
| POST   | `/api/hotspots/refresh` | 刷新热点（MCP 实时抓取） |
| POST   | `/api/blog/generate`    | 生成博客内容（风格/字数/深度） |
| POST   | `/api/images/generate`  | AI 生成图片（风格/比例/数量） |
| POST   | `/api/images/upload`    | 上传本地图片        |
| GET    | `/api/uploads/<file>`   | 访问已上传图片      |
| GET    | `/api/health`           | 健康检查            |

## 技术栈

| 层     | 技术                                |
|--------|-------------------------------------|
| 前端   | HTML5 + Tailwind CSS + Vanilla JS   |
| 后端   | Python 3.11 + Flask + Flask-CORS    |
| 热点   | MCP hotnews（@wopal/mcp-server-hotnews） |
| AI 生成 | 可配置 endpoint + API key（支持 OpenAI 兼容接口） |
| 运行时 | PowerShell（无需额外运行时安装 Node.js） |

## 快速开始

```powershell
# 1. 安装依赖
cd server
pip install -r requirements.txt

# 2. 配置 AI API（编辑 server/config.json）
#    → 填写你的 API endpoint 和 key

# 3. 启动
cd ..
.\start.ps1

# 4. 打开浏览器
#    http://localhost:3000
```

## 配置 AI API

编辑 `server/config.json`：

```json
{
  "ai": {
    "provider": "openai",
    "api_key": "sk-your-key-here",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo"
  },
  "image": {
    "provider": "openai",
    "api_key": "sk-your-key-here",
    "base_url": "https://api.openai.com/v1",
    "model": "dall-e-3"
  }
}
```

也可通过前端页面 **设置面板** 直接配置，无需手动编辑文件。

## 核心功能

1. **热点抓取** — MCP 实时拉取知乎/百度/微博/B站等 9 个平台热榜，支持分类筛选与搜索
2. **内容生成** — 10 种写作风格 + 3 档字数 + 2 级深度，生成结构化原创博客
3. **图片生成** — 10 种视觉风格 + 自定义描述 + 5 种比例 + 本地上传
4. **图文混排** — 图片居中/居左/居右 + 标准/杂志/紧凑三种排版
5. **格式导出** — HTML / Markdown / 纯文本，一键复制或下载

## 环境要求

- Windows PowerShell 5.1+
- Python 3.11+（Flask）
- Node.js 20+（仅 MCP hotnews 需要 npx）
- 网络连接（热点抓取需要）
