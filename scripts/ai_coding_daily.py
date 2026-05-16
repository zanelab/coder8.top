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
HISTORY_FILE = Path(__file__).parent.parent / "scripts" / "published_history.json"
HISTORY_DAYS = 30  # Keep history for 30 days

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


# ========== Published History ==========

def load_published_history():
    """Load history of published articles"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}", file=sys.stderr)
    return {"articles": []}


def save_published_history(history):
    """Save history to file"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"History saved: {len(history['articles'])} articles")
    except Exception as e:
        print(f"Error saving history: {e}", file=sys.stderr)


def clean_old_history(history):
    """Remove articles older than HISTORY_DAYS"""
    cutoff = datetime.now() - timedelta(days=HISTORY_DAYS)
    history['articles'] = [
        a for a in history['articles']
        if datetime.fromisoformat(a.get('published_date', '2000-01-01')) > cutoff
    ]
    return history


def generate_article_id(article):
    """Generate unique ID for article based on title and URL"""
    # Use URL as primary identifier, fallback to title hash
    url = article.get('url', '')
    if url:
        # Normalize URL (remove trailing slashes, lowercase)
        url = url.rstrip('/').lower()
        return hashlib.md5(url.encode()).hexdigest()
    else:
        title = article.get('title', '')
        return hashlib.md5(title.encode()).hexdigest()


def is_article_published(article, history):
    """Check if article was already published"""
    article_id = generate_article_id(article)
    for published in history['articles']:
        if published.get('id') == article_id:
            return True
        # Also check title similarity (exact match)
        if published.get('title') == article.get('title'):
            return True
    return False


def mark_article_published(article, history):
    """Mark article as published in history"""
    history['articles'].append({
        'id': generate_article_id(article),
        'title': article.get('title', ''),
        'url': article.get('url', ''),
        'source': article.get('source', ''),
        'published_date': datetime.now().isoformat()
    })
    return history


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
            "sort_type": 200,  # 热门排序
            "cate_id": "6809637773935378440",  # 人工智能分类
            "cursor": "0",
            "limit": 20
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("err_no") == 0:
                for item in result.get("data", []):
                    article_info = item.get("article_info", {})
                    author_info = item.get("author_user_info", {})
                    title = article_info.get("title", "")
                    article_id = article_info.get("article_id", "")
                    
                    if matches_ai_keywords(title):
                        detail = fetch_juejin_article_detail(article_id)
                        content = detail.get("content", "") if detail else article_info.get("brief_content", "")
                        # Get author from list API (detail API often fails)
                        author = detail.get("author", "") if detail else author_info.get("user_name", "")
                        
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
    
    # Load published history
    print("\nLoading published history...")
    history = load_published_history()
    history = clean_old_history(history)
    print(f"  History contains {len(history['articles'])} recent articles")
    
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
        return {
            "status": "no_articles",
            "date": datetime.now().isoformat(),
            "statistics": {
                "hacker_news": {"collected": 0, "new": 0, "duplicates": 0},
                "github": {"collected": 0, "new": 0, "duplicates": 0},
                "juejin": {"collected": 0, "new": 0, "duplicates": 0},
                "total": {"collected": 0, "new": 0, "duplicates": 0, "published": 0}
            },
            "all_articles": [],
            "published_articles": []
        }
    
    # Filter out already published articles
    print("\nFiltering duplicates...")
    new_articles = []
    for article in all_articles:
        if is_article_published(article, history):
            print(f"  Skipping (already published): {article['title'][:50]}...")
        else:
            new_articles.append(article)
    
    print(f"  {len(new_articles)} new articles after filtering")
    
    if not new_articles:
        print("\nAll articles were already published. No new content today.")
        return {
            "status": "no_new_articles",
            "date": datetime.now().isoformat(),
            "statistics": {
                "hacker_news": {
                    "collected": len(hn_articles),
                    "new": 0,
                    "duplicates": len(hn_articles)
                },
                "github": {
                    "collected": len(gh_articles),
                    "new": 0,
                    "duplicates": len(gh_articles)
                },
                "juejin": {
                    "collected": len(jj_articles),
                    "new": 0,
                    "duplicates": len(jj_articles)
                },
                "total": {
                    "collected": len(all_articles),
                    "new": 0,
                    "duplicates": len(all_articles),
                    "published": 0
                }
            },
            "all_articles": [
                {
                    "title": a.get("title", ""),
                    "source": a.get("source", ""),
                    "url": a.get("url", ""),
                    "view_count": a.get("view_count", 0),
                    "like_count": a.get("like_count", 0),
                    "author": a.get("author", ""),
                    "is_duplicate": True
                }
                for a in all_articles
            ],
            "published_articles": []
        }
    
    # Sort by popularity (score/stars/views)
    new_articles.sort(
        key=lambda x: x.get('view_count', 0) + x.get('like_count', 0) * 2,
        reverse=True
    )
    top_articles = new_articles[:MAX_ARTICLES]
    
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
    
    # Mark articles as published in history
    print("\nUpdating published history...")
    for article in top_articles:
        history = mark_article_published(article, history)
    save_published_history(history)
    
    output = {
        "status": "success",
        "date": datetime.now().isoformat(),
        "statistics": {
            "hacker_news": {
                "collected": len(hn_articles),
                "new": len([a for a in hn_articles if not is_article_published(a, history)]),
                "duplicates": len([a for a in hn_articles if is_article_published(a, history)])
            },
            "github": {
                "collected": len(gh_articles),
                "new": len([a for a in gh_articles if not is_article_published(a, history)]),
                "duplicates": len([a for a in gh_articles if is_article_published(a, history)])
            },
            "juejin": {
                "collected": len(jj_articles),
                "new": len([a for a in jj_articles if not is_article_published(a, history)]),
                "duplicates": len([a for a in jj_articles if is_article_published(a, history)])
            },
            "total": {
                "collected": len(all_articles),
                "new": len(new_articles),
                "duplicates": len(all_articles) - len(new_articles),
                "published": len(top_articles)
            }
        },
        "all_articles": [
            {
                "title": a.get("title", ""),
                "source": a.get("source", ""),
                "url": a.get("url", ""),
                "view_count": a.get("view_count", 0),
                "like_count": a.get("like_count", 0),
                "author": a.get("author", ""),
                "is_duplicate": is_article_published(a, history)
            }
            for a in all_articles
        ],
        "published_articles": top_articles
    }
    
    print("\n" + json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    result = main()
    # Allow no_articles and no_new_articles as valid exits
    valid_statuses = ["success", "no_articles", "no_new_articles"]
    sys.exit(0 if result.get("status") in valid_statuses else 1)