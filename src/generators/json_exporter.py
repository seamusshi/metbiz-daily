#!/usr/bin/env python3
"""
JSON Exporter - JSON导出器
"""

import json
from datetime import datetime
from pathlib import Path

class JSONExporter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export(self, data: dict, date_str: str) -> str:
        """导出数据为JSON文件"""
        # 主数据文件
        json_path = self.output_dir / f"{date_str}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 最新数据文件（用于API访问）
        latest_path = self.output_dir / "latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(json_path)
