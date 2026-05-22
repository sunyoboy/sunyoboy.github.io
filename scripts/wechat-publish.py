#!/usr/bin/env python3
"""
VitePress Markdown → 微信公众号草稿箱

用法:
  python scripts/wechat-publish.py review/2026/05/2026-05-21.md

前提:
  1. 复制 .env.example 为 .env，填入 AppID/AppSecret
  2. 公众号后台配置 IP 白名单
  3. pip install requests markdown python-dotenv

流程:
  1. 读取 .md → 转为公众号 HTML
  2. 提取首图作为封面 → 上传永久素材
  3. 调用 draft/add → 文章进入草稿箱
"""

import os
import sys
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
import markdown
from dotenv import load_dotenv

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

APPID = os.getenv("WECHAT_APPID")
APPSECRET = os.getenv("WECHAT_APPSECRET")
AUTHOR = os.getenv("WECHAT_AUTHOR", "知行合一")

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"
WECHAT_IMAGE_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"


# ── token 缓存 ────────────────────────────────────────────
TOKEN_CACHE = ROOT / ".wechat_token"


def get_token():
    if TOKEN_CACHE.exists():
        data = json.loads(TOKEN_CACHE.read_text())
        if data.get("ts", 0) > __import__("time").time() - 7000:
            return data["token"]

    resp = requests.get(TOKEN_URL, params={
        "grant_type": "client_credential",
        "appid": APPID,
        "secret": APPSECRET
    }).json()

    if "access_token" not in resp:
        sys.exit(f"获取 token 失败: {resp}")

    token = resp["access_token"]
    TOKEN_CACHE.write_text(json.dumps({
        "token": token,
        "ts": __import__("time").time()
    }))
    return token


# ── 上传永久素材（封面图）─────────────────────────────────
def upload_cover(image_path, token):
    url = f"{MATERIAL_URL}?access_token={token}&type=image"
    with open(image_path, "rb") as f:
        resp = requests.post(url, files={"media": f}).json()
    if "media_id" not in resp:
        sys.exit(f"上传封面失败: {resp}")
    return resp["media_id"]


# ── 上传正文图片（转为 mmbiz.qpic.cn）─────────────────────
def upload_inline_image(image_path, token):
    url = f"{WECHAT_IMAGE_URL}?access_token={token}"
    with open(image_path, "rb") as f:
        resp = requests.post(url, files={"media": f}).json()
    if "url" not in resp:
        print(f"  警告: 上传图片失败 {image_path}: {resp}")
        return None
    return resp["url"]


# ── Markdown → 公众号 HTML ─────────────────────────────────
def md_to_wechat_html(md_text, md_dir, token):
    """将 Markdown 转为公众号兼容的 HTML，处理图片上传"""
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

    # 处理本地图片：上传到微信并替换 URL
    def replace_img(m):
        src = m.group(1)
        if src.startswith("http"):
            return m.group(0)
        img_path = Path(md_dir) / src
        if img_path.exists():
            wx_url = upload_inline_image(str(img_path), token)
            if wx_url:
                return f'<img src="{wx_url}" style="max-width:100%">'
        return m.group(0)

    html = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', replace_img, html)

    # 注入公众号适配样式
    style = """
    <style>
      body { font-size: 16px; color: #3d3a35; line-height: 1.8; }
      h1 { font-size: 22px; margin: 20px 0 12px; }
      h2 { font-size: 19px; margin: 18px 0 10px; }
      h3 { font-size: 17px; margin: 15px 0 8px; }
      table { border-collapse: collapse; width: 100%; margin: 12px 0; }
      th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
      th { background: #f5f5f5; }
      code { background: #f0e8d8; padding: 2px 6px; border-radius: 3px; font-size: 14px; }
      pre { background: #f5ede0; padding: 12px; border-radius: 6px; overflow-x: auto; }
      blockquote { border-left: 3px solid #5b8c5a; padding-left: 12px; color: #666; }
      img { max-width: 100%; height: auto; }
    </style>
    """
    return style + html


# ── 主流程 ─────────────────────────────────────────────────
def main(md_file):
    if not APPID or not APPSECRET:
        sys.exit("请先配置 .env 文件中的 WECHAT_APPID 和 WECHAT_APPSECRET")

    md_path = Path(md_file).resolve()
    if not md_path.exists():
        sys.exit(f"文件不存在: {md_file}")

    md_text = md_path.read_text()
    md_dir = md_path.parent

    # 提取标题（第一个 # 开头行）
    title = "未命名"
    for line in md_text.split("\n"):
        m = re.match(r"^#\s+(.+)", line)
        if m:
            title = m.group(1).strip()
            break

    print(f"标题: {title}")

    token = get_token()
    print(f"Token: {token[:8]}...")

    # 正文 HTML（含图片上传）
    print("转换正文 + 上传图片...")
    content = md_to_wechat_html(md_text, str(md_dir), token)

    # 封面图：尝试用正文第一张图
    thumb_media_id = None
    img_match = re.search(r'!\[.*?\]\((.+?\.(?:jpg|png|jpeg|gif))\)', md_text, re.I)
    if img_match:
        cover_path = Path(md_dir) / img_match.group(1)
        if cover_path.exists():
            print(f"上传封面: {cover_path.name}")
            thumb_media_id = upload_cover(str(cover_path), token)
    if not thumb_media_id:
        sys.exit("未找到封面图，请在 md 第一段前插入一张图片作为封面")

    # 提取摘要（纯文本前 100 字）
    plain = re.sub(r"<[^>]+>", "", content)
    digest = plain[:110]

    # 创建草稿
    print("创建草稿...")
    resp = requests.post(
        f"{DRAFT_URL}?access_token={token}",
        json={
            "articles": [{
                "title": title,
                "author": AUTHOR,
                "digest": digest,
                "thumb_media_id": thumb_media_id,
                "content": content,
                "need_open_comment": 0,
            }]
        }
    ).json()

    if "media_id" in resp:
        print(f"\n✓ 草稿创建成功")
        print(f"  media_id: {resp['media_id']}")
        print(f"  请前往 mp.weixin.qq.com → 草稿箱 查看")
    else:
        print(f"\n✗ 创建失败: {resp}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"用法: python {sys.argv[0]} <markdown文件>")
    main(sys.argv[1])
