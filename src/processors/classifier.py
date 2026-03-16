#!/usr/bin/env python3
"""
Content Classifier - 内容分类器
将搜索结果分类到不同维度
"""

import re
from typing import List, Dict, Any

class ContentClassifier:
    def __init__(self, config: Dict):
        self.config = config
        self.categories = config.get('categories', {})
    
    def classify(self, raw_data: List[Dict]) -> Dict[str, List[Dict]]:
        """对原始数据进行分类"""
        classified = {cat_id: [] for cat_id in self.categories.keys()}
        
        for item in raw_data:
            category = self._determine_category(item)
            if category:
                item['category'] = category
                classified[category].append(item)
        
        return classified
    
    def _determine_category(self, item: Dict) -> str:
        """确定数据所属分类"""
        title = item.get('title', '').lower()
        content = item.get('content', '').lower()
        text = f"{title} {content}"
        
        # 招标信息检测
        if self._is_tender(text):
            return 'tender'
        
        # 竞品动态检测
        if self._is_competitor(text):
            return 'competitor'
        
        # 政策动态检测
        if self._is_policy(text):
            return 'policy'
        
        # 技术趋势检测
        if self._is_technology(text):
            return 'technology'
        
        # 默认分类
        return 'tender'
    
    def _is_tender(self, text: str) -> bool:
        """检测是否为招标信息"""
        tender_keywords = [
            '招标', '中标', '采购', '投标', '询价', '竞争性磋商',
            '招标公告', '中标公告', '中标结果', '成交公告'
        ]
        return any(kw in text for kw in tender_keywords)
    
    def _is_competitor(self, text: str) -> bool:
        """检测是否为竞品动态"""
        competitor_names = []
        comp_config = self.categories.get('competitor', {})
        
        for company in comp_config.get('companies', []):
            competitor_names.append(company['name'].lower())
        
        return any(name in text for name in competitor_names)
    
    def _is_policy(self, text: str) -> bool:
        """检测是否为政策动态"""
        policy_keywords = [
            '政策', '通知', '意见', '规划', '纲要', '办法',
            '发布', '印发', '出台', '实施'
        ]
        has_policy_kw = any(kw in text for kw in policy_keywords)
        has_gov = '气象局' in text or '政府' in text
        return has_policy_kw and has_gov
    
    def _is_technology(self, text: str) -> bool:
        """检测是否为技术趋势"""
        tech_keywords = [
            '人工智能', 'ai', '大模型', '大数据', '机器学习',
            '深度学习', '遥感', '卫星', '雷达', '算法'
        ]
        return any(kw in text for kw in tech_keywords)
