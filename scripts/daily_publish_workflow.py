#!/usr/bin/env python3
"""
Daily AI Coding Article Publishing Workflow
- Fetches top articles directly from sources
- AI rewrites via Hermes Agent model (embedded prompt)
- Generates Jekyll posts
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
HISTORY_FILE = WORKSPACE / "scripts" / "published_history.json"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ========== Direct Fetcher (bypasses published history) ==========

def fetch_juejin():
    """Fetch from Juejin directly"""
    articles = []
    url = "https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"
    headers = {"Content-Type": "application/json"}

    try:
        data = json.dumps({
            "id_type": 2,
            "sort_type": 200,
            "cate_id": "6809637773935378440",
            "cursor": "0",
            "limit": 20
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        if result.get("err_no") == 0:
            for item in result.get("data", [])[:10]:
                art = item.get("article_info", {})
                articles.append({
                    "title": art.get("title", ""),
                    "url": f"https://juejin.cn/post/{art.get('article_id', '')}",
                    "content_preview": art.get("brief_content", "")[:300],
                    "source": "juejin",
                    "author": item.get("author_user_info", {}).get("user_name", ""),
                    "view_count": art.get('view_count', 0),
                    "like_count": art.get('digg_count', 0),
                })
    except Exception as e:
        print(f"Juejin error: {e}")

    return articles

def fetch_hackernews():
    """Fetch from HN Algolia"""
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
    """Fetch from GitHub"""
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

# ========== AI Rewrite (write directly to file) ==========

def rewrite_article(article, index, total):
    """Generate AI rewrite prompt for this article, output as Jekyll post"""
    title = article['title']
    url = article['url']
    content = article.get('content_preview', '')
    source = article['source']
    style = classify_article(title, content)
    author = article.get('author', 'Unknown')

    slug = generate_slug(title)
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
    filepath = POSTS_DIR / filename

    # Determine translation style message
    style_msg = {
        'academic': 'This is an academic/article piece. Rewrite with thorough depth, technical background, comparisons, and detailed analysis. Include relevant context and make it comprehensive for an international audience.',
        'tutorial': 'This is a tutorial/guide piece. Rewrite as a step-by-step hands-on guide with code examples, prerequisites, common pitfalls to avoid, and practical tips. Make each step clear and executable.'
    }[style]

    # Build the Jekyll post content with embedded rewrite instruction
    cover = download_cover(title)
    cover_line = f"\ncover_image: {cover}\n" if cover else ""

    jekyll_post = f'''---
layout: post
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S +0800')}
categories: [AI Coding, Translation]
tags: [AI, Coding, Translation, {source}]
source_url: "{url}"
author: "{author}"
translation_style: {style}
translation_status: pending
{cover_line}---

# {title}

**Source:** [{url}]({url})  
**Author:** {author}  
**Style:** {style}  
**Views:** {article.get('view_count', 0):,} | **Likes:** {article.get('like_count', 0):,}

---

## AI Rewrite Required

This article needs to be rewritten in English for an international audience.

**Translation Style:** {style_msg}

**Original Title:** {title}  
**Original URL:** {url}

**Original Content Preview:**
{content}

**Instructions:**
- Rewrite the full article in English
- Maintain all key technical information and data points
- Use proper Markdown formatting with headings, code blocks, and lists
- For tutorials: include step-by-step instructions with code examples
- For academic: include background context and deeper analysis

<!-- 
BEGIN REWRITE - Replace everything below this comment with your English rewrite.
Keep the frontmatter above unchanged.
-->

[AI rewrite pending - please rewrite the content above in English with proper Markdown formatting. Make it comprehensive and well-structured. Remove this comment when complete.]

'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(jekyll_post)

    print(f"  [{index}/{total}] Created: {filename} ({style})")
    return filename

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

    # Step 1: Fetch from multiple sources
    print("\n[1/4] Fetching articles from sources...")

    all_articles = []

    # Fetch from Juejin
    print("  Fetching Juejin...")
    jj = fetch_juejin()
    print(f"    -> {len(jj)} articles")
    all_articles.extend(jj)

    # Fetch from HN
    print("  Fetching Hacker News...")
    hn = fetch_hackernews()
    print(f"    -> {len(hn)} articles")
    all_articles.extend(hn)

    # Fetch from GitHub
    print("  Fetching GitHub...")
    gh = fetch_github_trending()
    print(f"    -> {len(gh)} articles")
    all_articles.extend(gh)

    print(f"\n  Total fetched: {len(all_articles)}")

    if not all_articles:
        print("No articles fetched.")
        return {"status": "no_articles"}

    # Step 2: Score and rank
    print("\n[2/4] Scoring and filtering...")

    scored = []
    for art in all_articles:
        score = score_article(art['title'], art.get('content_preview', ''))
        if score >= 1:  # At least one AI coding keyword
            scored.append((score, art))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top 3
    top = [art for score, art in scored[:3]]

    print(f"  Top 3 after filtering:")
    for i, art in enumerate(top, 1):
        print(f"    {i}. [{art['source']}] {art['title'][:55]}...")

    if not top:
        print("No relevant articles found.")
        return {"status": "no_relevant"}

    # Step 3: Generate Jekyll posts with rewrite placeholder
    print("\n[3/4] Generating Jekyll posts...")
    published = []

    for i, art in enumerate(top, 1):
        fname = rewrite_article(art, i, len(top))
        published.append(fname)

    # Step 4: Git commit & push
    print("\n[4/4] Git commit & push...")
    result = git_push()

    print("\n" + "=" * 60)
    print(f"Done! {len(published)} posts created")
    print(f"Git: {result.get('status')}")
    print("=" * 60)

    # Print rewrite instructions
    print("\n[REWRITE INSTRUCTIONS FOR AGENT]")
    print("=" * 60)
    for i, art in enumerate(published, 1):
        style = classify_article(art['title'], art.get('content_preview', ''))
        print(f"\n{i}. {art['title']}")
        print(f"   File: {POSTS_DIR / published[i-1]}")
        print(f"   Style: {style}")
        print(f"   URL: {art['url']}")

    return {
        "status": "success",
        "published": published,
        "articles": top,
        "git": result
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get('status') == 'success' else 1)