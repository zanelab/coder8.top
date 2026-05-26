#!/usr/bin/env python3
"""
Daily AI Coding Article Publishing Workflow
- Fetches top articles via ai_coding_daily.py
- AI rewrites (academic: detailed, tutorial: step-by-step)
- Generates Jekyll posts
- Commits and pushes to GitHub
"""

import os
import sys
import json
import re
import subprocess
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.parse
import ssl

# ========== Config ==========
WORKSPACE = Path(__file__).parent.parent  # /opt/data/workspace/coder8.top
POSTS_DIR = WORKSPACE / "_posts"
POSTS_IMAGES_DIR = WORKSPACE / "assets" / "images" / "posts"
HISTORY_FILE = WORKSPACE / "scripts" / "published_history.json"

GITHUB_REPO = "git@github.com:zanelab/coder8.top.git"
GITHUB_BRANCH = "main"

# AI rewriting prompt templates
ACADEMIC_PROMPT = """You are an expert technical writer specializing in academic and in-depth analysis.
Rewrite the following article for an international English-speaking audience.
Requirements:
1. Academic tone, thorough and detailed explanations
2. Include background context, related work, and deeper technical insights
3. Preserve all key technical details, data points, and citations
4. Format with proper headings, and where relevant include comparison tables
5. Output ONLY the rewritten article in Markdown format - no commentary, no meta-discussion

Article Title: {title}
Article URL: {url}
Article Content Preview: {content}

BEGIN ARTICLE:"""

TUTORIAL_PROMPT = """You are an expert technical educator specializing in hands-on learning.
Rewrite the following article as a step-by-step tutorial for an international English-speaking audience.
Requirements:
1. Tutorial style - each step clearly numbered and executable
2. Include prerequisite sections, expected outcomes, and common pitfalls/warnings
3. Code examples should be complete and runnable
4. Use "Try it yourself" and "Note" callout boxes where appropriate
5. Output ONLY the rewritten tutorial in Markdown format - no commentary, no meta-discussion

Article Title: {title}
Article URL: {url}
Article Content Preview: {content}

BEGIN TUTORIAL:"""

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# ========== AI Rewriting (via OpenRouter API) ==========

def rewrite_with_ai(title, url, content, style='academic'):
    """Use AI to rewrite article. Returns rewritten markdown."""
    
    prompt_template = ACADEMIC_PROMPT if style == 'academic' else TUTORIAL_PROMPT
    prompt = prompt_template.format(title=title, url=url, content=content[:2000])
    
    # Try OpenRouter API (supports many LLMs)
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if not api_key:
        # Try other common env vars
        api_key = os.environ.get('OPENAI_API_KEY', '') or os.environ.get('ANTHROPIC_API_KEY', '')
    
    if api_key:
        return call_llm_api(prompt, api_key, title)
    
    print(f"  [WARN] No AI API key found, using placeholder content")
    return f"# {title}\n\n**Source:** [{url}]({url})\n\n*This article was originally published in Chinese and has been queued for AI rewriting.*\n\n---\n\n{content[:1000]}..."

def call_llm_api(prompt, api_key, title):
    """Call LLM API (OpenRouter/OpenAI compatible)"""
    
    # Try OpenRouter first (cheaper, more models)
    openrouter_models = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku",
        "google/gemini-flash",
    ]
    
    for model in openrouter_models:
        try:
            result = call_openrouter(prompt, api_key, model)
            if result:
                return result
        except Exception as e:
            print(f"  OpenRouter {model} failed: {e}")
            continue
    
    # Fallback: try direct OpenAI
    try:
        result = call_openai(prompt, api_key)
        if result:
            return result
    except Exception as e:
        print(f"  OpenAI API failed: {e}")
    
    return None

def call_openrouter(prompt, api_key, model):
    """Call OpenRouter API"""
    import urllib.request
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://coder8.top",
        "X-Title": "AI Coding Daily",
    }
    
    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0.7,
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120, context=ssl_context) as resp:
        result = json.loads(resp.read().decode())
        return result['choices'][0]['message']['content']

