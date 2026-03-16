#!/usr/bin/env python3
"""
MetBiz Daily Report - 主入口
气象行业情报日报生成器
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from collectors.search_collector import SearchCollector
from processors.classifier import ContentClassifier
from processors.priority import PriorityScorer
from generators.json_exporter import JSONExporter
from generators.site_generator import SiteGenerator

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config" / "keywords.yml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    """主流程"""
    print("🚀 MetBiz Daily Report 开始生成...")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载配置
    config = load_config()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 数据收集
    print("\n📡 阶段1: 数据收集...")
    collector = SearchCollector(config)
    raw_data = collector.collect_all()
    print(f"   收集到 {len(raw_data)} 条原始数据")
    
    # 内容分类
    print("\n📂 阶段2: 内容分类...")
    classifier = ContentClassifier(config)
    classified = classifier.classify(raw_data)
    for cat, items in classified.items():
        print(f"   {cat}: {len(items)} 条")
    
    # 紧急度评分
    print("\n🔥 阶段3: 紧急度评分...")
    scorer = PriorityScorer(config)
    scored = scorer.score_all(classified)
    
    # 生成报告数据
    report_data = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "summary": generate_summary(scored),
        "categories": format_categories(scored, config)
    }
    
    # 输出JSON
    print("\n💾 阶段4: 导出数据...")
    json_exporter = JSONExporter()
    json_path = json_exporter.export(report_data, today)
    print(f"   JSON已保存: {json_path}")
    
    # 生成网站
    print("\n🌐 阶段5: 生成网站...")
    site_gen = SiteGenerator(config)
    site_gen.generate(report_data, today)
    print(f"   网站已生成到 output/ 目录")
    
    print("\n✅ 日报生成完成!")
    return report_data

def generate_summary(scored_data):
    """生成统计摘要"""
    total = 0
    urgency_count = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
    
    for cat_items in scored_data.values():
        for item in cat_items:
            total += 1
            urgency = item.get('urgency', 'low')
            urgency_count[urgency] = urgency_count.get(urgency, 0) + 1
    
    return {
        "total": total,
        "urgent": urgency_count.get('urgent', 0),
        "high": urgency_count.get('high', 0),
        "medium": urgency_count.get('medium', 0),
        "low": urgency_count.get('low', 0)
    }

def format_categories(scored_data, config):
    """格式化分类数据"""
    categories = []
    
    for cat_id, items in scored_data.items():
        if not items:
            continue
            
        cat_config = config['categories'].get(cat_id, {})
        category = {
            "id": cat_id,
            "name": cat_config.get('name', cat_id),
            "description": cat_config.get('description', ''),
            "items": sorted(items, key=lambda x: urgency_order(x.get('urgency', 'low')))
        }
        categories.append(category)
    
    # 按优先级排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    categories.sort(key=lambda x: priority_order.get(config['categories'].get(x['id'], {}).get('priority', 'low'), 3))
    
    return categories

def urgency_order(urgency):
    """紧急度排序"""
    order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    return order.get(urgency, 4)

if __name__ == "__main__":
    main()
