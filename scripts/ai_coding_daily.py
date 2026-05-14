#!/usr/bin/env python3
"""
AI Coding Daily Article Collector
- Fetches hot articles from Juejin and Zhihu about AI coding
- Translates to English
- Generates Jekyll posts
- Commits and pushes to GitHub
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error
import ssl
import re

# Configuration
POSTS_DIR = Path(__file__).parent.parent / "_posts"
MAX_ARTICLES = 2  # Max articles per day
KEYWORDS = ["ai coding", "copilot", "cursor", "ai programming", "llm coding", "code generation", "ai assistant", "claude code", "ai 开发", "ai 编程", "ai 代码", "copilot", "cursor"]

# SSL context for HTTPS requests
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Images directory
IMAGES_DIR = Path(__file__).parent.parent / "assets" / "images" / "posts"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def fetch_image_from_unsplash(query):
    """Fetch a free image from Unsplash based on query"""
    # Unsplash source API (no auth needed for source images)
    # Format: https://source.unsplash.com/featured/?{query}
    
    keywords = ["ai", "coding", "programming", "technology", "developer", "computer"]
    search_query = query.lower() if query else "ai coding"
    
    # Use Unsplash source for random relevant image
    image_url = f"https://source.unsplash.com/800x400/?{search_query},{','.join(keywords[:3])}"
    
    try:
        req = urllib.request.Request(image_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            hash_part = hashlib.md5(search_query.encode()).hexdigest()[:6]
            filename = f"{timestamp}-{hash_part}.jpg"
            filepath = IMAGES_DIR / filename
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.read())
            
            print(f"Downloaded image: {filename}")
            return f"/assets/images/posts/{filename}"
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        return None


def fetch_juejin_article_detail(article_id):
    """Fetch full article content from Juejin"""
    url = "https://api.juejin.cn/content_api/v1/article/detail"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        data = json.dumps({"article_id": article_id}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("err_no") == 0:
                article_info = result.get("data", {}).get("article_info", {})
                return {
                    "title": article_info.get("title", ""),
                    "content": article_info.get("mark_content", "") or article_info.get("brief_content", ""),
                    "author": result.get("data", {}).get("author_user_info", {}).get("user_name", ""),
                }
    except Exception as e:
        print(f"Error fetching article detail: {e}", file=sys.stderr)
    return None


def fetch_juejin_articles():
    """Fetch hot articles from Juejin API"""
    articles = []
    
    # Juejin recommend API
    url = "https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        data = json.dumps({
            "id_type": 2,
            "sort_type": 200,  # Hot sort
            "cate_id": "6809637767543259144",  # AI category
            "cursor": "0",
            "limit": 20
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("err_no") == 0:
                for item in result.get("data", []):
                    article_info = item.get("article_info", {})
                    title = article_info.get("title", "")
                    article_id = article_info.get("article_id", "")
                    
                    # Check if related to AI coding
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in ["copilot", "cursor", "ai", "gpt", "llm", "claude", "ai编程", "ai开发", "代码生成"]):
                        # Fetch full article content
                        detail = fetch_juejin_article_detail(article_id)
                        if detail:
                            articles.append({
                                "title": detail.get("title", title),
                                "url": f"https://juejin.cn/post/{article_id}",
                                "content": detail.get("content", ""),
                                "source": "juejin",
                                "author": detail.get("author", ""),
                                "view_count": article_info.get("view_count", 0),
                                "like_count": article_info.get("digg_count", 0)
                            })
    except Exception as e:
        print(f"Error fetching from Juejin: {e}", file=sys.stderr)
    
    return articles


def fetch_zhihu_articles():
    """Fetch hot questions/articles from Zhihu"""
    articles = []
    
    # Zhihu hot questions API
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            for item in result.get("data", []):
                target = item.get("target", {})
                title = target.get("title", "")
                excerpt = target.get("excerpt", "")
                
                # Check if related to AI coding
                title_lower = title.lower()
                excerpt_lower = excerpt.lower()
                combined = title_lower + " " + excerpt_lower
                
                if any(kw in combined for kw in ["copilot", "cursor", "ai编程", "ai开发", "ai代码", "ai 写代码", "gpt", "llm", "claude"]):
                    articles.append({
                        "title": title,
                        "url": target.get("url", ""),
                        "content": excerpt,
                        "source": "zhihu",
                        "author": target.get("author", {}).get("name", ""),
                        "hot_score": item.get("detail_text", "")
                    })
    except Exception as e:
        print(f"Error fetching from Zhihu: {e}", file=sys.stderr)
    
    return articles


def translate_to_english(title, content):
    """Translate Chinese to English using LLM API"""
    # This will be handled by the calling script via Hermes
    # For now, return a placeholder that indicates translation needed
    return title, content


def generate_jekyll_post(article, translated_title, translated_content):
    """Generate a Jekyll post markdown file"""
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    datetime_str = today.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create filename from title
    slug = re.sub(r'[^\w\s-]', '', translated_title.lower())
    slug = re.sub(r'[\s]+', '-', slug)[:80]
    filename = f"{date_str}-{slug}.md"
    
    # Generate unique hash to avoid duplicates
    content_hash = hashlib.md5(article['title'].encode()).hexdigest()[:8]
    if len(slug) < 10:
        slug = f"{slug}-{content_hash}"
        filename = f"{date_str}-{slug}.md"
    
    frontmatter = f"""---
title: "{translated_title}"
date: {datetime_str}
categories: [AI Coding]
tags: [AI, Coding, Productivity]
---

"""
    
    return filename, frontmatter + translated_content


def main():
    print("Starting AI Coding Daily Article Collection...")
    print(f"Posts directory: {POSTS_DIR}")
    
    # Ensure posts directory exists
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch articles
    all_articles = []
    
    print("Fetching from Juejin...")
    juejin_articles = fetch_juejin_articles()
    print(f"  Found {len(juejin_articles)} articles")
    all_articles.extend(juejin_articles)
    
    print("Fetching from Zhihu...")
    zhihu_articles = fetch_zhihu_articles()
    print(f"  Found {len(zhihu_articles)} articles")
    all_articles.extend(zhihu_articles)
    
    if not all_articles:
        print("No relevant articles found today.")
        return {"status": "no_articles", "count": 0}
    
    # Sort by popularity and take top articles
    all_articles.sort(key=lambda x: x.get('view_count', 0) + x.get('like_count', 0) * 10, reverse=True)
    top_articles = all_articles[:MAX_ARTICLES]
    
    # Fetch cover images for each article
    print("\nFetching cover images...")
    for article in top_articles:
        # Extract key topic from title for image search
        title_words = article['title'].replace("AI", "").replace("写", "").replace("代码", "").replace("编程", "")
        keywords = title_words[:30] if len(title_words) > 30 else title_words
        image_path = fetch_image_from_unsplash(keywords)
        article['cover_image'] = image_path
    
    print(f"\nTop {len(top_articles)} articles selected:")
    for i, a in enumerate(top_articles, 1):
        print(f"  {i}. [{a['source']}] {a['title'][:50]}...")
    
    # Output for processing by Hermes
    output = {
        "status": "success",
        "count": len(top_articles),
        "articles": top_articles,
        "date": datetime.now().isoformat()
    }
    
    print("\n" + json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get("status") in ["success", "no_articles"] else 1)