#!/usr/bin/env python3
"""
Daily AI Coding Article Publishing Workflow
- Fetches top articles from multiple sources
- Generates Jekyll posts with placeholder for AI rewriting
- Title/content translation done by Hermes Agent's own model
- Commits and pushes to GitHub
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.parse
import ssl
import hashlib
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
POSTS_DIR = WORKSPACE / "_posts"
POSTS_IMAGES_DIR = WORKSPACE / "assets" / "images" / "posts"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ========== Fetchers ==========

def fetch_juejin():
    articles = []
    url = "https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"
    try:
        data = json.dumps({
            "id_type": 2,
            "sort_type": 200,
            "cate_id": "6809637773935378440",
            "cursor": "0",
            "limit": 20
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        if result.get("err_no") == 0:
            for item in result.get("data", [])[:10]:
                art = item.get("article_info", {})
                articles.append({
                    "title": art.get("title", ""),
                    "url": f"https://juejin.cn/post/{art.get('article_id', '')}",
                    "content_preview": art.get("brief_content", "")[:500],
                    "source": "juejin",
                    "author": item.get("author_user_info", {}).get("user_name", ""),
                    "view_count": art.get('view_count', 0),
                    "like_count": art.get('digg_count', 0),
                })
    except Exception as e:
        print(f"Juejin error: {e}")
    return articles

def fetch_hackernews():
    articles = []
    url = "https://hn.algolia.com/api/v1/search?query=ai+OR+llm+OR+copilot+OR+claude+OR+cursor&tags=story&hitsPerPage=10"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode())
        for hit in data.get('hits', [])[:5]:
            articles.append({
                "title": hit.get('title', ''),
                "url": hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "content_preview": f"HN: {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
                "source": "hackernews",
                "author": hit.get('author', ''),
                "view_count": hit.get('points', 0) * 10,
                "like_count": hit.get('points', 0),
            })
    except Exception as e:
        print(f"HN error: {e}")
    return articles

def fetch_github_trending():
    articles = []
    query = urllib.parse.quote("ai coding assistant OR llm programming OR copilot cursor")
    url = f"https://api.github.com/search/repositories?q={query}+language:python&sort=stars&order=desc&per_page=5"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode())
        for repo in data.get('items', [])[:3]:
            articles.append({
                "title": f"{repo.get('full_name', '')}: {repo.get('description', '') or ''}",
                "url": repo.get('html_url', ''),
                "content_preview": f"GitHub: {repo.get('stargazers_count', 0)} stars. {repo.get('description', '')}",
                "source": "github",
                "author": repo.get('owner', {}).get('login', ''),
                "view_count": repo.get('stargazers_count', 0),
                "like_count": repo.get('stargazers_count', 0),
            })
    except Exception as e:
        print(f"GitHub error: {e}")
    return articles

# ========== Article Processing ==========

AI_CODING_KEYWORDS = [
    "ai coding", "ai programming", "copilot", "cursor", "claude", "llm",
    "gpt", "deepseek", "agent", "code generation", "mcp", "autonomous",
    "编程助手", "代码生成", "智能编程",
]
BOOST_KEYWORDS = ["cursor", "claude code", "copilot", "deepseek", "aider", "mcp", "agent"]

def score_article(title, content=''):
    text = f"{title} {content}".lower()
    score = sum(1 for kw in AI_CODING_KEYWORDS if kw in text)
    score += sum(2 for kw in BOOST_KEYWORDS if kw in text)
    return score

def classify_article(title, content=''):
    text = f"{title} {content}".lower()
    tutorial = ['tutorial', 'guide', 'how to', 'step', '入门', '教程', '实战', '手把手', 'build']
    academic = ['research', 'analysis', '原理', '研究', '深入', '架构', 'comparison', '评测']
    t = sum(1 for p in tutorial if p in text)
    a = sum(1 for p in academic if p in text)
    return 'tutorial' if t > a else 'academic'

def generate_slug(title):
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')[:80].lower()

def download_cover(title):
    try:
        seed = hashlib.md5(title.encode()).hexdigest()[:8]
        image_url = f"https://picsum.photos/seed/{seed}/800/400"
        POSTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{seed}.jpg"
        req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            with open(POSTS_IMAGES_DIR / filename, 'wb') as f:
                f.write(resp.read())
        return f"/assets/images/posts/{filename}"
    except Exception as e:
        print(f"Cover error: {e}")
        return None

# ========== Jekyll Post Generation ==========

def create_jekyll_post(article, style):
    """Create a Jekyll post with English title and AI rewrite placeholder"""
    title = article['title']
    url = article['url']
    content_preview = article.get('content_preview', '')
    source = article['source']
    author = article.get('author', 'Unknown')
    views = article.get('view_count', 0)
    likes = article.get('like_count', 0)

    slug = generate_slug(title)
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
    filepath = POSTS_DIR / filename

    # Cover image
    cover = download_cover(title)
    cover_path = cover if cover else "/assets/images/covers/cluade-1.jpg"

    # Rewrite instructions based on style
    if style == 'tutorial':
        rewrite_instructions = """This is a tutorial/guide article. Rewrite as a step-by-step hands-on guide with:
