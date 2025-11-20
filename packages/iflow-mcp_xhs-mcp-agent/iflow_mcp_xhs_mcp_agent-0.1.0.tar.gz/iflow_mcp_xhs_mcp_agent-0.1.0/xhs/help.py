import hashlib
import json
import os
import random
import re
import string
import time
from typing import Dict, List, Optional, Union

import requests
from lxml import etree


def sign(url: str, data: Optional[Dict] = None, a1: Optional[str] = None) -> Dict[str, str]:
    """Generate signature for XHS API requests
    
    This is a simplified implementation. In a real-world scenario, you would need
    to implement the actual signing algorithm used by Xiaohongshu.
    """
    timestamp = str(int(time.time()))
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    # This is a placeholder. The actual signing algorithm would be more complex
    signature = hashlib.md5((url + (json.dumps(data) if data else "") + timestamp + nonce).encode()).hexdigest()
    
    return {
        "x-s": signature,
        "x-t": timestamp,
        "x-s-common": nonce
    }


def cookie_jar_to_cookie_str(cookie_jar) -> str:
    """Convert cookie jar to cookie string"""
    return '; '.join([f"{k}={v}" for k, v in requests.utils.dict_from_cookiejar(cookie_jar).items()])


def update_session_cookies_from_cookie(session: requests.Session, cookie: Optional[str]) -> None:
    """Update session cookies from cookie string"""
    if not cookie:
        return
    
    for item in cookie.split(';'):
        item = item.strip()
        if not item:
            continue
        
        if '=' not in item:
            continue
            
        name, value = item.split('=', 1)
        session.cookies.set(name, value)


def get_imgs_url_from_note(note: Dict) -> List[str]:
    """Extract image URLs from note"""
    if note.get("type") != "normal":
        return []
    
    image_list = note.get("image_list", [])
    return [img.get("url", "") for img in image_list if img.get("url")]


def get_video_url_from_note(note: Dict) -> str:
    """Extract video URL from note"""
    if note.get("type") != "video":
        return ""
    
    video = note.get("video", {})
    return video.get("url", "")


def get_valid_path_name(name: str) -> str:
    """Convert string to valid path name"""
    if not name:
        return ""
    
    # Replace invalid characters with underscore
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def get_search_id() -> str:
    """Generate search ID"""
    return str(int(time.time() * 1000))


def download_file(url: str, file_path: str) -> None:
    """Download file from URL to local path"""
    if not url:
        return
    
    response = requests.get(url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def parse_xml(xml_str: str) -> Dict:
    """Parse XML string to dictionary"""
    root = etree.fromstring(xml_str)
    result = {}
    
    for child in root:
        result[child.tag] = child.text
    
    return result
