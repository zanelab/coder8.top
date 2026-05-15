#!/usr/bin/env python3
"""
AI Coding Daily Article Collector
- Fetches hot articles from Juejin, Hacker News, GitHub Trending about AI coding
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
import urllib.parse
import ssl
import re

# Configuration
POSTS_DIR = Path(__file__).parent.parent / "_posts"
MAX_ARTICLES = 3  # Max articles per day
MAX_PER_SOURCE = 5  # Max articles per source

# Keywords for AI coding topics
AI_KEYWORDS = [
    "copilot", "cursor", "claude", "gpt", "llm", "ai", "chatgpt",
    "deepseek", "agent", "prompt", "code generation", "ai coding",
    "ai programming", "machine learning", "neural network",
    "ai编程", "ai开发", "代码生成", "智能", "写代码", "编程助手"
]

# SSL context for HTTPS requests
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Images directory
IMAGES_DIR = Path(__file__).parent.parent / "assets" / "images" / "posts"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Covers directory (local custom cover images)
COVERS_DIR = Path(__file__).parent.parent / "assets" / "images" / "covers"

# Keyword mapping for local covers (keyword -> list of matching file patterns)
COVER_KEYWORDS = {
    "claude": ["claude", "cluade"],
    "cursor": ["claude", "cluade", "cursor"],
    "copilot": ["claude", "cluade", "copilot"],
    "gpt": ["claude", "cluade"],
    "llm": ["claude", "cluade"],
    "ai": ["claude", "cluade"],
    "n8n": ["n8n"],
    "workflow": ["n8n"],
    "automation": ["n8n"],
    "openclaw": ["openclaw"],
    "opencode": ["openclaw"],
    "agent": ["openclaw"],
    "assistant": ["openclaw"],
    "autogpt": ["openclaw"],
}


def find_local_cover(keyword):
    """Find a matching cover image from local covers directory"""
    import random
    
    keyword_lower = keyword.lower()
    
    # Try to find matching cover by keyword
    matching_files = []
    
    if COVERS_DIR.exists():
        for file in COVERS_DIR.glob("*.jpg"):
            file_name = file.name.lower()
            
            # Check if file name matches keyword via mapping
            for key, patterns in COVER_KEYWORDS.items():
                if key in keyword_lower:
                    for pattern in patterns:
                        if pattern in file_name:
                            matching_files.append(file)
                            break
        
        # If no match via mapping, try direct filename match
        if not matching_files:
            for file in COVERS_DIR.glob("*.jpg"):
                file_name = file.name.lower()
                # Extract base name (without extension and number suffix)
                base_name = file_name.replace("-1.jpg", "").replace("-2.jpg", "").replace(".jpg", "")
                if base_name in keyword_lower or keyword_lower in base_name:
                    matching_files.append(file)
    
    if matching_files:
        # Randomly select one from matching files
        selected = random.choice(matching_files)
        print(f"Found local cover: {selected.name} (keyword: {keyword})")
        return f"/assets/images/covers/{selected.name}"
    
    return None


def fetch_image(query="ai coding technology"):
    """Fetch a cover image - first try local covers, then download from picsum.photos"""
    
    # First try to find a matching local cover
    local_cover = find_local_cover(query)
    if local_cover:
        return local_cover
    
    # No local cover found, download from picsum.photos
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        seed = hashlib.md5(query.encode()).hexdigest()[:8]
        image_url = f"https://picsum.photos/seed/{seed}/800/400"
        
        req = urllib.request.Request(image_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            filename = f"{timestamp}-{seed}.jpg"
            filepath = IMAGES_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.read())
            
            print(f"Downloaded image: {filename} (keyword: {query})")
            return f"/assets/images/posts/{filename}"
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        return None


def matches_ai_keywords(text):
    """Check if text matches AI coding keywords"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in AI_KEYWORDS)


# ========== Hacker News ==========

def fetch_hacker_news_articles():
    """Fetch top stories from Hacker News related to AI coding"""
    articles = []
    
    try:
        # Use HN Algolia API (much faster than Firebase API)
        # Search for AI-related stories directly
        url = "https://hn.algolia.com/api/v1/search?query=ai+OR+llm+OR+gpt+OR+claude+OR+copilot&tags=story&hitsPerPage=10"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        
        with urllib.request.urlopen(req, timeout=20, context=ssl_context) as resp:
            data = json.loads(resp.read().decode())
        
        hits = data.get("hits", [])
        print(f"  Got {len(hits)} AI-related stories from Algolia")
        
        for hit in hits[:5]:
            title = hit.get("title", "")
            url_link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            
            articles.append({
                "title": title,
                "url": url_link,
                "content": f"Hacker News story with {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
                "source": "hacker_news",
                "author": hit.get("author", ""),
                "view_count": hit.get("points", 0),
                "like_count": hit.get("points", 0)
            })
            print(f"    Found: {title[:50]}...")
        
        print(f"  Found {len(articles)} AI-related articles")
        
    except Exception as e:
        print(f"Error fetching from Hacker News: {e}", file=sys.stderr)
    
    return articles


