#!/bin/bash

###############################################################################
# 准备Railway部署脚本
# 帮助快速准备代码并推送到GitHub
###############################################################################

echo "=========================================="
echo "   准备Railway部署"
echo "=========================================="
echo ""

# 1. 检查是否已初始化Git
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
    git branch -M main
else
    echo "✅ Git仓库已存在"
fi

# 2. 生成SECRET_KEY
echo ""
echo "🔐 生成SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY: $SECRET_KEY"
echo ""
echo "⚠️  请保存这个密钥，稍后在Railway控制台需要使用！"
echo ""

# 3. 检查必要文件
echo "📋 检查必要文件..."
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "railway.json"
    ".gitignore"
    "backend/app.py"
    "frontend/dist/index.html"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ] && [ ! -d "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ 所有必要文件都存在"
else
    echo "⚠️  缺少以下文件："
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
fi

# 4. 添加所有文件
echo ""
echo "📦 添加文件到Git..."
git add .

# 5. 提交
echo ""
read -p "提交信息（默认: 准备部署到Railway）: " commit_msg
commit_msg=${commit_msg:-"准备部署到Railway"}

git commit -m "$commit_msg" || echo "没有新的改动需要提交"

# 6. 检查远程仓库
echo ""
if git remote | grep -q "origin"; then
    echo "✅ 远程仓库已配置"
    echo "远程地址: $(git remote get-url origin)"
    echo ""
    read -p "是否推送到GitHub? (y/n): " push_confirm
    if [ "$push_confirm" = "y" ] || [ "$push_confirm" = "Y" ]; then
        echo "📤 推送到GitHub..."
        git push origin main || git push -u origin main
        echo "✅ 推送成功！"
    fi
else
    echo "⚠️  还没有配置远程仓库"
    echo ""
    echo "请执行以下步骤："
    echo "1. 访问 https://github.com/new 创建新仓库"
    echo "2. 运行以下命令（替换成你的仓库地址）："
    echo ""
    echo "   git remote add origin https://github.com/你的用户名/仓库名.git"
    echo "   git push -u origin main"
fi

echo ""
echo "=========================================="
echo "✅ 准备完成！"
echo "=========================================="
echo ""
echo "📋 下一步操作："
echo ""
echo "1️⃣  确保代码已推送到GitHub"
echo ""
echo "2️⃣  访问 https://railway.app/"
echo "   - 使用GitHub登录"
echo "   - 点击 'Deploy from GitHub repo'"
echo "   - 选择你的仓库"
echo ""
echo "3️⃣  在Railway添加环境变量："
echo "   DATABASE_PATH = /app/data/project_management.db"
echo "   SECRET_KEY = $SECRET_KEY"
echo "   FLASK_ENV = production"
echo ""
echo "4️⃣  等待构建完成（5-10分钟）"
echo ""
echo "5️⃣  获取域名并访问！"
echo ""
echo "📖 详细教程: ./Railway部署详细教程.md"
echo "📖 快速指南: ./README_RAILWAY.md"
echo ""