- Clear prerequisites and expected outcomes
- Numbered steps that are executable
- Code examples that are complete and runnable
- "Note" and "Warning" callouts where relevant
- A summary section at the end"""
    else:
        rewrite_instructions = """This is an academic/informational article. Rewrite with:
- Thorough technical depth and background context
- Structured headings for logical flow
- Key data points and comparisons preserved
- Analysis and insights expanded
- A conclusions section at the end"""

    # Build post content (without title in body - title only in frontmatter)
    post_body = f"""## Translation Notes

**Original Title:** {title}
**Original URL:** {url}
**Author:** {author}
**Views:** {views:,} | **Likes:** {likes:,}
**Type:** {style}

---

**Content to translate and rewrite in English:**

{content_preview}

---

**Rewrite Instructions:**

{rewrite_instructions}

<!-- 
Please translate and rewrite the content above into English.
- Title should also be translated to English (update in frontmatter)
- Remove this comment when complete.
-->"""

    # Correct frontmatter format
    frontmatter = f"""---
layout: post
title: "{title}"
subtitle: ""
banner:
  image: {cover_path}
  opacity: 0.7
author: zane.deng
categories: [AI Coding]
tags:
- AI Coding
- Translation
- {source}
---

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + post_body)

    return filepath

# ========== Git Operations ==========

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=WORKSPACE, check=True, capture_output=True)
        msg = f"Daily: AI coding articles queued for rewriting - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], cwd=WORKSPACE, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE, check=True, capture_output=True)
        return {"status": "success", "message": msg}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e)}

# ========== Main ==========

def main():
    print("=" * 60)
    print("Daily AI Coding Article Publishing")
    print("=" * 60)

    # Step 1: Fetch
    print("\n[1/4] Fetching articles...")
    all_articles = []
    for name, fetcher in [("Juejin", fetch_juejin), ("Hacker News", fetch_hackernews), ("GitHub", fetch_github_trending)]:
        print(f"  Fetching {name}...")
        arts = fetcher()
        print(f"    -> {len(arts)} articles")
        all_articles.extend(arts)

    if not all_articles:
        print("No articles fetched.")
        return {"status": "no_articles"}

    # Step 2: Score and filter
    print("\n[2/4] Scoring and filtering...")
    scored = [(score_article(a['title'], a.get('content_preview', '')), a) for a in all_articles]
    scored = [(s, a) for s, a in scored if s >= 1]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [a for _, a in scored[:3]]

    print(f"  Top 3 articles:")
    for i, art in enumerate(top, 1):
        print(f"    {i}. [{art['source']}] {art['title'][:55]}...")

    if not top:
        return {"status": "no_relevant"}

    # Step 3: Generate posts
    print("\n[3/4] Generating Jekyll posts...")
    created = []
    for i, art in enumerate(top, 1):
        style = classify_article(art['title'], art.get('content_preview', ''))
        path = create_jekyll_post(art, style)
        print(f"  [{i}/{len(top)}] {path.name}")
        created.append(path)

    # Step 4: Git push
    print("\n[4/4] Git commit & push...")
    result = git_push()
    print(f"  -> {result.get('status')}")

    print("\n" + "=" * 60)
    print(f"Done! {len(created)} posts created")
    print("=" * 60)

    return {"status": "success", "created": len(created), "git": result}


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get('status') == 'success' else 1)