# MetBiz Daily Report

🌤️ 气象行业情报日报 - 自动化收集与发布系统

[![Daily Report](https://github.com/shixin/metbiz-daily/actions/workflows/daily-report.yml/badge.svg)](https://github.com/shixin/metbiz-daily/actions/workflows/daily-report.yml)

📊 **在线访问**: https://shixin.github.io/metbiz-daily/

## 功能特性

- 📡 **自动收集** - 每日自动扫描招标信息、政策动态、竞品动态
- 🔍 **多源搜索** - 覆盖政府采购网、气象局官网、行业媒体
- 🏷️ **智能分类** - 自动分类并标注紧急程度
- 📱 **响应式设计** - 支持桌面端和移动端访问
- 🔔 **RSS订阅** - 支持通过 RSS 订阅更新

## 监控范围

| 类别 | 内容 |
|------|------|
| 🎯 招标信息 | 各省气象局招投标、中标公告 |
| 📋 政策动态 | 中国气象局及各省政策文件、规划通知 |
| 🏢 竞品动态 | 航天宏图、华云、墨迹天气等企业动态 |
| 💡 技术趋势 | 气象AI、大数据、卫星遥感等新技术 |

## 配置文件

编辑 `config/keywords.yml` 自定义监控关键词：

```yaml
categories:
  tender:
    name: "招标信息"
    keywords:
      - "气象局 招标"
      - "智慧气象 项目"
    provinces:
      - "广东"
      - "江苏"
      - "浙江"
```

## 技术架构

- **数据收集**: Python + Playwright/Scrapy
- **静态生成**: Jinja2 模板引擎
- **定时任务**: GitHub Actions
- **静态托管**: GitHub Pages

## 本地运行

```bash
# 克隆仓库
git clone https://github.com/shixin/metbiz-daily.git
cd metbiz-daily

# 安装依赖
pip install -r requirements.txt

# 生成日报
python main.py

# 查看结果
open output/index.html
```

## 更新频率

每日上午 9:17 (UTC+8) 自动更新

## License

MIT License
