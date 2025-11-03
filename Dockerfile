# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（用于Pillow）
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff6 \
    && rm -rf /var/lib/apt/lists/*

# 复制应用程序代码
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 创建必要的目录
RUN mkdir -p backend/wallpapers backend/thumbnails

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 启动应用
CMD ["python", "backend/app.py"]