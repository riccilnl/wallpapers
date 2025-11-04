# 壁纸管理库

一个基于Python Flask的智能壁纸管理服务，集成了AI图片分析和重命名功能，提供Web界面浏览和管理壁纸。

## 文件结构

```
wallpaper-main/
├── backend/
│   ├── app.py           # 主程序文件（Web服务）
│   ├── rename.py        # AI图片重命名工具
│   ├── requirements.txt # 依赖包列表
│   ├── wallpapers/      # 图片存储目录
│   ├── thumbnails/      # 缩略图缓存目录
│   ├── rename.json      # 重命名记录文件
│   └── wallpaper_cache.json # 缓存文件
├── static/              # 前端静态文件目录
├── index.html           # 前端主页面
└── README.md           # 说明文档
```

## 功能特性

### 🤖 AI智能分析
- 使用智谱GLM-4.5V多模态模型分析图片内容
- 自动识别图片类型（风光、美女、动漫、汽车、城市）
- 生成6个精准关键词标签
- 智能压缩图片以减少带宽占用

### 🖼️ 壁纸管理
- 自动扫描本地图片文件
- 智能分类和标签生成
- 动态缩略图生成
- 支持局域网访问
- 一键设置桌面壁纸

### 📱 Web界面
- 响应式设计，支持移动端
- 暗色主题
- 分类浏览和搜索
- API接口供第三方集成

## 安装和运行

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动Web服务
```bash
cd backend
python app.py
```

### 3. 访问服务
打开浏览器访问：`http://localhost:5000` 或你的局域网IP地址

## AI图片重命名使用

### 1. 配置API密钥
在 `backend/rename.py` 中设置智谱AI API密钥：
```python
API_KEY = "your_api_key_here"  # 智谱API密钥
```

### 2. 运行重命名工具
```bash
cd backend
python rename.py
```

### 3. 处理模式
- **单文件处理**：修改 `main()` 函数中的 `image_path`
- **批量处理**：修改 `main()` 函数中的 `directory_path`

## API接口

### 获取壁纸列表（包含AI标签，支持分页）
```
GET /api?cid=分类ID&start=起始位置&count=数量
```

**参数说明：**
- `cid`: 分类ID（可选，默认为'all'）
- `start`: 起始位置（可选，默认为0）
- `count`: 每页数量（可选，默认为30，最大100）

**响应格式（新增keywords字段和分页信息）：**
```json
{
  "code": 200,
  "data": [
    {
      "id": "图片唯一ID",
      "url": "图片URL",
      "thumbnail": "缩略图URL",
      "tag": "综合标签",
      "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5", "关键词6"],
      "width": 1920,
      "height": 1080,
      "size": 1024000,
      "uploaded_at": "2023-01-01T12:00:00"
    }
  ],
  "total": 10000,
  "has_more": true,
  "limit": 30
}
```

**分页示例：**
```bash
# 获取前30条
GET /api?start=0&count=30

# 获取31-60条
GET /api?start=30&count=30

# 按分类分页
GET /api?cid=风光&start=0&count=50
```

### 获取分类列表
```
GET /categories
```

### 清空缓存
```
GET /clear-cache
```

### 设置桌面壁纸
```bash
POST /set-wallpaper
Content-Type: application/json

{
  "url": "/images/图片路径.jpg"
}
```

## 文件命名规范

AI重命名后的文件采用以下格式：
```
类型_关键词1_关键词2_关键词3_关键词4_关键词5_关键词6.jpg
```

示例：
- `风光_黄昏_山脉_雾气_湖泊_森林_日出.jpg`
- `美女_时尚_都市_街拍_模特_长发_微笑.png`

## 配置说明

### Web服务配置
在 `backend/app.py` 中修改：
```python
class Config:
    IMAGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wallpapers')
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
```

### AI分析配置
在 `backend/rename.py` 中修改：
```python
API_KEY = "0exxxxxxxxxxxxxxxxxxx.e26D2EYwgs1eMQ2e"  # 智谱API密钥
API_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
```

## 使用流程

1. **图片收集**：将待处理的图片放入 `backend/wallpapers/` 目录
2. **AI分析**：运行 `rename.py` 进行智能分析和重命名
3. **Web浏览**：启动 `app.py` 通过浏览器访问和管理壁纸
4. **设置壁纸**：在Web界面一键设置喜欢的图片为桌面背景

## 容器化部署

### 环境变量配置

创建 `.env` 文件配置智谱API密钥：

```bash
# .env
ZHIPU_API_KEY=your_api_key_here
```

### Docker Compose部署

```bash
# 构建并启动容器
docker-compose up -d

# 停止容器
docker-compose down

# 查看容器日志
docker-compose logs -f
```

### Docker部署

```bash
# 构建镜像
docker build -t wallpaper-app .

# 运行容器
docker run -d \
  --name wallpaper-container \
  -p 5000:5000 \
  -e ZHIPU_API_KEY=your_api_key_here \
  -v $(pwd)/backend/wallpapers:/app/backend/wallpapers \
  -v $(pwd)/backend/thumbnails:/app/backend/thumbnails \
  -v $(pwd)/backend/config.json:/app/backend/config.json:ro \
  wallpaper-app
```

### 配置文件

#### config.json
```json
{
  "zhipu_api_key": "your_api_key_here"
}
```

#### 配置优先级
1. 环境变量 `ZHIPU_API_KEY`
2. 配置文件 `config.json`
3. 默认开发密钥（不推荐生产使用）

## 技术栈

- **后端**：Python + Flask
- **AI模型**：智谱GLM-4.5V多模态模型
- **前端**：HTML5 + CSS3 + JavaScript
- **图像处理**：Pillow
- **容器化**：Docker + Docker Compose
- **配置管理**：环境变量 + JSON配置文件

## 更新日志

### v2.1.0 (2024-01-31) - 容器化版本
- 🐳 **新增容器化支持**：Docker和Docker Compose配置
- 🔧 **配置管理优化**：支持环境变量和配置文件
- 🔒 **安全增强**：API密钥不再硬编码，支持灵活配置
- 📦 **部署简化**：一键部署和管理
- 🧪 **本地测试**：提供默认开发密钥用于本地测试

### v2.0.0 (2024-01-31) - AI智能版本
- 🤖 **新增AI图片分析功能**：集成智谱GLM-4.5V模型
- 🏷️ **智能标签系统**：自动生成6个关键词标签
- 📊 **API增强**：返回完整的AI分析结果
- 🖼️ **文件重命名**：根据AI分析结果自动重命名图片
- 📁 **自动分类**：按图片类型创建子目录
- 📉 **智能压缩**：减少图片大小，提高传输效率

### v1.1.0 (2024-01-31)
- ✅ 修复壁纸拉伸问题：添加 `object-fit: cover` 样式
- ✅ 优化标签生成逻辑：移除重复路径信息，标签更简洁
- ✅ 新增缓存清理功能：支持 `/clear-cache` API 清空缓存
- ✅ 改进项目结构：将缓存文件和缩略图目录移至 backend 目录
- ✅ 增强错误处理：改进壁纸设置功能的错误提示

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础壁纸展示功能
- 分类管理
- 响应式设计
- 暗色主题
- 壁纸设置功能
