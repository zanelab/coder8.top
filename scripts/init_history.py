#!/usr/bin/env python3
"""
Initialize published history from existing posts
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

POSTS_DIR = Path(__file__).parent.parent / "_posts"
HISTORY_FILE = Path(__file__).parent / "published_history.json"

def extract_frontmatter(filepath):
    """Extract title and source_url from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    frontmatter = {}
    in_fm = False
    
    for line in lines:
        if line.strip() == '---':
            if in_fm:
                break
            in_fm = True
            continue
        if in_fm and ':' in line:
            key, val = line.split(':', 1)
            frontmatter[key.strip()] = val.strip().strip('"').strip("'")
    
    return frontmatter

def generate_id(title):
    """Generate ID from title"""
    return hashlib.md5(title.encode()).hexdigest()

def main():
    history = {"articles": []}
    
    for md_file in POSTS_DIR.glob("*.md"):
        fm = extract_frontmatter(md_file)
        title = fm.get('title', '')
        date_str = md_file.name[:10]  # Extract date from filename
        
        if title:
            history["articles"].append({
                "id": generate_id(title),
                "title": title,
                "url": fm.get('source_url', ''),
                "source": "imported",
                "published_date": f"{date_str}T08:00:00"
            })
            print(f"Added: {title[:50]}...")
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {len(history['articles'])} articles imported to history")

if __name__ == "__main__":
    main()