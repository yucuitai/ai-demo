# 博客智能体 (Blog Agent)

> AI 驱动的图文博客生成工具 — 热点抓取 → AI 写作 → 图片生成 → 图文混排 → 一键导出

轻量化全栈 Web 应用，前后端分离，无需 MySQL。支持 OpenAI 兼容接口，内置 MCP 热点引擎，10 种写作风格 + 10 种图片风格，三种排版模式，多格式导出。

---

## 目录

- [项目架构](#项目架构)
- [数据流](#数据流)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [API 接口文档](#api-接口文档)
- [AI API 配置](#ai-api-配置)
- [MCP 热点引擎](#mcp-热点引擎)
- [项目结构](#项目结构)
- [部署](#部署)
- [环境要求](#环境要求)
- [License](#license)

---

## 项目架构

```
 ┌──────────────────────────────────────────────────────────┐
 │                        client/                           │
 │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
 │  │  index.html  │  │   app.js      │  │  styles.css    │  │
 │  │  主页面布局   │  │  状态管理/API │  │  3 种排版方案   │  │
 │  └─────────────┘  └──────────────┘  └────────────────┘  │
 └────────────┬─────────────────────────────────────────────┘
              │  HTTP RESTful API (Fetch)
              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                     server/ (Flask)                       │
 │  ┌─────────────────────────────────────────────────────┐ │
 │  │                    app.py                            │ │
 │  │  路由: /api/hotspots  /api/blog  /api/images         │ │
 │  │        /api/config    /api/uploads  /api/health       │ │
 │  └──────────┬──────────────────────────────────────────┘ │
 │             │                                             │
 │  ┌──────────┴──────────────────────────────────────────┐ │
 │  │              services/ (业务层)                       │ │
 │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│ │
 │  │  │hotspots  │ │blog_gen  │ │images    │ │config    ││ │
 │  │  │热点服务   │ │博客生成   │ │图片服务   │ │配置管理   ││ │
 │  │  └────┬─────┘ └──────────┘ └──────────┘ └──────────┘│ │
 │  │       │                                                │ │
 │  │  ┌────┴─────────────────────────────────────────────┐ │ │
 │  │  │          mcp_client.py                            │ │ │
 │  │  │   JSON-RPC stdio ↔ MCP hotnews 服务器              │ │ │
 │  │  └──────────────────────────┬───────────────────────┘ │ │
 │  └─────────────────────────────┼─────────────────────────┘ │
 └────────────────────────────────┼───────────────────────────┘
                                  │  stdio
                                  ▼
                   ┌─────────────────────────────┐
                   │    MCP Hot News Server        │
                   │  @wopal/mcp-server-hotnews    │
                   │  知乎/百度/微博/B站/抖音       │
                   │  36氪/虎扑/豆瓣/IT新闻         │
                   └─────────────────────────────┘
```

## 数据流

```
1. 页面加载 → GET /api/hotspots → MCP 拉取 → 渲染热点卡片
2. 用户选择 → POST /api/blog/generate → AI API / 模板引擎 → 富文本编辑
3. 图片需求 → POST /api/images/generate → AI API / Placeholder → 插入预览
4. 排版调整 → 前端 CSS 切换（居中/居左/居右 / 标准/杂志/紧凑）
5. 导出保存 → HTML / Markdown / TXT 下载 / 一键复制
```

## 核心功能

| 模块 | 功能 | 详情 |
|------|------|------|
| 🔥 热点抓取 | 9 大平台实时热榜 | 知乎、百度、微博、B站、抖音、36氪、虎扑、豆瓣、IT新闻 |
| ✍️ 内容生成 | AI + 模板双引擎 | 4 种风格 × 3 档字数 × 2 级深度，结构完整（标题/引言/正文/结语） |
| 🎨 图片生成 | AI + 本地上传 | 10 种视觉风格 + 自定义描述 + 5 种比例 + 批量上传 |
| 📐 图文混排 | 精细化排版 | 图片居中/居左/居右 + 标准/杂志/紧凑三种方案 + 首字下沉 |
| 📦 格式导出 | 多格式输出 | HTML / Markdown / 纯文本，一键复制到剪贴板 |
| ⚙️ API 配置 | UI 可视化配置 | 前端面板填写 API endpoint/key，无需编辑配置文件 |

## 技术栈

| 层 | 技术 |
|---|------|
| 前端框架 | HTML5 + Tailwind CSS (CDN) |
| 前端逻辑 | Vanilla JavaScript (ES6+) |
| 后端框架 | Python 3.11 + Flask |
| 跨域 | Flask-CORS |
| 热点引擎 | MCP (Model Context Protocol) |
| AI 接口 | OpenAI 兼容 (Chat Completions + Images) |
| 富文本 | 原生 textarea + 实时预览 |
| 存储 | JSON 文件 + 本地文件系统 |

## 快速开始

```powershell
# 1. 进入后端目录
cd server

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 返回根目录启动
cd ..
.\start.ps1
```

浏览器打开 **http://localhost:3000**，即可使用。

> **提示**：未配置 AI API 时，内置模板引擎仍可正常生成博客内容。

## API 接口文档

### 热点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/hotspots?type=tech&search=AI&page=1&pageSize=12` | 获取热点列表 |
| `POST` | `/api/hotspots/refresh` | 刷新热点（MCP 实时抓取） |

**响应示例**:
```json
{
  "items": [
    { "id": "1", "title": "AI大模型最新进展...", "content": "...", "hotValue": 98765, "type": "tech", "time": "2小时前" }
  ],
  "total": 12, "page": 1, "pageSize": 12
}
```

### 博客内容

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/blog/generate` | 生成博客内容 |

**请求体**:
```json
{
  "topics": [{"id":"1","title":"热点标题","content":"摘要"}],
  "style": "professional",
  "wordCount": "standard",
  "depth": "deep"
}
```

**参数说明**:
- `style`: `professional` / `casual` / `educational` / `emotional`
- `wordCount`: `short` (300-500) / `standard` (800-1200) / `long` (1500-2000)
- `depth`: `basic` / `deep`

### 图片

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/images/generate` | AI 生成图片 |
| `POST` | `/api/images/upload` | 上传本地图片 (multipart) |
| `GET` | `/api/uploads/<filename>` | 访问已上传图片 |

**生成请求体**:
```json
{
  "keyword": "赛博朋克都市",
  "style": "cyberpunk",
  "width": 800, "height": 450,
  "count": 2
}
```

### 配置

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/config` | 获取当前配置（Key 脱敏） |
| `PUT` | `/api/config/ai` | 更新文本生成配置 |
| `PUT` | `/api/config/image` | 更新图片生成配置 |
| `GET` | `/api/health` | 健康检查 |

## AI API 配置

### 方式一：前端面板（推荐）

点击页面顶部 **⚙ API 设置** 按钮：

1. **AI 文本生成**：填写 Base URL、API Key、模型名 → 保存
2. **AI 图片生成**：填写 Base URL、API Key、模型名 → 保存

Key 保存后前端显示脱敏预览（`sk-****`），安全不回显。

### 方式二：手动编辑

创建 `server/config.json`：

```json
{
  "ai": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-your-key-here",
    "model": "gpt-3.5-turbo"
  },
  "image": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-your-key-here",
    "model": "dall-e-3"
  }
}
```

> ⚠️ `config.json` 已加入 `.gitignore`，不会被提交到 Git。

### 支持的 AI 平台

兼容 OpenAI Chat Completions + Images API 格式的服务均可使用：

- OpenAI（GPT / DALL-E）
- Azure OpenAI Service
- 阿里云百炼（DashScope）
- DeepSeek
- 智谱 GLM
- 其他 OpenAI 兼容代理

## MCP 热点引擎

项目集成了 MCP (Model Context Protocol) 热点抓取服务器：

| 平台 ID | 平台名称 |
|---------|----------|
| 1 | 知乎热榜 |
| 2 | 36氪热榜 |
| 3 | 百度热点 |
| 4 | B站热榜 |
| 5 | 微博热搜 |
| 6 | 抖音热点 |
| 7 | 虎扑热榜 |
| 8 | 豆瓣热榜 |
| 9 | IT 新闻 |

**工作流程**：
1. Python 后端通过 `subprocess` 启动 MCP 服务器
2. 通过 stdio JSON-RPC 2.0 协议通信
3. 调用 `get_hot_news` 工具获取实时热点
4. 网络不可达时自动回退本地缓存

## 项目结构

```
ai-demo/
├── client/                          # 前端 (SPA)
│   ├── index.html                   # 主页面 — 热点面板 + 编辑区 + 预览区 + 配置面板
│   ├── app.js                       # 核心逻辑 — API 调用、状态管理、排版控制
│   └── styles.css                   # 样式 — 标准/杂志/紧凑三种排版方案
│
├── server/                          # 后端 (Python Flask)
│   ├── app.py                       # Flask 主应用 — 路由注册、启动日志
│   ├── config.json                  # API 配置（不入 Git）
│   ├── requirements.txt             # Python 依赖
│   ├── services/                    # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── config.py                # 配置读写服务
│   │   ├── mcp_client.py            # MCP 客户端（JSON-RPC stdio）
│   │   ├── hotspots.py              # 热点数据服务
│   │   ├── blog_generator.py        # 博客生成服务（AI + 模板）
│   │   └── images.py                # 图片服务（AI + Placeholder）
│   └── data/                        # 文件存储
│       ├── hotspots.json            # 热点缓存
│       └── uploads/                 # 用户上传图片
│
├── start.ps1                        # 启动脚本
├── deploy.ps1                       # GitHub 一键部署
├── README.md                        # 本文件
└── .gitignore
```

## 部署

### 本地开发

```powershell
.\start.ps1
```

### GitHub

```powershell
# 交互式（按提示输入用户名和 Token）
.\deploy.ps1

# 直接传参
.\deploy.ps1 -Username "your-name" -Token "ghp_xxxx" -RepoName "blog-agent"
```

### 生产环境

建议使用 Gunicorn 替代 Flask 内置服务器：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 app:app
```

## 环境要求

| 依赖 | 最低版本 | 用途 |
|------|----------|------|
| Python | 3.11+ | 后端运行时 |
| Flask | 3.0+ | Web 框架 |
| Flask-CORS | 4.0+ | 跨域支持 |
| Node.js | 20+ | MCP 热点服务器 (npx) |
| Git | 2.40+ | 部署推送 |

> 无 Node.js 时热点功能自动降级为本地缓存，不影响其他功能使用。

## License

MIT
