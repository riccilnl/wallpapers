FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p backend/wallpapers backend/thumbnails

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV PYTHONPATH=/app

# 启动应用
CMD ["python", "backend/app.py"]