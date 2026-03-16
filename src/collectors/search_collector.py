#!/usr/bin/env python3
"""
Search Collector - 搜索数据收集器
使用 kimi_search 进行多关键词并行搜索
"""

import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        
        # 串行执行（因为 kimi_search 是外部工具调用）
        for i, keyword in enumerate(self.all_keywords, 1):
            print(f"   [{i}/{len(self.all_keywords)}] 搜索: {keyword}")
            results = self._search_single(keyword)
            all_results.extend(results)
        
        # 去重
        unique_results = self._deduplicate(all_results)
        print(f"   去重后: {len(unique_results)} 条")
        
        return unique_results
    
    def _search_single(self, keyword: str) -> List[Dict[str, Any]]:
        """执行单个搜索 - 调用 kimi_search 工具"""
        results = []
        
        try:
            # 这里使用工具调用，实际运行时由 OpenClaw 环境提供
            # 为了可测试性，我们先模拟返回结构
            # 真实运行时，这个函数会被实际的 kimi_search 调用替换
            
            # 模拟数据用于结构验证
            # 实际部署时，这里会调用 tools.kimi_search
            pass
            
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
