# AgentLens

> A local Web UI for [Agent Reach](https://github.com/Panniantong/Agent-Reach) — search, read, and interact with 9 internet platforms from one dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-green?logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow)

## What is AgentLens?

AgentLens provides a clean browser-based interface for Agent Reach's multi-platform internet capabilities. Instead of memorizing CLI commands, you get a unified dashboard to search, browse, and interact across:

| Platform | Features |
|----------|----------|
| **GitHub** | Search repos, view details, browse Issues |
| **XiaoHongShu** (小红书) | Search notes, browse feed, like/favorite |
| **Douyin** (抖音) | Parse videos, get watermark-free download links |
| **Twitter/X** | Search tweets, view user profiles |
| **YouTube** | Get video info, extract subtitles |
| **Bilibili** (B站) | Get video info, extract subtitles |
| **Exa Search** | Semantic web search (free, no API key) |
| **Web Reader** | Extract content from any URL |
| **RSS** | Read any RSS/Atom feed |

## Screenshots

<p align="center">
  <img src="docs/screenshot-home.png" width="800" alt="Home">
</p>

## Prerequisites

- Python 3.10+
- [Agent Reach](https://github.com/Panniantong/Agent-Reach) installed and configured
- Channels you want to use should show ✅ in `agent-reach doctor`

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/anson55sky/AgentLens.git
cd AgentLens

# 2. Install dependencies
pip install flask feedparser

# 3. Start the server
python server.py

# 4. Open browser
open http://127.0.0.1:9800
```

The UI will be available at **http://127.0.0.1:9800**.

## Project Structure

```
AgentLens/
├── server.py          # Flask backend — API routes for all 9 channels
├── static/
│   └── index.html     # Single-page frontend (vanilla JS, no build step)
├── requirements.txt
├── LICENSE
└── README.md
```

## How It Works

AgentLens is a thin web layer that calls the underlying Agent Reach tools:

- **GitHub** → `gh` CLI
- **XiaoHongShu / Douyin** → `mcporter` (MCP protocol)
- **Twitter/X** → `xreach` CLI
- **YouTube / Bilibili** → `yt-dlp`
- **Exa Search** → `mcporter` + Exa MCP
- **Web Reader** → Jina Reader API
- **RSS** → `feedparser` library

No API keys needed for most channels. XiaoHongShu requires browser cookies (see Agent Reach docs).

## Configuration

All channel configuration is managed by Agent Reach. Run `agent-reach doctor` to check which channels are available.

```bash
# Check channel status
agent-reach doctor

# Configure channels as needed
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
agent-reach configure proxy http://user:pass@ip:port
```

## License

MIT
