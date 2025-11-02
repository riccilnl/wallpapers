# FNOS服务器部署指南

## 概述

本指南将帮助您在FNOS服务器上部署壁纸管理应用。该应用已完全容器化，支持直接运行或通过Nginx反向代理部署。

## 环境要求

### 硬件要求
- CPU: 1核及以上
- 内存: 1GB及以上
- 存储: 根据壁纸数量而定，建议预留足够空间
- 网络: 稳定的互联网连接

### 软件要求
- FNOS系统（基于Linux）
- Docker 20.10+
- Docker Compose 1.29+

## 部署步骤

### 1. 准备工作

#### 1.1 检查系统环境
```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version

# 检查系统资源
df -h  # 查看磁盘空间
free -h  # 查看内存使用
```

#### 1.2 安装Docker（如未安装）
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 部署应用

#### 2.1 上传项目文件
将以下文件上传到FNOS服务器的项目目录：
- `Dockerfile`
- `docker-compose.yml`
- `deploy.sh`
- `backend/` 目录
- `static/` 目录
- `index.html`

#### 2.2 设置部署脚本权限
```bash
chmod +x deploy.sh
```

#### 2.3 构建和启动服务
```bash
# 构建镜像
./deploy.sh build

# 启动服务
./deploy.sh start
```

### 4. 数据管理

#### 4.1 壁纸文件存放
壁纸文件应放置在：
```
backend/
└── wallpapers/
    ├── 风景/
    │   ├── image1.jpg
    │   └── image2.png
    └── 动漫/
        ├── anime1.jpg
        └── anime2.png
```

#### 4.2 数据持久化
Docker容器会自动将以下目录挂载到宿主机：
- `./backend/wallpapers` → 容器内壁纸目录
- `./backend/thumbnails` → 容器内缩略图目录
- `./backend/wallpaper_cache.json` → 容器内缓存文件

### 5. 服务管理

#### 5.1 常用命令
```bash
# 查看服务状态
docker-compose ps

# 查看日志
./deploy.sh logs wallpaper-app
./deploy.sh logs nginx  # 如果使用了Nginx

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop

# 清理所有数据（谨慎使用）
./deploy.sh clean
```

#### 5.2 监控服务
```bash
# 查看容器资源使用
docker stats

# 查看容器日志
docker logs wallpaper-app -f
```

## 访问应用

### 1. 直接访问
- HTTP: `http://服务器IP:5000`
- HTTPS: `https://服务器IP:5000`（需自行配置SSL）


## 配置说明

### 1. 环境变量配置
在`docker-compose.yml`中可配置：
```yaml
environment:
  - FLASK_ENV=production
  - FLASK_APP=backend/app.py
```

### 2. 端口配置
- 默认应用端口：5000

如需修改端口，在`docker-compose.yml`中调整：
```yaml
ports:
  - "8080:5000"  # 将容器的5000端口映射到宿主机的8080端口
```

### 3. 存储配置
确保宿主机有足够的存储空间存放壁纸文件，建议：
- 定期清理不需要的壁纸
- 监控磁盘使用情况
- 考虑使用外部存储挂载

## 故障排除

### 1. 常见问题

**Q: 服务启动失败**
A: 检查Docker和Docker Compose是否正确安装，查看日志定位问题：
```bash
./deploy.sh logs wallpaper-app
```

**Q: 无法访问应用**
A: 检查：
1. 防火墙设置是否开放了相应端口
2. Docker容器是否正常运行
3. 网络配置是否正确

**Q: 壁纸无法显示**
A: 检查：
1. `backend/wallpapers`目录是否有读写权限
2. 壁纸文件格式是否支持（.jpg, .jpeg, .png, .gif, .webp, .bmp）
3. 文件路径是否正确

### 2. 日志查看
```bash
# 查看应用日志
docker logs wallpaper-app

# 查看Nginx日志
docker logs wallpaper-nginx
```

### 3. 重启服务
```bash
# 重启应用
./deploy.sh restart

# 或者单独重启
docker-compose restart wallpaper-app
```

## 安全建议

### 1. 网络安全
- 配置防火墙，只开放必要的端口
- 使用HTTPS加密传输
- 定期更新系统和Docker

### 2. 数据安全
- 定期备份壁纸文件和配置
- 设置适当的文件权限
- 监控异常访问

### 3. 容器安全
- 使用官方基础镜像
- 定期更新容器镜像
- 限制容器权限

## 性能优化

### 1. 缓存优化
- 启用浏览器缓存（Nginx配置中已包含）
- 定期清理缩略图缓存
- 使用CDN加速静态资源

### 2. 资源优化
- 压缩壁纸文件大小
- 使用合适的缩略图尺寸
- 优化数据库查询（如有）

## 更新和维护

### 1. 应用更新
```bash
# 停止服务
./deploy.sh stop

# 更新代码文件

# 重新构建
./deploy.sh build

# 启动服务
./deploy.sh start
```

### 2. 定期维护
- 检查磁盘空间使用
- 清理过期日志
- 更新依赖包
- 备份重要数据

## 技术支持

如果遇到问题，请：
1. 查看日志文件定位问题
2. 检查配置文件是否正确
3. 参考故障排除章节
4. 联系技术支持

---

**注意**: 本指南基于标准FNOS环境编写，具体配置可能需要根据您的实际环境进行调整。