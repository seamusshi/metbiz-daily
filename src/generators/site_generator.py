#!/usr/bin/env python3
"""
Site Generator - 网站生成器
生成静态HTML日报网站
"""

import json
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class SiteGenerator:
    def __init__(self, config: dict, output_dir: str = "output"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化模板引擎
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate(self, data: dict, date_str: str):
        """生成完整网站"""
        # 生成首页（最新日报）
        self._generate_index(data, date_str)
        
        # 生成历史归档页面
        self._generate_archive(data, date_str)
        
        # 生成关于页面
        self._generate_about()
        
        # 生成RSS订阅
        self._generate_rss(data, date_str)
        
        # 复制静态资源
        self._copy_static_assets()
    
    def _generate_index(self, data: dict, date_str: str):
        """生成首页"""
        template = self.env.get_template("index.html")
        
        html = template.render(
            report=data,
            config=self.config,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        index_path = self.output_dir / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_archive(self, data: dict, date_str: str):
        """生成归档页面"""
        template = self.env.get_template("archive.html")
        
        # 获取历史报告列表
        archive_files = sorted(self.output_dir.glob("*.json"))
        archive_list = []
        
        for f in archive_files:
            if f.stem not in ['latest', 'archive']:
                try:
                    with open(f, 'r', encoding='utf-8') as file:
                        report = json.load(file)
                        archive_list.append({
                            'date': report.get('date', f.stem),
                            'total': report.get('summary', {}).get('total', 0)
                        })
                except:
                    pass
        
        html = template.render(
            archives=archive_list[-30:],  # 最近30天
            config=self.config
        )
        
        archive_path = self.output_dir / "archive.html"
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_about(self):
        """生成关于页面"""
        template = self.env.get_template("about.html")
        html = template.render(config=self.config)
        
        about_path = self.output_dir / "about.html"
        with open(about_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_rss(self, data: dict, date_str: str):
        """生成RSS订阅"""
        template = self.env.get_template("feed.xml")
        
        rss = template.render(
            report=data,
            config=self.config,
            build_date=datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0800')
        )
        
        rss_path = self.output_dir / "feed.xml"
        with open(rss_path, 'w', encoding='utf-8') as f:
            f.write(rss)
    
    def _copy_static_assets(self):
        """复制静态资源"""
        # 创建简单的内联CSS，不依赖外部文件
        pass
