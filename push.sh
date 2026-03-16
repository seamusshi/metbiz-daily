#!/bin/bash
# 手动推送脚本 - 使用环境变量中的 GitHub Token
# 用法: export GITHUB_TOKEN=your_token_here && ./push.sh

set -e

REPO_URL="https://${GITHUB_USER:-seamusshi}:${GITHUB_TOKEN}@github.com/seamusshi/metbiz-daily.git"

echo "🚀 推送到 GitHub..."
echo "仓库: seamusshi/metbiz-daily"

# 添加远程仓库（如果不存在）
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# 推送
git push -u origin main

echo "✅ 推送成功！"
echo "🌐 访问: https://github.com/seamusshi/metbiz-daily"
