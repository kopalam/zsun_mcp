# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY app/ /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -e .

# 暴露端口（如果需要的话）
EXPOSE 8010

# 设置启动命令
CMD ["python", "run.py"] 