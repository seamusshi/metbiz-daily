#!/usr/bin/env python3
"""快速测试搜索和链接解码"""

import urllib.request
import urllib.parse
import re

def decode_duckduckgo_url(url):
    """解码 DuckDuckGo 重定向 URL"""
    if url.startswith('//'):
        url = 'https:' + url
    
    if 'duckduckgo.com/l/' in url or 'duckduckgo.com/l?' in url:
        try:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            
            if 'uddg' in params:
                real_url = urllib.parse.unquote(params['uddg'][0])
                return real_url
        except Exception as e:
            print(f"解码错误: {e}")
    
    return url

def search_single(keyword):
    """执行单个搜索"""
    results = []
    
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(keyword)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(search_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # 提取搜索结果
            result_pattern = r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
            matches = re.findall(result_pattern, html, re.DOTALL)
            
            for url, title in matches[:3]:  # 取前3条
                title = re.sub(r'<[^>]+>', '', title).strip()
                real_url = decode_duckduckgo_url(url)
                if title and real_url:
                    results.append({
                        'title': title[:100],
                        'original_url': url[:80] + '...' if len(url) > 80 else url,
                        'decoded_url': real_url[:80] + '...' if len(real_url) > 80 else real_url
                    })
                    
    except Exception as e:
        print(f"搜索失败: {e}")
    
    return results

# 测试搜索
print("🔍 测试搜索: 开封市气象局 招标")
print("=" * 80)
results = search_single("开封市气象局 招标")

for i, item in enumerate(results, 1):
    print(f"\n结果 {i}:")
    print(f"  标题: {item['title']}")
    print(f"  原始链接: {item['original_url']}")
    print(f"  解码链接: {item['decoded_url']}")

print("\n" + "=" * 80)
print("✅ 测试完成")
