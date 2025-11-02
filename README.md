# 壁纸管理库

一个基于Python Flask的局域网壁纸管理服务，可以自动扫描本地图片文件并提供Web界面浏览。

## 文件结构

```
wallpaper-main/
├── backend/
│   ├── app.py           # 主程序文件
│   ├── requirements.txt # 依赖包列表
│   ├── wallpapers/      # 图片存储目录
│   ├── thumbnails/      # 缩略图缓存目录
│   └── wallpaper_cache.json # 缓存文件
├── static/              # 前端静态文件目录
├── index.html           # 前端主页面
└── README.md           # 说明文档
```

## 安装和运行

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务
```bash
cd backend
python app.py
```

### 3. 访问服务
打开浏览器访问：`http://localhost:5000` 或你的局域网IP地址

## API接口

### 获取壁纸列表
```
GET /api?cid=分类ID&start=起始位置&count=数量
```

**参数说明：**
- `cid`: 分类ID（可选，默认为'all'）
- `start`: 起始位置（可选，默认为0）
- `count`: 每页数量（可选，默认为30）

**响应格式：**
```json
{
  "code": 200,
  "data": [
    {
      "id": "图片唯一ID",
      "url": "图片URL",
      "thumbnail": "缩略图URL",
      "tag": "标签",
      "width": 1920,
      "height": 1080,
      "size": 1024000,
      "uploaded_at": "2023-01-01T12:00:00"
    }
  ],
  "total": 100,
  "has_more": true
}
```

### 获取分类列表
```
GET /categories
```

### 获取配置信息
```
GET /config
```

## 使用说明

1. **添加图片**：将图片文件放入 `backend/wallpapers/` 目录或其子目录中
2. **自动分类**：系统会根据文件夹结构自动分类
3. **缓存机制**：首次扫描后会生成缓存，提高加载速度
4. **缩略图**：动态生成缩略图，不占用额外存储空间

## 配置

在 `backend/app.py` 中可以修改以下配置：

```python
class Config:
    IMAGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wallpapers')  # 图片存储目录
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}  # 支持的格式
```

## 前端适配

API地址已正确配置，无需修改。

## 目录结构优化

现在项目的目录结构更加合理：
- `backend/wallpapers/` - 专门存放壁纸图片
- `backend/thumbnails/` - 存放生成的缩略图
- `static/` - 存放前端静态文件
- `index.html` - 前端主页面
- 根目录只保留配置文件和文档

这样避免了资源重复，提高了项目的组织性。

## 更新日志

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
