#!/bin/bash

# 部署脚本 - 提交 app/ 目录下的修改并推送到 main 分支

echo "🚀 开始部署流程..."

# 添加 app/ 目录下的所有文件到 git
echo "📁 添加 app/ 目录下的文件到 git..."
git add app/

# 检查是否有文件被暂存
if git diff --cached --quiet; then
    echo "❌ 没有检测到 app/ 目录下的修改，无需提交"
    exit 0
fi

# 显示将要提交的文件
echo "📋 将要提交的文件："
git diff --cached --name-only

# 提示用户输入提交信息
echo ""
echo "💬 请输入提交信息："
read -r commit_message

# 检查提交信息是否为空
if [ -z "$commit_message" ]; then
    echo "❌ 提交信息不能为空"
    exit 1
fi

# 提交更改
echo "💾 提交更改..."
git commit -m "$commit_message"

# 检查提交是否成功
if [ $? -eq 0 ]; then
    echo "✅ 提交成功！"
else
    echo "❌ 提交失败"
    exit 1
fi

# 推送到 main 分支
echo "🚀 推送到 main 分支..."
git push origin main

# 检查推送是否成功
if [ $? -eq 0 ]; then
    echo "🎉 部署完成！已成功推送到 main 分支"
else
    echo "❌ 推送失败"
    exit 1
fi
