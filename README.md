# AgentLens

> A local Web UI for [Agent Reach](https://github.com/Panniantong/Agent-Reach) — search, read, and interact with 9 internet platforms from one dashboard.
>
> 基于 [Agent Reach](https://github.com/Panniantong/Agent-Reach) 的本地 Web UI —— 一个面板搜索、阅读、操作 9 大互联网平台。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-green?logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is AgentLens? / 这是什么？

AgentLens provides a clean browser-based interface for Agent Reach's multi-platform internet capabilities. Instead of memorizing CLI commands, you get a unified dashboard to search, browse, and interact across 9 platforms.

AgentLens 为 Agent Reach 的多平台互联网能力提供了一个简洁的浏览器界面。无需记忆命令行指令，打开浏览器即可一站式搜索、浏览和操作 9 大平台。

| 平台 / Platform | 功能 / Features |
|-----------------|----------------|
| **GitHub** | 搜索仓库、查看详情、浏览 Issues / Search repos, view details, browse Issues |
| **小红书** (XiaoHongShu) | 搜索笔记、首页推荐、点赞收藏 / Search notes, browse feed, like & favorite |
| **抖音** (Douyin) | 解析视频、获取无水印下载链接 / Parse videos, get watermark-free download links |
| **Twitter/X** | 搜索推文、查看用户资料 / Search tweets, view user profiles |
| **YouTube** | 获取视频信息、提取字幕 / Get video info, extract subtitles |
| **B站** (Bilibili) | 获取视频信息、提取字幕 / Get video info, extract subtitles |
| **全网搜索** (Exa Search) | 语义搜索，免费无需 API Key / Semantic web search, free, no API key |
| **任意网页** (Web Reader) | 提取任意网页正文内容 / Extract content from any URL |
| **RSS** | 读取任意 RSS/Atom 订阅源 / Read any RSS/Atom feed |

## Screenshots / 截图

<p align="center">
  <img src="docs/screenshot-home.png" width="800" alt="Home">
</p>

## Prerequisites / 前置要求

- Python 3.10+
- 已安装并配置 [Agent Reach](https://github.com/Panniantong/Agent-Reach)（Install and configure Agent Reach first）
- 运行 `agent-reach doctor` 确认你需要的渠道显示 ✅

## Quick Start / 快速开始

```bash
# 1. 克隆仓库 / Clone this repo
git clone https://github.com/anson55sky/AgentLens.git
cd AgentLens

# 2. 安装依赖 / Install dependencies
pip install -r requirements.txt

# 3. 启动服务 / Start the server
python server.py

# 4. 打开浏览器 / Open browser
open http://127.0.0.1:9800
```

启动后访问 **http://127.0.0.1:9800** 即可使用。

## Project Structure / 项目结构

```
AgentLens/
├── server.py            # Flask 后端，9 个平台的 API 路由
├── static/
│   └── index.html       # 单页前端（原生 JS，无需构建）
├── requirements.txt     # Python 依赖
├── LICENSE
└── README.md
```

## How It Works / 工作原理

AgentLens 是一个轻量 Web 层，调用 Agent Reach 底层工具完成实际操作：

| 平台 | 底层工具 |
|------|---------|
| GitHub | `gh` CLI |
| 小红书 / 抖音 | `mcporter`（MCP 协议） |
| Twitter/X | `xreach` CLI |
| YouTube / B站 | `yt-dlp` |
| 全网搜索 | `mcporter` + Exa MCP |
| 任意网页 | Jina Reader API |
| RSS | `feedparser` 库 |

大部分渠道**无需 API Key**。小红书需要浏览器 Cookie（参见 Agent Reach 文档）。

## Channel Setup / 渠道配置

所有渠道配置由 Agent Reach 管理，运行 `agent-reach doctor` 查看状态：

```bash
# 查看渠道状态 / Check channel status
agent-reach doctor

# 一键安装所有依赖 / Install all dependencies
agent-reach install

# 配置 Twitter Cookie / Configure Twitter cookies
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"

# 配置代理（YouTube/B站等需要时）/ Configure proxy if needed
agent-reach configure proxy http://user:pass@ip:port
```

### 小红书配置 / XiaoHongShu Setup

小红书需要通过 Docker 运行 MCP 服务并导入浏览器 Cookie：

```bash
# 启动小红书 MCP 服务
docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp

# 注册到 mcporter
mcporter config add xiaohongshu http://localhost:18060/mcp

# 在浏览器登录小红书后，用 Cookie-Editor 插件导出 Cookie（Header String 格式）
# 将 Cookie 写入容器
docker cp cookies.json xiaohongshu-mcp:/app/cookies.json
```

### 抖音配置 / Douyin Setup

```bash
pip install douyin-mcp-server
# 启动服务后注册
mcporter config add douyin http://localhost:18070/mcp
```

## License / 许可证

MIT

## Acknowledgments / 致谢

- [Agent Reach](https://github.com/Panniantong/Agent-Reach) — 底层多平台互联网能力框架
- [Exa](https://exa.ai/) — 免费语义搜索
- [Jina Reader](https://jina.ai/reader/) — 网页内容提取
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — 视频信息与字幕提取