def call_openai(prompt, api_key):
    """Call OpenAI API directly"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0.7,
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120, context=ssl_context) as resp:
        result = json.loads(resp.read().decode())
        return result['choices'][0]['message']['content']

# ========== Article Classification ==========

def classify_article(title, content=''):
    """Classify article as 'academic' or 'tutorial' based on title/content patterns."""
    text = f"{title} {content}".lower()
    
    tutorial_patterns = [
        'tutorial', 'guide', 'how to', 'step by step', '入门', '教程',
        '实战', '手把手', '从零开始', 'beginner', 'learning',
        '教学', '练习', '实践', '实现', 'build', 'create',
    ]
    
    academic_patterns = [
        'research', 'paper', 'study', 'analysis', 'survey',
        '论文', '研究', '分析', '原理', '理论', '学术',
        'comparison', 'evaluation', 'benchmark', '评测',
        '架构', '设计模式', '深入', '解读',
    ]
    
    tutorial_score = sum(1 for p in tutorial_patterns if p in text)
    academic_score = sum(1 for p in academic_patterns if p in text)
    
    if tutorial_score > academic_score:
        return 'tutorial'
    return 'academic'

# ========== Jekyll Post Generation ==========

def generate_post_slug(title):
    """Generate URL-safe slug from title"""
    # Remove special chars, keep Chinese and English
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')[:80]
    return slug.lower()

def generate_frontmatter(title, source, url, date=None):
    """Generate Jekyll frontmatter"""
    if date is None:
        date = datetime.now()
    
    slug = generate_post_slug(title)
    date_str = date.strftime('%Y-%m-%d')
    datetime_str = date.strftime('%Y-%m-%d %H:%M:%S +0800')
    
    return f'''---
layout: post
title: "{title}"
date: {datetime_str}
categories: [AI Coding, Translation]
tags: [AI, Coding, Translation, {source}]
permalink: /:year/:month/:day/{slug}.html
source_url: "{url}"
---

'''

def download_cover_image(title, post_slug):
    """Download a cover image for the post"""
    try:
        import hashlib
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        seed = hashlib.md5(title.encode()).hexdigest()[:8]
        
        image_url = f"https://picsum.photos/seed/{seed}/800/400"
        
        POSTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{timestamp}-{seed}.jpg"
        filepath = POSTS_IMAGES_DIR / filename
        
        req = urllib.request.Request(image_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        
        return f"/assets/images/posts/{filename}"
    except Exception as e:
        print(f"  Cover image download failed: {e}")
        return None

# ========== Git Operations ==========

def git_commit_push(message="Daily AI Coding Articles Update"):
    """Commit and push changes to GitHub"""
    try:
        os.chdir(WORKSPACE)
        
        # Check git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=WORKSPACE
        )
        
        if not result.stdout.strip():
            print("No changes to commit.")
            return {"status": "no_changes"}
        
        # Add all changes
        subprocess.run(["git", "add", "."], cwd=WORKSPACE, check=True)
        
        # Commit with timestamp
        commit_msg = f"{message} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=WORKSPACE, check=True
        )
        
        # Push
        subprocess.run(
            ["git", "push", GITHUB_REPO, GITHUB_BRANCH],
            cwd=WORKSPACE, check=True
        )
        
        print(f"Successfully pushed to GitHub")
        return {"status": "success", "message": commit_msg}
        
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        return {"status": "error", "error": str(e)}

# ========== Main Workflow ==========

def main():
    print("=" * 60)
    print("Daily AI Coding Article Publishing Workflow")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Fetch articles via ai_coding_daily.py
    print("[1/5] Fetching top AI coding articles...")
    result = subprocess.run(
        [sys.executable, str(WORKSPACE / "scripts" / "ai_coding_daily.py")],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    
    if result.returncode not in [0, 1]:  # 0=success, 1=no_new_articles
        print(f"Fetch failed: {result.stderr}")
        return {"status": "error", "step": "fetch", "error": result.stderr}
    
    # Parse the JSON output from ai_coding_daily.py
    try:
        # Extract JSON from output
        output = result.stdout
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            fetch_result = json.loads(output[json_start:json_end])
        else:
            fetch_result = {"articles": []}
    except json.JSONDecodeError:
        fetch_result = {"articles": []}
    
    articles = fetch_result.get('articles', [])
    if not articles:
        print("No articles to publish.")
        return {"status": "no_articles"}
    
    print(f"  -> Fetched {len(articles)} articles\n")
    
    # Step 2: AI Rewrite each article
    print("[2/5] AI rewriting articles...")
    rewritten = []
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', '')
        url = article.get('url', '')
        content = article.get('content_preview', '')
        source = article.get('source', '')
        
        style = classify_article(title, content)
        print(f"\n  Article {i}/{len(articles)}: [{style}] {title[:50]}...")
        
        rewritten_md = rewrite_with_ai(title, url, content, style=style)
        
        if rewritten_md:
            print(f"  -> Rewrite complete ({len(rewritten_md)} chars)")
        else:
            print(f"  -> Rewrite skipped (no API key)")
            rewritten_md = f"# {title}\n\n**Source:** [{url}]({url})\n\n<!-- AI rewriting pending -->"
        
        rewritten.append({
            'title': title,
            'url': url,
            'source': source,
            'style': style,
            'markdown': rewritten_md,
        })
    
    # Step 3: Generate Jekyll posts
    print("\n[3/5] Generating Jekyll posts...")
    
    published = []
    for art in rewritten:
        slug = generate_post_slug(art['title'])
        date = datetime.now()
        filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
        filepath = POSTS_DIR / filename
        
        # Check if already exists
        if filepath.exists():
            print(f"  Skipping (already exists): {filename}")
            continue
        
        # Generate frontmatter + content
        frontmatter = generate_frontmatter(art['title'], art['source'], art['url'], date)
        full_content = frontmatter + art['markdown']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"  Created: {filename}")
        published.append(filename)
        
        # Download cover image
        cover = download_cover_image(art['title'], slug)
        if cover:
            print(f"  Cover: {cover}")
    
    if not published:
        print("  No new posts to publish.")
    
    # Step 4: Commit and push
    print("\n[4/5] Committing to Git...")
    commit_result = git_commit_push(f"Daily: {len(published)} AI coding articles")
    
    # Step 5: Summary
    print("\n[5/5] Summary")
    print("=" * 60)
    print(f"Published: {len(published)} posts")
    for p in published:
        print(f"  - {p}")
    print(f"Git push: {commit_result.get('status', 'unknown')}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "status": "success",
        "published": published,
        "git": commit_result,
    }


if __name__ == "__main__":
    result = main()
    
    # Exit with appropriate code
    if result.get('status') == 'success':
        sys.exit(0)
    elif result.get('status') == 'no_articles':
        sys.exit(0)
    else:
        sys.exit(1)