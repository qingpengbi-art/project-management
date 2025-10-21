#!/bin/bash

###############################################################################
# 项目打包脚本 - 用于迁移到Windows
###############################################################################

echo "=========================================="
echo "   项目管理系统 - 打包工具"
echo "=========================================="
echo ""

# 询问是否保留数据
read -p "是否保留现有数据？(y/n，默认n): " KEEP_DATA
KEEP_DATA=${KEEP_DATA:-n}

if [ "$KEEP_DATA" = "y" ] || [ "$KEEP_DATA" = "Y" ]; then
    OUTPUT_FILE="project-management-with-data.tar.gz"
    EXCLUDE_DATA=""
    echo "📦 将打包项目（包含数据）..."
else
    OUTPUT_FILE="project-management-clean.tar.gz"
    EXCLUDE_DATA="--exclude='data'"
    echo "📦 将打包项目（不含数据，全新部署）..."
fi

echo ""
echo "正在清理临时文件..."

# 清理Python缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "正在打包..."

# 打包项目
tar -czf "$OUTPUT_FILE" \
  --exclude='*.log' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='backend/venv' \
  --exclude='.git' \
  --exclude='.DS_Store' \
  --exclude='*.swp' \
  --exclude='.vscode' \
  --exclude='.idea' \
  --exclude='logs/*.log' \
  --exclude='frontend10022340.zip' \
  $EXCLUDE_DATA \
  .

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo "=========================================="
    echo "✅ 打包成功！"
    echo "=========================================="
    echo ""
    echo "📦 文件名: $OUTPUT_FILE"
    echo "📊 大小: $SIZE"
    echo "📍 位置: $(pwd)/$OUTPUT_FILE"
    echo ""
    echo "🔄 迁移步骤："
    echo "   1. 将此文件复制到Windows电脑"
    echo "   2. 在Windows上解压"
    echo "   3. 按照 Windows部署指南.md 操作"
    echo ""
else
    echo ""
    echo "❌ 打包失败！"
    exit 1
fi

