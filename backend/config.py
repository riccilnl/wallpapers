#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
支持环境变量和配置文件
"""

import os
import json
from pathlib import Path

class Config:
    """配置管理类"""
    
    def __init__(self):
        # 项目根目录
        self.ROOT_DIR = Path(__file__).parent.parent
        
        # 图片存储目录（基于backend目录）
        self.IMAGE_BASE_DIR = Path(__file__).parent / 'wallpapers'
        
        # 支持的图片格式
        self.ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
        # 缩略图缓存目录（基于backend目录）
        self.THUMBNAIL_DIR = Path(__file__).parent / 'thumbnails'
        
        # 静态文件目录（基于项目根目录）
        self.STATIC_DIR = self.ROOT_DIR / 'static'
        
        # AI配置
        self.ZHIPU_API_KEY = self._get_zhipu_api_key()
        self.ZHIPU_API_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        # 确保目录存在
        self._create_directories()
    
    def _get_zhipu_api_key(self):
        """获取智谱API密钥"""
        # 优先从环境变量获取
        api_key = os.environ.get('ZHIPU_API_KEY')
        if api_key:
            return api_key
        
        # 其次从配置文件获取
        config_file = Path(__file__).parent / 'config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('zhipu_api_key')
            except (json.JSONDecodeError, KeyError):
                pass
        
        # 最后使用默认值（仅用于开发环境）
        return "your_api_key_here"
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.IMAGE_BASE_DIR,
            self.THUMBNAIL_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
    
    def get_flask_config(self):
        """获取Flask配置"""
        return {
            'IMAGE_BASE_DIR': str(self.IMAGE_BASE_DIR),
            'THUMBNAIL_DIR': str(self.THUMBNAIL_DIR),
            'STATIC_DIR': str(self.STATIC_DIR),
            'ALLOWED_EXTENSIONS': list(self.ALLOWED_EXTENSIONS)
        }

# 全局配置实例
config = Config()