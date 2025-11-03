#!/bin/bash

# 壁纸管理库部署脚本

echo "开始部署壁纸管理库..."

# 检查是否安装了 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker"
    exit 1
fi

# 检查是否安装了 docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装 docker-compose"
    exit 1
fi

# 构建并启动容器
echo "构建 Docker 镜像..."
docker-compose build

echo "启动容器..."
docker-compose up -d

# 检查容器状态
echo "检查容器状态..."
docker-compose ps

echo "部署完成!"
echo "访问地址: http://localhost:5000"
echo "API 地址: http://localhost:5000/api"
echo "分类地址: http://localhost:5000/categories"