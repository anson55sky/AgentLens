# -*- coding: utf-8 -*-
"""Agent Reach Web UI — Flask backend with all 9 channels."""

import json
import subprocess
import feedparser
import urllib.request
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

MCPORTER = "mcporter"
GH = "gh"
XREACH = "xreach"
YTDLP = "yt-dlp"
TIMEOUT = 60


def run_cmd(cmd, timeout=TIMEOUT):
    """Run a shell command and return (ok, output)."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str)
        )
        output = (r.stdout + r.stderr).strip()
        return r.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "请求超时，请稍后重试"
    except Exception as e:
        return False, str(e)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/status")
def status():
    ok, out = run_cmd(["agent-reach", "doctor"], timeout=30)
    return jsonify({"ok": ok, "output": out})


# ═══════════════════════════════════════════════════════════════════════
#  GitHub
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/github/search")
def github_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"ok": False, "error": "请输入搜索关键词"})
    ok, out = run_cmd([GH, "search", "repos", q, "--limit", "10", "--json",
                       "fullName,description,stargazersCount,url,language,updatedAt"])
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "data": [], "raw": out})
    return jsonify({"ok": False, "error": out})


@app.route("/api/github/repo")
def github_repo():
    repo = request.args.get("repo", "").strip()
    if not repo or "/" not in repo:
        return jsonify({"ok": False, "error": "请输入正确的仓库名，格式：owner/repo"})
    ok, out = run_cmd([GH, "repo", "view", repo, "--json",
                       "name,description,stargazerCount,forkCount,url,defaultBranchRef"])
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out})
    return jsonify({"ok": False, "error": out})


@app.route("/api/github/issues")
def github_issues():
    repo = request.args.get("repo", "").strip()
    if not repo or "/" not in repo:
        return jsonify({"ok": False, "error": "请输入正确的仓库名"})
    ok, out = run_cmd([GH, "issue", "list", "-R", repo, "--limit", "10", "--json",
                       "number,title,state,author,createdAt,url"])
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "data": [], "raw": out})
    return jsonify({"ok": False, "error": out})


# ═══════════════════════════════════════════════════════════════════════
#  XiaoHongShu
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/xhs/search")
def xhs_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"ok": False, "error": "请输入搜索关键词"})
    cmd = f'{MCPORTER} call \'xiaohongshu.search_feeds(keyword: "{q}")\' --timeout 60000'
    ok, out = run_cmd(cmd, timeout=65)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out})
    return jsonify({"ok": False, "error": out})


@app.route("/api/xhs/home")
def xhs_home():
    cmd = f"{MCPORTER} call 'xiaohongshu.list_feeds()' --timeout 60000"
    ok, out = run_cmd(cmd, timeout=65)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out})
    return jsonify({"ok": False, "error": out})


@app.route("/api/xhs/detail")
def xhs_detail():
    feed_id = request.args.get("feed_id", "")
    xsec_token = request.args.get("xsec_token", "")
    if not feed_id or not xsec_token:
        return jsonify({"ok": False, "error": "缺少 feed_id 或 xsec_token"})
    cmd = (f'{MCPORTER} call \'xiaohongshu.get_feed_detail('
           f'feed_id: "{feed_id}", xsec_token: "{xsec_token}")\' --timeout 60000')
    ok, out = run_cmd(cmd, timeout=65)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out})
    return jsonify({"ok": False, "error": out})


@app.route("/api/xhs/like", methods=["POST"])
def xhs_like():
    body = request.json or {}
    feed_id = body.get("feed_id", "")
    xsec_token = body.get("xsec_token", "")
    unlike = "true" if body.get("unlike") else "false"
    if not feed_id or not xsec_token:
        return jsonify({"ok": False, "error": "缺少参数"})
    cmd = (f'{MCPORTER} call \'xiaohongshu.like_feed('
           f'feed_id: "{feed_id}", xsec_token: "{xsec_token}", unlike: {unlike})\' --timeout 30000')
    ok, out = run_cmd(cmd, timeout=35)
    return jsonify({"ok": ok, "output": out})


@app.route("/api/xhs/favorite", methods=["POST"])
def xhs_favorite():
    body = request.json or {}
    feed_id = body.get("feed_id", "")
    xsec_token = body.get("xsec_token", "")
    unfav = "true" if body.get("unfavorite") else "false"
    if not feed_id or not xsec_token:
        return jsonify({"ok": False, "error": "缺少参数"})
    cmd = (f'{MCPORTER} call \'xiaohongshu.favorite_feed('
           f'feed_id: "{feed_id}", xsec_token: "{xsec_token}", unfavorite: {unfav})\' --timeout 30000')
    ok, out = run_cmd(cmd, timeout=35)
    return jsonify({"ok": ok, "output": out})


# ═══════════════════════════════════════════════════════════════════════
#  Douyin
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/douyin/parse")
def douyin_parse():
    link = request.args.get("link", "")
    if not link:
        return jsonify({"ok": False, "error": "请输入抖音分享链接"})
    cmd = f'{MCPORTER} call \'douyin.parse_douyin_video_info(share_link: "{link}")\' --timeout 30000'
    ok, out = run_cmd(cmd, timeout=35)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out})
    return jsonify({"ok": False, "error": out})


@app.route("/api/douyin/download")
def douyin_download():
    link = request.args.get("link", "")
    if not link:
        return jsonify({"ok": False, "error": "请输入抖音分享链接"})
    cmd = f'{MCPORTER} call \'douyin.get_douyin_download_link(share_link: "{link}")\' --timeout 30000'
    ok, out = run_cmd(cmd, timeout=35)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out})
    return jsonify({"ok": False, "error": out})


# ═══════════════════════════════════════════════════════════════════════
#  YouTube (yt-dlp)
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/youtube/info")
def youtube_info():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入 YouTube 视频链接"})
    ok, out = run_cmd([YTDLP, "--dump-json", "--no-download", "--no-playlist", url], timeout=30)
    if ok:
        try:
            d = json.loads(out)
            return jsonify({"ok": True, "data": {
                "title": d.get("title", ""),
                "uploader": d.get("uploader", ""),
                "duration_string": d.get("duration_string", ""),
                "view_count": d.get("view_count"),
                "like_count": d.get("like_count"),
                "upload_date": d.get("upload_date", ""),
                "description": (d.get("description") or "")[:1000],
                "thumbnail": d.get("thumbnail", ""),
                "webpage_url": d.get("webpage_url", ""),
            }})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out[:2000]})
    return jsonify({"ok": False, "error": out[:500]})


@app.route("/api/youtube/subtitles")
def youtube_subtitles():
    import glob
    import os
    import tempfile
    url = request.args.get("url", "")
    lang = request.args.get("lang", "zh-Hans,zh,en")
    if not url:
        return jsonify({"ok": False, "error": "请输入 YouTube 视频链接"})
    # Use a unique temp dir to avoid file conflicts
    tmpdir = tempfile.mkdtemp(prefix="yt_sub_")
    out_tpl = os.path.join(tmpdir, "%(id)s.%(ext)s")
    ok, out = run_cmd([
        YTDLP, "--write-auto-sub", "--write-sub", "--sub-lang", lang,
        "--sub-format", "vtt/srt/best", "--skip-download",
        "-o", out_tpl, url
    ], timeout=45)
    # Find any subtitle file
    sub_files = glob.glob(os.path.join(tmpdir, "*.vtt")) + \
                glob.glob(os.path.join(tmpdir, "*.srt")) + \
                glob.glob(os.path.join(tmpdir, "*.*"))
    # Filter to subtitle files only
    sub_files = [f for f in sub_files if f.endswith(('.vtt', '.srt', '.ass'))]
    if sub_files:
        with open(sub_files[0], "r", encoding="utf-8") as f:
            content = f.read()
        # Clean to plain text
        lines = []
        seen = set()
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("WEBVTT") or line.startswith("Kind:") \
               or line.startswith("Language:") or "-->" in line or line.isdigit() \
               or line.startswith("[Script Info") or line.startswith("Style:") \
               or line.startswith("Dialogue:") and "," in line:
                # For ASS format, extract text after last comma
                if line.startswith("Dialogue:") and "," in line:
                    text = line.split(",", 9)[-1].strip() if line.count(",") >= 9 else ""
                    text = text.replace("\\N", " ").strip()
                    if text and text not in seen:
                        seen.add(text)
                        lines.append(text)
                continue
            if line not in seen:
                seen.add(line)
                lines.append(line)
        # Cleanup
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({"ok": True, "data": {"text": "\n".join(lines)}})
    # Cleanup on failure too
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)
    # Include yt-dlp output for debugging
    hint = ""
    if "timed out" in out or "Unable to download" in out:
        hint = "网络连接超时，YouTube 可能需要代理访问"
    elif "no subtitles" in out.lower() or "no automatic captions" in out.lower():
        hint = "该视频没有可用的字幕"
    else:
        hint = "未找到字幕文件"
    return jsonify({"ok": False, "error": hint})


# ═══════════════════════════════════════════════════════════════════════
#  Twitter/X (xreach)
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/twitter/search")
def twitter_search():
    q = request.args.get("q", "")
    count = request.args.get("count", "20")
    if not q:
        return jsonify({"ok": False, "error": "请输入搜索关键词"})
    ok, out = run_cmd([XREACH, "search", q, "-n", count, "--json"], timeout=30)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out[:3000]})
    return jsonify({"ok": False, "error": out[:500]})


@app.route("/api/twitter/user")
def twitter_user():
    handle = request.args.get("handle", "").lstrip("@")
    if not handle:
        return jsonify({"ok": False, "error": "请输入用户名"})
    ok, out = run_cmd([XREACH, "user", handle, "--json"], timeout=15)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out[:2000]})
    return jsonify({"ok": False, "error": out[:500]})


@app.route("/api/twitter/tweet")
def twitter_tweet():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入推文链接或ID"})
    ok, out = run_cmd([XREACH, "tweet", url, "--json"], timeout=15)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out[:2000]})
    return jsonify({"ok": False, "error": out[:500]})


# ═══════════════════════════════════════════════════════════════════════
#  Bilibili (yt-dlp)
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/bilibili/info")
def bilibili_info():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入B站视频链接"})
    ok, out = run_cmd([YTDLP, "--dump-json", "--no-download", "--no-playlist", url], timeout=30)
    if ok:
        try:
            d = json.loads(out)
            return jsonify({"ok": True, "data": {
                "title": d.get("title", ""),
                "uploader": d.get("uploader", ""),
                "duration_string": d.get("duration_string", ""),
                "view_count": d.get("view_count"),
                "like_count": d.get("like_count"),
                "comment_count": d.get("comment_count"),
                "upload_date": d.get("upload_date", ""),
                "description": (d.get("description") or "")[:1000],
                "thumbnail": d.get("thumbnail", ""),
                "webpage_url": d.get("webpage_url", ""),
            }})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out[:2000]})
    return jsonify({"ok": False, "error": out[:500]})


@app.route("/api/bilibili/subtitles")
def bilibili_subtitles():
    import glob
    import os
    import tempfile
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入B站视频链接"})
    tmpdir = tempfile.mkdtemp(prefix="bili_sub_")
    out_tpl = os.path.join(tmpdir, "%(id)s.%(ext)s")
    ok, out = run_cmd([
        YTDLP, "--write-auto-sub", "--write-sub", "--sub-lang", "zh-Hans,zh,en",
        "--sub-format", "vtt/srt/best", "--skip-download",
        "-o", out_tpl, url
    ], timeout=45)
    sub_files = glob.glob(os.path.join(tmpdir, "*.vtt")) + \
                glob.glob(os.path.join(tmpdir, "*.srt")) + \
                glob.glob(os.path.join(tmpdir, "*.ass"))
    if sub_files:
        with open(sub_files[0], "r", encoding="utf-8") as f:
            content = f.read()
        lines = []
        seen = set()
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("WEBVTT") or "-->" in line or line.isdigit() \
               or line.startswith("[Script Info") or line.startswith("Style:"):
                continue
            if line.startswith("Dialogue:") and "," in line:
                text = line.split(",", 9)[-1].strip() if line.count(",") >= 9 else ""
                text = text.replace("\\N", " ").strip()
                if text and text not in seen:
                    seen.add(text)
                    lines.append(text)
                continue
            if line not in seen:
                seen.add(line)
                lines.append(line)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({"ok": True, "data": {"text": "\n".join(lines)}})
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)
    hint = "网络连接超时" if ("timed out" in out) else "未找到字幕"
    return jsonify({"ok": False, "error": hint})


# ═══════════════════════════════════════════════════════════════════════
#  Exa — 全网语义搜索
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/exa/search")
def exa_search():
    q = request.args.get("q", "")
    num = request.args.get("num", "8")
    if not q:
        return jsonify({"ok": False, "error": "请输入搜索关键词"})
    cmd = (f'{MCPORTER} call \'exa.web_search_exa(query: "{q}", numResults: {num})\' --timeout 30000')
    ok, out = run_cmd(cmd, timeout=35)
    if ok:
        try:
            return jsonify({"ok": True, "data": json.loads(out)})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "raw": out[:5000]})
    return jsonify({"ok": False, "error": out[:500]})


# ═══════════════════════════════════════════════════════════════════════
#  任意网页 (Jina Reader)
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/web/read")
def web_read():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入网页链接"})
    jina_url = "https://r.jina.ai/" + url
    try:
        req = urllib.request.Request(jina_url, headers={"Accept": "text/plain"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        return jsonify({"ok": True, "data": {"content": content[:20000], "url": url}})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════
#  RSS
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/rss/read")
def rss_read():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入 RSS/Atom 源地址"})
    try:
        feed = feedparser.parse(url)
        entries = []
        for e in feed.entries[:20]:
            entries.append({
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "published": e.get("published", ""),
                "summary": (e.get("summary") or "")[:300],
                "author": e.get("author", ""),
            })
        return jsonify({"ok": True, "data": {
            "title": feed.feed.get("title", ""),
            "link": feed.feed.get("link", ""),
            "entries": entries,
        }})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9800, debug=False)
