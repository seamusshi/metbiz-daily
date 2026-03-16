#!/usr/bin/env python3
"""
Search Collector - 搜索数据收集器
使用 DuckDuckGo 搜索并过滤最近1个月的信息
"""

import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

class SearchCollector:
    def __init__(self, config: Dict):
        self.config = config
        self.all_keywords = self._extract_all_keywords()
        # 只保留最近1个月的信息
        self.cutoff_date = datetime.now() - timedelta(days=30)
        self.current_year = datetime.now().year
    
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
        print(f"   过滤条件: 只保留 {self.cutoff_date.strftime('%Y-%m-%d')} 之后的信息")
        
        # 串行执行（避免请求过快）
        for i, keyword in enumerate(self.all_keywords, 1):
            print(f"   [{i}/{len(self.all_keywords)}] 搜索: {keyword}")
            results = self._search_single(keyword)
            all_results.extend(results)
            time.sleep(1)  # 避免请求过快
        
        # 去重
        unique_results = self._deduplicate(all_results)
        
        # 按日期过滤
        filtered_results = self._filter_by_date(unique_results)
        
        print(f"   去重后: {len(unique_results)} 条")
        print(f"   日期过滤后: {len(filtered_results)} 条")
        
        return filtered_results
    
    def _search_single(self, keyword: str) -> List[Dict[str, Any]]:
        """执行单个搜索"""
        results = []
        
        try:
            import urllib.request
            import urllib.parse
            
            # 在搜索关键词中添加年份限制，优先搜索最近2年的内容
            search_query = f"{keyword} {self.current_year} OR {self.current_year - 1}"
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(search_url, headers=headers)
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                    
                    # 提取结果标题和链接
                    result_pattern = r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
                    matches = re.findall(result_pattern, html, re.DOTALL)
                    
                    # 提取摘要
                    snippet_pattern = r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>'
                    snippets = re.findall(snippet_pattern, html, re.DOTALL)
                    
                    for idx, (url, title) in enumerate(matches[:5]):
                        title = re.sub(r'<[^>]+>', '', title).strip()
                        real_url = self._decode_duckduckgo_url(url)
                        
                        # 获取摘要
                        snippet = ''
                        if idx < len(snippets):
                            snippet = re.sub(r'<[^>]+>', '', snippets[idx]).strip()
                        if not snippet:
                            snippet = title
                        
                        # 从标题中提取年份进行预过滤
                        year_match = re.search(r'(202[0-5])', title)
                        if year_match:
                            year = int(year_match.group(1))
                            if year < self.current_year - 1:  # 如果是2024年及更早
                                print(f"     [预过滤] 旧年份 ({year}): {title[:50]}...")
                                continue
                        
                        # 提取日期信息
                        date_info = self._extract_date(title, snippet)
                        
                        if title and real_url:
                            results.append({
                                'title': title[:200],
                                'url': real_url,
                                'snippet': snippet[:300],
                                'summary': snippet[:300],
                                'content': snippet[:300],
                                'source': 'duckduckgo',
                                'keyword': keyword,
                                'date_str': date_info.get('date_str'),
                                'deadline': date_info.get('deadline'),
                                'is_expired': date_info.get('is_expired', False)
                            })
            except Exception as e:
                print(f"   搜索请求失败: {e}")
                
        except Exception as e:
            print(f"   搜索失败 [{keyword}]: {e}")
        
        return results
    
    def _extract_date(self, title: str, snippet: str) -> Dict:
        """从标题和摘要中提取日期信息"""
        text = title + " " + snippet
        result = {'date_str': None, 'deadline': None, 'is_expired': False}
        
        # 匹配各种日期格式
        date_patterns = [
            r'(\d{4})[-年.](\d{1,2})[-月.](\d{1,2})[日]?',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
        ]
        
        found_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    year, month, day = int(match[0]), int(match[1]), int(match[2])
                    if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                        date_obj = datetime(year, month, day)
                        found_dates.append({
                            'date_str': f"{year}-{month:02d}-{day:02d}",
                            'date_obj': date_obj
                        })
                except:
                    pass
        
        # 找最近的日期作为发布日期
        if found_dates:
            found_dates.sort(key=lambda x: x['date_obj'], reverse=True)
            result['date_str'] = found_dates[0]['date_str']
        
        # 尝试提取截止日期
        deadline_patterns = [
            r'截止[时间]?[:\s]*(\d{4}[-年.]\d{1,2}[-月.]\d{1,2})',
            r'投标截止[:\s]*(\d{4}[-年.]\d{1,2}[-月.]\d{1,2})',
            r'报名截止[:\s]*(\d{4}[-年.]\d{1,2}[-月.]\d{1,2})',
            r'截止日期[:\s]*(\d{4}[-年.]\d{1,2}[-月.]\d{1,2})',
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(1).replace('年', '-').replace('月', '-').replace('.', '-')
                    parts = date_str.split('-')
                    if len(parts) == 3:
                        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                        deadline = datetime(year, month, day)
                        result['deadline'] = deadline.strftime('%Y-%m-%d')
                        result['is_expired'] = deadline < datetime.now()
                except:
                    pass
                break
        
        return result
    
    def _filter_by_date(self, results: List[Dict]) -> List[Dict]:
        """按日期过滤，只保留最近1个月的信息，过滤已过期的招标"""
        filtered = []
        
        for item in results:
            # 如果是招标信息且已过期，跳过
            if item.get('is_expired'):
                print(f"     [过滤] 已过期招标: {item['title'][:40]}...")
                continue
            
            # 如果有日期信息，检查是否在1个月内
            date_str = item.get('date_str')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    if date_obj >= self.cutoff_date:
                        filtered.append(item)
                    else:
                        print(f"     [过滤] 过期信息 ({date_str}): {item['title'][:40]}...")
                except:
                    # 日期解析失败，保留
                    filtered.append(item)
            else:
                # 没有日期信息，但有年份过滤过的，保留
                filtered.append(item)
        
        return filtered
    
    def _decode_duckduckgo_url(self, url: str) -> str:
        """解码 DuckDuckGo 重定向 URL"""
        import urllib.parse
        
        if url.startswith('//'):
            url = 'https:' + url
        
        if 'duckduckgo.com/l/' in url or 'duckduckgo.com/l?' in url:
            try:
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                
                if 'uddg' in params:
                    return urllib.parse.unquote(params['uddg'][0])
                elif 'rurl' in params:
                    return urllib.parse.unquote(params['rurl'][0])
            except:
                pass
        
        return url
    
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
