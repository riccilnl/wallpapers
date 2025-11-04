import os
import json
import base64
import shutil
import requests
from PIL import Image, ImageOps
from typing import Dict, Optional, List

# 导入配置
from config import config

# 配置API密钥和端点
API_KEY = config.ZHIPU_API_KEY  # 智谱API密钥
API_ENDPOINT = config.ZHIPU_API_ENDPOINT  # 智谱AI的API端点

def compress_image(image_path: str, max_size_mb: float = 2.0, target_width: int = 800) -> bytes:
    """压缩图片以减少带宽占用"""
    with Image.open(image_path) as img:
        # 检查文件大小
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
        
        # 如果文件小于阈值且尺寸合适，直接返回原图数据
        if file_size <= max_size_mb and img.width <= target_width:
            with open(image_path, 'rb') as f:
                return f.read()
        
        # 保持宽高比缩放
        if img.width > target_width:
            ratio = target_width / img.width
            new_width = target_width
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 转换为RGB模式（处理RGBA等格式）
        if img.mode not in ('RGB', 'L'):
            if img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        
        # 压缩图片
        import io
        output = io.BytesIO()
        
        # 根据原格式选择压缩参数
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            img.save(output, format='JPEG', quality=75, optimize=True)
        elif image_path.lower().endswith('.png'):
            # PNG转JPEG
            img.save(output, format='JPEG', quality=75, optimize=True)
        else:
            img.save(output, format='JPEG', quality=75, optimize=True)
        
        compressed_data = output.getvalue()
        
        # 如果压缩后 still 太大，进一步降低质量
        if len(compressed_data) > max_size_mb * 1024 * 1024:
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=60, optimize=True)
            compressed_data = output.getvalue()
        
        return compressed_data

def encode_image(image_path: str) -> str:
    """将图片文件编码为base64字符串（支持压缩）"""
    # 压缩图片
    compressed_data = compress_image(image_path)
    # 编码为base64
    return base64.b64encode(compressed_data).decode('utf-8')

def analyze_image(image_path: str) -> Dict:
    """调用智谱GLM-4.5V模型API分析图片"""
    # 检查图片格式
    if not (image_path.lower().endswith('.jpg') or 
            image_path.lower().endswith('.jpeg') or 
            image_path.lower().endswith('.png')):
        raise ValueError("不支持的图片格式，请使用JPG或PNG格式的图片")
    
    # 编码图片
    base64_image = encode_image(image_path)
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 构建prompt，告诉模型我们需要什么样的分析结果
    prompt = """
    请分析这张图片，并严格按照以下JSON格式返回结果：
    {
        "type": "图片类型（必须是以下之一：风光、美女、动漫、汽车、城市）",
        "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5", "关键词6"]
    }
    
    注意：
    1. 图片类型必须是"风光"、"美女"、"动漫"、"汽车"、"城市"之一
    2. 关键词应该是描述这张图片的标签词语，比如"黄昏"、"山脉"、"雾气"等
    3. 关键词中不能包含图片类型名称本身（例如如果类型是"动漫"，关键词中就不能出现"动漫"）
    4. 只返回JSON格式的结果，不要包含其他解释或说明
    """
    
    # 构建请求体
    payload = {
        "model": "glm-4.5v",  # 使用GLM-4.5V模型
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2,  # 降低温度以获得更确定的结果
        "max_tokens": 500
    }
    
    # 发送请求
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # 如果请求失败，抛出HTTPError异常
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求失败：{e}")
    
    # 解析响应
    try:
        result = response.json()
    except json.JSONDecodeError:
        raise Exception("API返回的响应不是有效的JSON格式")
    
    # 检查响应中是否包含预期的字段
    if "choices" not in result or len(result["choices"]) == 0:
        raise Exception("API响应中不包含'choices'字段")
    
    if "message" not in result["choices"][0] or "content" not in result["choices"][0]["message"]:
        raise Exception("API响应格式不正确")
    
    # 提取模型返回的内容
    content = result["choices"][0]["message"]["content"]
    
    # 尝试解析JSON
    try:
        # 尝试直接解析整个内容为JSON
        analysis = json.loads(content)
    except json.JSONDecodeError:
        # 如果直接解析失败，尝试提取JSON部分
        try:
            # 查找JSON开始和结束的位置
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                raise Exception("无法从响应中提取JSON")
        except Exception as e:
            raise Exception(f"模型返回的格式不正确，无法解析为JSON：{content}")
    
    # 检查解析结果是否包含所需的字段
    if "type" not in analysis or "keywords" not in analysis:
        raise Exception("模型返回的结果不包含所需的字段")
    
    # 验证图片类型是否合法
    valid_types = ["风光", "美女", "动漫", "汽车", "城市"]
    if analysis["type"] not in valid_types:
        # 如果类型不合法，尝试从内容中推断
        for valid_type in valid_types:
            if valid_type in content:
                analysis["type"] = valid_type
                break
        else:
            analysis["type"] = "风光"  # 默认类型
    
    # 确保至少有六个关键词
    while len(analysis["keywords"]) < 6:
        analysis["keywords"].append("未知")
    
    return analysis

