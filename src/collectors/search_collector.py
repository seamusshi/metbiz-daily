#!/usr/bin/env python3
"""
Search Collector - 搜索数据收集器
使用 kimi_search 进行多关键词并行搜索
"""

import json
import time
from typing import List, Dict, Any

class SearchCollector:
    def __init__(self, config: Dict):
        self.config = config
        self.all_keywords = self._extract_all_keywords()
    
    def _extract_all_keywords(self) -> List[str]:
        """从配置中提取所有搜索关键词"""
        keywords = []
        categories = self.config.get('categories', {})
        
        for cat_id, cat_config in categories.items():
            # 提取分类关键词
            if 'keywords' in cat_config:
                keywords.extend(cat_config['keywords'])
            
            # 提取竞品公司关键词
            if 'companies' in cat_config:
                for company in cat_config['companies']:
                    if 'keywords' in company:
                        keywords.extend(company['keywords'])
        
        # 去重并返回
        return list(set(keywords))
    
    def collect_all(self) -> List[Dict[str, Any]]:
        """执行所有搜索任务"""
        all_results = []
        
        print(f"   准备搜索 {len(self.all_keywords)} 个关键词...")
        
        # 串行执行（避免请求过快）
        for i, keyword in enumerate(self.all_keywords, 1):
            print(f"   [{i}/{len(self.all_keywords)}] 搜索: {keyword}")
            results = self._search_single(keyword)
            all_results.extend(results)
            time.sleep(1)  # 避免请求过快
        
        # 去重
        unique_results = self._deduplicate(all_results)
        print(f"   去重后: {len(unique_results)} 条")
        
        return unique_results
    
    def _search_single(self, keyword: str) -> List[Dict[str, Any]]:
        """执行单个搜索 - 使用 web_search 工具"""
        results = []
        
        try:
            # 使用 brave web search (Python 实现)
            import urllib.request
            import urllib.parse
            
            # Brave Search API (需要 API key)
            # 这里使用 duckduckgo 搜索作为免费替代
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(keyword)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(search_url, headers=headers)
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                    
                    # 简单解析搜索结果
                    import re
                    # 提取结果标题和链接
                    result_pattern = r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
                    matches = re.findall(result_pattern, html, re.DOTALL)
                    
                    for url, title in matches[:5]:  # 取前5条
                        # 清理标题
                        title = re.sub(r'<[^>]+>', '', title).strip()
                        if title and url:
                            results.append({
                                'title': title[:200],
                                'url': url,
                                'snippet': title,
                                'source': 'duckduckgo',
                                'keyword': keyword
                            })
            except Exception as e:
                print(f"   搜索请求失败: {e}")
                
        except Exception as e:
            print(f"   搜索失败 [{keyword}]: {e}")
        
        return results
    
    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """按URL去重"""
        seen_urls = set()
        unique = []
        
        for item in results:
            url = item.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(item)
            elif not url:
                unique.append(item)
        
        return unique