# ========== GitHub Trending ==========

def fetch_github_trending():
    """Fetch trending AI coding repositories from GitHub"""
    articles = []
    
    try:
        # Simplified search query for AI repos
        query = urllib.parse.quote("ai OR llm OR gpt OR claude OR copilot OR cursor")
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=15"
        
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.github.v3+json"
        })
        
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            data = json.loads(resp.read().decode())
        
        print(f"  Got {data.get('total_count', 0)} total repos")
        
        for repo in data.get("items", [])[:MAX_PER_SOURCE]:
            name = repo.get("full_name", "")
            desc = repo.get("description", "") or ""
            
            articles.append({
                "title": f"{name}: {desc[:80]}",
                "url": repo.get("html_url", ""),
                "content": f"GitHub repository with {repo.get('stargazers_count', 0)} stars. {desc}",
                "source": "github",
                "author": repo.get("owner", {}).get("login", ""),
                "view_count": repo.get("stargazers_count", 0),
                "like_count": repo.get("stargazers_count", 0)
            })
            print(f"    Found: {name} ({repo.get('stargazers_count', 0)} stars)")
        
        print(f"  Found {len(articles)} AI repos")
        
    except Exception as e:
        print(f"Error fetching from GitHub: {e}", file=sys.stderr)
    
    return articles


# ========== Juejin ==========

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
    
    url = "https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        data = json.dumps({
            "id_type": 2,
            "sort_type": 200,
            "cate_id": "6809637767543259144",
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
                    
                    if matches_ai_keywords(title):
                        detail = fetch_juejin_article_detail(article_id)
                        content = detail.get("content", "") if detail else article_info.get("brief_content", "")
                        author = detail.get("author", "") if detail else article_info.get("author_user_info", {}).get("user_name", "")
                        
                        articles.append({
                            "title": detail.get("title", title) if detail else title,
                            "url": f"https://juejin.cn/post/{article_id}",
                            "content": content,
                            "source": "juejin",
                            "author": author,
                            "view_count": article_info.get("view_count", 0),
                            "like_count": article_info.get("digg_count", 0)
                        })
                        print(f"    Found: {title[:50]}...")
                        
                        if len(articles) >= MAX_PER_SOURCE:
                            break
        
        print(f"  Found {len(articles)} AI-related articles")
        
    except Exception as e:
        print(f"Error fetching from Juejin: {e}", file=sys.stderr)
    
    return articles


# ========== Main ==========

def main():
    print("Starting AI Coding Daily Article Collection...")
    print(f"Posts directory: {POSTS_DIR}")
    
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    
    all_articles = []
    
    # Fetch from Hacker News
    print("\nFetching from Hacker News...")
    hn_articles = fetch_hacker_news_articles()
    all_articles.extend(hn_articles)
    
    # Fetch from GitHub Trending
    print("\nFetching from GitHub Trending...")
    gh_articles = fetch_github_trending()
    all_articles.extend(gh_articles)
    
    # Fetch from Juejin
    print("\nFetching from Juejin...")
    jj_articles = fetch_juejin_articles()
    all_articles.extend(jj_articles)
    
    if not all_articles:
        print("\nNo relevant articles found today.")
        return {"status": "no_articles", "count": 0, "sources_checked": 3}
    
    # Sort by popularity (score/stars/views)
    all_articles.sort(
        key=lambda x: x.get('view_count', 0) + x.get('like_count', 0) * 2,
        reverse=True
    )
    top_articles = all_articles[:MAX_ARTICLES]
    
    # Fetch cover images (use article title as keyword for unique images)
    print("\nFetching cover images...")
    for article in top_articles:
        # Use article title as image keyword for unique covers
        image_keyword = article.get('title', 'ai coding technology')
        # Clean up title for better image search (remove URLs, special chars)
        image_keyword = re.sub(r'https?://\S+', '', image_keyword)  # Remove URLs
        image_keyword = re.sub(r'[^\w\s]', ' ', image_keyword)  # Remove special chars
        image_keyword = ' '.join(image_keyword.split()[:5])  # Use first 5 words
        image_path = fetch_image(image_keyword)
        article['cover_image'] = image_path
    
    print(f"\nTop {len(top_articles)} articles selected:")
    for i, a in enumerate(top_articles, 1):
        print(f"  {i}. [{a['source']}] {a['title'][:60]}...")
    
    output = {
        "status": "success",
        "count": len(top_articles),
        "total_found": len(all_articles),
        "articles": top_articles,
        "date": datetime.now().isoformat()
    }
    
    print("\n" + json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get("status") in ["success", "no_articles"] else 1)