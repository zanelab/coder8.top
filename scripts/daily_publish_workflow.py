#!/usr/bin/env python3
"""
Daily AI Coding Article Publishing Workflow
- Fetches top articles via ai_coding_daily.py
- Outputs raw articles for agent-level AI rewriting
- Generates Jekyll posts with AI-rewritten content
- Commits and pushes to GitHub
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
POSTS_DIR = WORKSPACE / "_posts"
POSTS_IMAGES_DIR = WORKSPACE / "assets" / "images" / "posts"
RAW_ARTICLES_FILE = WORKSPACE / "scripts" / "_raw_articles.json"

def fetch_articles():
    """Fetch articles via ai_coding_daily.py"""
    result = subprocess.run(
        [sys.executable, str(WORKSPACE / "scripts" / "ai_coding_daily.py")],
        capture_output=True, text=True, cwd=WORKSPACE
    )

    try:
        output = result.stdout
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(output[json_start:json_end]).get('articles', [])
    except (json.JSONDecodeError, ValueError):
        pass

    return []

def classify_article(title, content=''):
    """Classify as 'academic' or 'tutorial'"""
    text = f"{title} {content}".lower()

    tutorial_patterns = ['tutorial', 'guide', 'how to', 'step by step', '入门', '教程',
                         '实战', '手把手', '从零开始', 'beginner', 'build', 'create', '教学']
    academic_patterns = ['research', 'paper', 'study', 'analysis', 'survey', '论文',
                         '研究', '原理', '理论', '架构', '深入', '解读']

    tutorial_score = sum(1 for p in tutorial_patterns if p in text)
    academic_score = sum(1 for p in academic_patterns if p in text)

    return 'tutorial' if tutorial_score > academic_score else 'academic'

def generate_post_slug(title):
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')[:80].lower()

def download_cover_image(title):
    try:
        import hashlib
        seed = hashlib.md5(title.encode()).hexdigest()[:8]
        image_url = f"https://picsum.photos/seed/{seed}/800/400"
        POSTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{seed}.jpg"
        filepath = POSTS_IMAGES_DIR / filename

        import urllib.request, ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())

        return f"/assets/images/posts/{filename}"
    except Exception as e:
        print(f"  Cover image failed: {e}")
        return None

def git_commit_push(count):
    """Commit and push to GitHub"""
    try:
        subprocess.run(["git", "add", "."], cwd=WORKSPACE, check=True)
        msg = f"Daily: {count} AI coding articles translated - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], cwd=WORKSPACE, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE, check=True)
        return {"status": "success"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e)}

def main():
    print("=" * 60)
    print("Daily AI Coding Article Publishing Workflow")
    print("=" * 60)

    # Step 1: Fetch articles
    print("\n[1/4] Fetching top AI coding articles...")
    articles = fetch_articles()

    if not articles:
        print("No articles fetched.")
        return {"status": "no_articles"}

    # Save raw articles for agent to process
    with open(RAW_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "count": len(articles),
            "articles": articles
        }, f, ensure_ascii=False, indent=2)

    print(f"  Fetched {len(articles)} articles")
    print(f"  Saved to: {RAW_ARTICLES_FILE}")
    print("\n  Articles ready for AI rewriting:")
    for i, art in enumerate(articles, 1):
        style = classify_article(art.get('title', ''), art.get('content_preview', ''))
        print(f"  {i}. [{style}] {art.get('title', '')[:60]}...")

    # Step 2: Summary (rewrite happens via cron agent's model)
    print("\n[2/4] AI Rewriting (via Hermes Agent model)")
    print("  -> The cron job agent will use its own model to rewrite")
    print("  -> Articles saved to _raw_articles.json for rewriting")
    print("  -> Rewritten content will be committed in next step")

    # Step 3: Placeholder posts (actual rewriting done by agent)
    print("\n[3/4] Generating Jekyll posts (placeholder)")
    published = 0

    for art in articles:
        title = art.get('title', '')
        url = art.get('url', '')
        source = art.get('source', '')
        slug = generate_post_slug(title)
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
        filepath = POSTS_DIR / filename

        if filepath.exists():
            print(f"  Skip: {filename} (exists)")
            continue

        style = classify_article(title, art.get('content_preview', ''))

        frontmatter = f'''---
layout: post
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S +0800')}
categories: [AI Coding, Translation]
tags: [AI, Coding, Translation, {source}]
source_url: "{url}"
translation_style: {style}
---

# {title}

**Source:** [{url}]({url})
**Style:** {style} (AI rewriting pending)

<!--
AI rewriting prompt:
{"academic" if style == "academic" else "tutorial"}

Rewrite this article for an international English-speaking audience.
{"Academic: Be thorough, include background context, technical depth, comparisons." if style == "academic" else "Tutorial: Step-by-step, each step executable, include code examples, warnings, and practical tips."}

Original title: {title}
Original URL: {url}
Original content: {art.get('content_preview', '')[:500]}
-->

'''

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)

        print(f"  Created: {filename}")
        published += 1

        cover = download_cover_image(title)
        if cover:
            print(f"    Cover: {cover}")

    # Step 4: Git commit & push
    print("\n[4/4] Git commit & push")
    result = git_commit_push(published)

    print("\n" + "=" * 60)
    print(f"Summary: {published} posts created")
    print(f"Git: {result.get('status')}")
    print("=" * 60)

    return {
        "status": "success",
        "published": published,
        "articles_file": str(RAW_ARTICLES_FILE),
        "git": result
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get('status') == 'success' else 1)