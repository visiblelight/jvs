#!/usr/bin/env bash
set -e

echo "=============================="
echo " JVS 自动化测试"
echo "=============================="

cd "$(dirname "$0")/backend"

echo ""
echo "▶ 安装测试依赖..."
pip install -r requirements-dev.txt -q

echo ""
echo "▶ 运行后端 API 集成测试..."
python -m pytest tests/ -v --tb=short

echo ""
echo "=============================="
echo " 所有测试通过 ✓"
echo "=============================="
