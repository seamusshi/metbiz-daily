#!/usr/bin/env python3
"""
Priority Scorer - 紧急度评分器
根据规则为内容评分
"""

import re
from typing import List, Dict, Any

class PriorityScorer:
    def __init__(self, config: Dict):
        self.config = config
        self.rules = config.get('urgency_rules', {})
    
    def score_all(self, classified_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """为所有内容评分"""
        scored = {}
        
        for category, items in classified_data.items():
            scored[category] = [self._score_item(item) for item in items]
        
        return scored
    
    def _score_item(self, item: Dict) -> Dict:
        """为单条内容评分"""
        text = f"{item.get('title', '')} {item.get('content', '')}"
        
        # 检查紧急度规则
        urgency = self._determine_urgency(text)
        item['urgency'] = urgency
        item['urgency_label'] = self._get_urgency_label(urgency)
        
        # 提取关键字段
        item['budget'] = self._extract_budget(text)
        item['province'] = self._extract_province(text)
        item['deadline'] = self._extract_deadline(text)
        
        return item
    
    def _determine_urgency(self, text: str) -> str:
        """确定紧急度"""
        # 按优先级检查规则
        for level in ['urgent', 'high', 'medium']:
            patterns = self.rules.get(level, [])
            for pattern in patterns:
                try:
                    if re.search(pattern, text):
                        return level
                except re.error:
                    continue
        
        return 'low'
    
    def _get_urgency_label(self, urgency: str) -> str:
        """获取紧急度标签"""
        labels = {
            'urgent': '🔴 紧急',
            'high': '🟡 高',
            'medium': '🟢 中',
            'low': '⚪ 低'
        }
        return labels.get(urgency, '⚪ 低')
    
    def _extract_budget(self, text: str) -> str:
        """提取预算金额"""
        # 匹配 "预算：xxx万元" 或 "xxx万元" 或 "xxx元"
        patterns = [
            r'预算[：:]\s*([\d,\.]+)\s*万',
            r'([\d,\.]+)\s*万元',
            r'金额[：:]\s*([\d,\.]+)\s*万'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}万元"
        
        return ""
    
    def _extract_province(self, text: str) -> str:
        """提取省份"""
        provinces = [
            '北京', '天津', '上海', '重庆',
            '河北', '山西', '辽宁', '吉林', '黑龙江',
            '江苏', '浙江', '安徽', '福建', '江西', '山东',
            '河南', '湖北', '湖南', '广东', '海南',
            '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
            '内蒙古', '广西', '西藏', '宁夏', '新疆',
            '香港', '澳门'
        ]
        
        for province in provinces:
            if province in text:
                return province
        
        return ""
    
    def _extract_deadline(self, text: str) -> str:
        """提取截止时间"""
        # 匹配 "截止：2026-xx-xx" 或 "截止日期"
        patterns = [
            r'截止[日期]*[：:]\s*(\d{4}-\d{2}-\d{2})',
            r'(\d{4}年\d{2}月\d{2}日).*截止',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
