#!/bin/bash

# SmartTime 系统部署脚本

echo "🚀 SmartTime 智能时间管理系统部署脚本"
echo "=========================================="

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Python版本: $python_version"
else
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查pip
echo "📋 检查pip..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3已安装"
    pip_cmd="pip3"
elif command -v pip &> /dev/null; then
    echo "✅ pip已安装"
    pip_cmd="pip"
else
    echo "❌ 未找到pip，请先安装pip"
    exit 1
fi

# 安装依赖
echo "📦 安装Python依赖..."
if [ -f "requirements.txt" ]; then
    $pip_cmd install -r requirements.txt
    if [[ $? -eq 0 ]]; then
        echo "✅ 依赖安装成功"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "⚠️  未找到requirements.txt文件"
fi

# 检查环境变量文件
echo "📋 检查环境配置..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 创建环境配置文件..."
        cp .env.example .env
        echo "✅ 已创建.env文件，请根据需要修改数据库配置"
        echo "💡 请编辑.env文件，配置以下数据库信息："
        echo "   - DB_HOST: 数据库主机地址"
        echo "   - DB_PORT: 数据库端口"
        echo "   - DB_USERNAME: 数据库用户名"
        echo "   - DB_PASSWORD: 数据库密码"
        echo "   - DB_DATABASE: 数据库名称"
    else
        echo "⚠️  未找到.env.example文件"
    fi
else
    echo "✅ 环境配置文件已存在"
fi

# 检查数据库连接
echo "🔍 测试数据库连接..."
python3 -c "
import asyncio
import sys
import os
sys.path.append('app')
from database import db_manager

async def test_db():
    try:
        await db_manager.initialize()
        print('✅ 数据库连接成功')
        await db_manager.close()
    except Exception as e:
        print(f'❌ 数据库连接失败: {e}')
        sys.exit(1)

asyncio.run(test_db())
"

if [[ $? -ne 0 ]]; then
    echo "❌ 数据库连接测试失败，请检查配置"
    exit 1
fi

# 启动服务器
echo "🚀 启动SmartTime服务器..."
echo "📝 服务器将在 http://localhost:8010 启动"
echo "📝 按 Ctrl+C 停止服务器"
echo ""

cd app
python3 run.py 