def generate_new_name(analysis: Dict) -> str:
    """根据分析结果生成新的文件名"""
    image_type = analysis.get("type", "风光")
    keywords = analysis.get("keywords", ["未知", "未知", "未知"])
    
    # 只取前六个关键词
    keywords = keywords[:6]
    
    # 生成新文件名
    new_name = f"{image_type}_{keywords[0]}_{keywords[1]}_{keywords[2]}_{keywords[3]}_{keywords[4]}_{keywords[5]}"
    
    return new_name

def save_rename_result(original_name: str, new_name: str, output_file: str = "rename.json"):
    """将重命名结果保存到JSON文件中"""
    result = {
        "原名": original_name,
        "重命名": new_name
    }
    
    # 如果文件已存在，读取现有内容
    existing_results = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                existing_results = json.load(f)
                if not isinstance(existing_results, list):
                    existing_results = [existing_results]
            except json.JSONDecodeError:
                existing_results = []
    
    # 添加新结果
    existing_results.append(result)
    
    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_results, f, ensure_ascii=False, indent=2)

def process_image(image_path: str, output_file: str = "rename.json") -> Optional[str]:
    """处理单个图片文件"""
    try:
        # 分析图片
        analysis = analyze_image(image_path)
        
        # 生成新文件名
        new_name = generate_new_name(analysis)
        
        # 获取原文件名（不含路径）
        original_name = os.path.basename(image_path)
        
        # 获取文件扩展名
        file_ext = os.path.splitext(image_path)[1]
        
        # 构建新的文件路径
        new_file_path = os.path.join(os.path.dirname(image_path), new_name + file_ext)
        
        # 实际重命名文件
        os.rename(image_path, new_file_path)
        
        # 按文件名类型移动到对应文件夹
        move_to_category_folder(new_file_path, new_name, file_ext)
        
        # 保存重命名结果
        save_rename_result(original_name, new_name + file_ext, output_file)
        
        print(f"图片处理完成：{original_name} -> {new_name}{file_ext}")
        
        return new_name + file_ext
    
    except Exception as e:
        print(f"处理图片时出错：{e}")
        return None

def move_to_category_folder(file_path: str, new_name: str, file_ext: str):
    """根据文件名类型将图片移动到对应的分类文件夹"""
    try:
        # 提取文件类型（文件名的第一个部分）
        file_type = new_name.split('_')[0]
        
        # 构建目标文件夹路径
        target_folder = os.path.join(os.path.dirname(file_path), file_type)
        
        # 如果目标文件夹不存在，则创建
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        # 构建目标文件路径
        target_file_path = os.path.join(target_folder, os.path.basename(file_path))
        
        # 移动文件
        shutil.move(file_path, target_file_path)
        
        print(f"图片已移动到分类文件夹：{file_type}/")
        
    except Exception as e:
        print(f"移动文件到分类文件夹时出错：{e}")

def process_directory(directory: str, output_file: str = "rename.json"):
    """处理目录中的所有图片文件"""
    if not os.path.isdir(directory):
        print(f"目录不存在：{directory}")
        return
    
    # 支持的图片格式
    supported_extensions = (".jpg", ".jpeg", ".png")
    
    # 遍历目录中的文件
    for filename in os.listdir(directory):
        if filename.lower().endswith(supported_extensions):
            image_path = os.path.join(directory, filename)
            process_image(image_path, output_file)

def main():
    """主函数"""
    # 示例用法
    
    # 1. 处理单个图片
    image_path = "example.jpg"  # 替换为你要处理的图片路径
    if os.path.exists(image_path):
        process_image(image_path)
    else:
        print(f"图片文件不存在：{image_path}")
    
    # 2. 处理目录中的所有图片
    directory_path = "wallpapers"  # 替换为包含图片的目录路径
    if os.path.exists(directory_path):
        process_directory(directory_path)
    else:
        print(f"目录不存在：{directory_path}")

if __name__ == "__main__":
    main()