#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
壁纸管理库后端服务 - 完整版本
"""

import os
import json
import glob
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import hashlib

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置
class Config:
    # 图片存储目录（基于backend目录）
    IMAGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wallpapers')
    # 支持的图片格式
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    # 缩略图缓存目录（基于backend目录）
    THUMBNAIL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thumbnails')
    # 静态文件目录（基于项目根目录）
    STATIC_DIR = os.path.join(ROOT_DIR, 'static')

app = Flask(__name__, static_folder=Config.STATIC_DIR, static_url_path='/static')

# 确保目录存在
os.makedirs(Config.IMAGE_BASE_DIR, exist_ok=True)
os.makedirs(Config.THUMBNAIL_DIR, exist_ok=True)

class WallpaperManager:
    def __init__(self):
        # 使用 backend 目录定义缓存文件的绝对路径
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wallpaper_cache.json')
        self.image_cache = self.load_cache()
    
    def load_cache(self):
        """加载图片缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """保存图片缓存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.image_cache, f, ensure_ascii=False, indent=2)
    
    def clear_cache(self):
        """清空缓存，强制重新扫描"""
        self.image_cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("缓存已清空，下次扫描将重新生成所有数据")
    
    def scan_images(self):
        """扫描所有图片文件"""
        images = []
        
        for root, dirs, files in os.walk(Config.IMAGE_BASE_DIR):
            for file in files:
                if self.is_image_file(file):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, Config.IMAGE_BASE_DIR)
                    
                    # 检查是否需要重新扫描（文件修改时间）
                    file_mtime = os.path.getmtime(file_path)
                    cache_key = relative_path
                    
                    if cache_key in self.image_cache:
                        if self.image_cache[cache_key]['mtime'] == file_mtime:
                            # 使用缓存数据
                            images.append(self.image_cache[cache_key]['data'])
                            continue
                    
                    # 获取图片信息
                    try:
                        img_info = self.get_image_info(file_path, relative_path)
                        if img_info:
                            images.append(img_info)
                            
                            # 更新缓存
                            self.image_cache[cache_key] = {
                                'mtime': file_mtime,
                                'data': img_info
                            }
                    except Exception as e:
                        print(f"处理图片失败: {file_path}, 错误: {e}")
        
        # 保存缓存
        self.save_cache()
        return images
    
    def is_image_file(self, filename):
        """检查是否为支持的图片格式"""
        return any(filename.lower().endswith(ext) for ext in Config.ALLOWED_EXTENSIONS)
    
    def get_image_info(self, file_path, relative_path):
        """获取图片详细信息"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                # 生成唯一ID
                file_hash = self.get_file_hash(file_path)
                
                return {
                    'id': file_hash,
                    'url': f'/images/{relative_path.replace(os.sep, "/")}',
                    'thumbnail': f'/thumbnails/{file_hash}.jpg',
                    'tag': self.extract_tags(relative_path),
                    'width': width,
                    'height': height,
                    'size': os.path.getsize(file_path),
                    'uploaded_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                }
        except Exception as e:
            print(f"读取图片信息失败: {file_path}, 错误: {e}")
            return None
    
    def get_file_hash(self, file_path):
        """生成文件哈希"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def extract_tags(self, relative_path):
        """从路径中提取标签"""
        # 基于文件夹结构生成标签
        path_parts = relative_path.split(os.sep)
        tags = []
        
        # 添加文件夹名作为标签
        for part in path_parts[:-1]:  # 排除文件名
            if part:
                tags.append(part)
        
        # 添加文件名（不含扩展名）作为标签
        filename = path_parts[-1]
        if filename:
            name_without_ext = os.path.splitext(filename)[0]
            if name_without_ext:
                # 只取文件名作为标签，不包含路径信息
                tags.append(name_without_ext)
        
        return '_'.join(tags) if tags else 'uncategorized'
    
    def get_categories(self):
        """获取所有分类信息"""
        all_images = self.scan_images()
        
        # 提取所有标签
        tags = set()
        for img in all_images:
            tag = img.get('tag', 'uncategorized')
            if tag:
                tags.add(tag)
        
        # 按文件夹结构组织分类
        categories = []
        folder_tags = set()
        
        for tag in sorted(tags):
            parts = tag.split('_')
            if len(parts) > 1:
                # 如果是复合标签，添加父级文件夹
                parent_tag = parts[0]
                if parent_tag not in folder_tags:
                    folder_tags.add(parent_tag)
                    categories.append({
                        'id': parent_tag,
                        'name': parent_tag,
                        'type': 'folder',
                        'count': self.get_category_count(parent_tag, all_images)
                    })
            else:
                # 单个标签
                categories.append({
                    'id': tag,
                    'name': tag,
                    'type': 'file',
                    'count': self.get_category_count(tag, all_images)
                })
        
        return categories
    
    def get_category_count(self, category_id, all_images):
        """获取分类中的图片数量"""
        count = 0
        for img in all_images:
            tag = img.get('tag', '')
            if category_id in tag or tag.startswith(category_id + '_'):
                count += 1
        return count

# 全局实例
wallpaper_manager = WallpaperManager()

@app.route('/api')
def api_wallpapers():
    """壁纸API接口"""
    try:
        # 获取参数
        cid = request.args.get('cid', 'all')  # 分类ID
        start = int(request.args.get('start', 0))  # 起始位置
        count = int(request.args.get('count', 30))  # 数量
        
        # 扫描图片
        all_images = wallpaper_manager.scan_images()
        
        # 按分类过滤
        if cid != 'all':
            filtered_images = [
                img for img in all_images 
                if cid in img.get('tag', '') or img.get('tag', '').startswith(cid)
            ]
        else:
            filtered_images = all_images
        
        # 分页
        end = start + count
        paginated_images = filtered_images[start:end]
        
        # 构造响应数据
        result = {
            'code': 200,
            'data': paginated_images,
            'total': len(filtered_images),
            'has_more': end < len(filtered_images)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': []
        }), 500

@app.route('/categories')
def api_categories():
    """获取所有分类"""
    try:
        categories = wallpaper_manager.get_categories()
        
        return jsonify({
            'code': 200,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分类失败: {str(e)}',
            'categories': []
        }), 500

@app.route('/config')
def api_config():
    """获取配置信息"""
    return jsonify({
        'code': 200,
        'config': {
            'image_base_dir': Config.IMAGE_BASE_DIR,
            'thumbnail_dir': Config.THUMBNAIL_DIR,
            'allowed_extensions': list(Config.ALLOWED_EXTENSIONS)
        }
    })

@app.route('/clear-cache')
def api_clear_cache():
    """清空缓存并重新扫描"""
    try:
        wallpaper_manager.clear_cache()
        return jsonify({
            'code': 200,
            'message': '缓存已清空，下次访问将重新生成'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'清空缓存失败: {str(e)}'
        }), 500

@app.route('/')
def index():
    """提供前端页面"""
    # 使用 ROOT_DIR 来提供 index.html
    return send_from_directory(ROOT_DIR, 'index.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    """提供图片文件"""
    return send_from_directory(Config.IMAGE_BASE_DIR, filename)

@app.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    """动态生成并提供缩略图"""
    import io
    from flask import Response
    
    # 提取文件哈希
    if not filename.endswith('.jpg'):
        return "Invalid thumbnail format", 400
    
    file_hash = filename[:-4]  # 去掉.jpg后缀
    
    # 在缓存中查找对应的原图路径
    for cache_key, cache_data in wallpaper_manager.image_cache.items():
        if cache_data['data']['id'] == file_hash:
            # 找到对应的原图 - 正确处理Windows路径分隔符
            # cache_key已经是相对路径格式，直接使用
            original_path = os.path.join(Config.IMAGE_BASE_DIR, cache_key)
            
            if os.path.exists(original_path):
                try:
                    # 使用PIL生成缩略图
                    with Image.open(original_path) as img:
                        # 保持宽高比，设置最大尺寸
                        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                        
                        # 转换为JPEG格式并返回
                        buffer = io.BytesIO()
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(buffer, format='JPEG', quality=85)
                        buffer.seek(0)
                        
                        return Response(
                            buffer.getvalue(),
                            mimetype='image/jpeg',
                            headers={
                                'Cache-Control': 'public, max-age=31536000',  # 缓存1年
                                'ETag': f'"{file_hash}"'
                            }
                        )
                except Exception as e:
                    print(f"生成缩略图失败: {e}")
                    break
    
    # 如果找不到原图，返回404
    return "Thumbnail not found", 404


@app.route('/set-wallpaper', methods=['POST'])
def api_set_wallpaper():
    """设置桌面壁纸API"""
    try:
        from flask import request
        
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据格式错误'
            }), 400
            
        image_url = data.get('url')
        
        if not image_url:
            return jsonify({
                'code': 400,
                'message': '缺少图片URL参数'
            }), 400
        
        # 调试：打印接收到的URL
        print(f"收到的图片URL: {image_url}")
        
        # 将URL转换为本地路径
        if image_url.startswith('/images/'):
            # 提取相对路径
            relative_path = image_url[len('/images/'):]
            # 转换为本地文件路径
            local_path = os.path.join(Config.IMAGE_BASE_DIR, relative_path.replace('/', os.sep))
            
            print(f"转换后的本地路径: {local_path}")
            print(f"文件是否存在: {os.path.exists(local_path)}")
            
            if os.path.exists(local_path):
                success, message = set_wallpaper(local_path)
                if success:
                    return jsonify({
                        'code': 200,
                        'message': message
                    })
                else:
                    return jsonify({
                        'code': 500,
                        'message': message
                    }), 500
            else:
                return jsonify({
                    'code': 404,
                    'message': f'图片文件不存在: {local_path}'
                }), 404
        else:
            return jsonify({
                'code': 400,
                'message': f'不支持的图片URL格式: {image_url}'
            }), 400
            
    except Exception as e:
        print(f"设置壁纸API错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'设置壁纸失败: {str(e)}'
        }), 500

def set_wallpaper(image_path):
    """设置桌面壁纸（Windows系统）"""
    try:
        import ctypes
        from ctypes import wintypes
        import os
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return False, f"图片文件不存在: {image_path}"
        
        # 检查文件是否可读
        if not os.access(image_path, os.R_OK):
            return False, f"图片文件不可读: {image_path}"
        
        # Windows API 常量
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        
        # 确保路径是绝对路径且使用正确的分隔符
        abs_path = os.path.abspath(image_path)
        
        print(f"尝试设置壁纸: {abs_path}")
        print(f"文件存在: {os.path.exists(abs_path)}")
        print(f"文件大小: {os.path.getsize(abs_path) if os.path.exists(abs_path) else 'N/A'}")
        
        # 调用Windows API设置壁纸
        user32 = ctypes.windll.user32
        result = user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        
        if result:
            print("Windows API调用成功")
            return True, "壁纸设置成功"
        else:
            error_code = ctypes.GetLastError()
            print(f"Windows API调用失败，错误代码: {error_code}")
            return False, f"Windows API调用失败，错误代码: {error_code}"
            
    except ImportError:
        print("导入错误: 需要在Windows系统上运行")
        return False, "需要在Windows系统上运行"
    except Exception as e:
        print(f"设置壁纸异常: {str(e)}")
        return False, f"设置壁纸失败: {str(e)}"

if __name__ == '__main__':
    print("壁纸管理库后端服务启动中...")
    print(f"图片目录: {Config.IMAGE_BASE_DIR}")
    print(f"缩略图目录: {Config.THUMBNAIL_DIR}")
    print("访问 http://localhost:5000/ 查看前端")
    print("访问 http://localhost:5000/api 测试API")
    print("访问 http://localhost:5000/categories 测试分类")
    app.run(host='0.0.0.0', port=5000, debug=True)