#!/bin/bash

# 壁纸项目容器化部署脚本
# 适用于FNOS服务器

set -e

# 配置变量
PROJECT_NAME="wallpaper"
IMAGE_NAME="wallpaper-app"
CONTAINER_NAME="wallpaper-app"
NGINX_CONTAINER_NAME="wallpaper-nginx"
PORT=5000

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker和Docker Compose检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录结构..."
    
    mkdir -p backend/wallpapers
    mkdir -p backend/thumbnails
    mkdir -p ssl
    
    log_success "目录创建完成"
}

# 构建镜像
build_image() {
    log_info "开始构建Docker镜像..."
    
    if docker-compose build; then
        log_success "镜像构建完成"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d wallpaper-app
    log_success "应用服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    docker-compose down
    log_success "服务已停止"
}

# 查看日志
view_logs() {
    local service=$1
    docker-compose logs -f $service
}

# 清理数据
clean_data() {
    log_warning "即将清理所有容器、镜像和数据，确定继续吗？(y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "清理所有数据..."
        docker-compose down -v --rmi all
        log_success "数据清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 显示帮助
show_help() {
    echo "壁纸项目部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build           构建Docker镜像"
    echo "  start           启动服务"
    echo "  stop            停止服务"
    echo "  restart         重启服务"
    echo "  logs [service]  查看日志（可选参数：wallpaper-app, nginx）"
    echo "  clean           清理所有数据"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build"
    echo "  $0 start"
    echo "  $0 start-nginx"
    echo "  $0 logs wallpaper-app"
    echo "  $0 clean"
}

# 主函数
main() {
    case "$1" in
        build)
            check_docker
            create_directories
            build_image
            ;;
        start)
            check_docker
            create_directories
            start_services
            log_info "服务启动完成！"
            log_info "访问地址: http://localhost:5000"
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        logs)
            if [ -z "$2" ]; then
                view_logs "wallpaper-app"
            else
                view_logs "$2"
            fi
            ;;
        clean)
            clean_data
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"