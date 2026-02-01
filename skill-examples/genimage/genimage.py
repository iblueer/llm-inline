#!/usr/bin/env python3
"""
图像生成技能处理脚本
使用llm-switch设置的Vision模型（如gemini-3-pro-image）生成图像
支持传入比例参数
"""

import sys
import os
import base64
from pathlib import Path
from datetime import datetime


# 比例到尺寸的映射
RATIO_TO_SIZE = {
    "1:1": "1024x1024",
    "16:9": "1280x720",
    "9:16": "720x1280",
    "4:3": "1216x896",
    "3:4": "896x1216",
}


def main(args):
    """图像生成技能的主函数"""
    # 导入llmi运行时API
    import llmi_runtime
    
    try:
        # 解析参数
        if len(args) == 0:
            print("❌ 请提供图像生成提示词")
            print("Usage: llmi genimage \"你的提示词\" [ratio] [output_path]")
            print()
            print("支持的比例参数:")
            for ratio, size in RATIO_TO_SIZE.items():
                print(f"  {ratio} -> {size}")
            return False
        
        # 获取提示词
        prompt = args[0]
        
        # 获取比例参数（默认1:1）
        ratio = args[1] if len(args) > 1 else "1:1"
        
        # 转换比例为尺寸
        if ratio in RATIO_TO_SIZE:
            size = RATIO_TO_SIZE[ratio]
        elif "x" in ratio:
            # 直接传入尺寸格式 如 "1024x1024"
            size = ratio
        else:
            print(f"⚠️ 未知比例 '{ratio}'，使用默认1:1 (1024x1024)")
            size = "1024x1024"
        
        # 获取输出路径
        if len(args) > 2:
            output_path = Path(args[2]).expanduser().resolve()
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path.cwd() / f"generated_{timestamp}.png"
        
        print("🎨 图像生成技能")
        print("=" * 60)
        print(f"📝 提示词: {prompt}")
        print(f"📐 比例: {ratio} ({size})")
        print(f"📁 输出路径: {output_path}")
        print("=" * 60)
        print()
        
        # 通过llmi调用Vision LLM生成图像
        print("🔧 正在调用Vision模型生成图像...")
        print()
        
        # 调用Vision模型（使用vision_call_llm）
        result = llmi_runtime.vision_call_llm(
            prompt=prompt,
            size=size
        )
        
        # 解析结果
        if isinstance(result, dict):
            if 'error' in result:
                print(f"❌ 生成失败: {result['error']}")
                return False
            
            # 如果返回了图像数据
            if 'image_data' in result:
                image_data = base64.b64decode(result['image_data'])
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"✅ 图像已保存到: {output_path}")
                return True
            
            # 如果返回了图像URL
            if 'image_url' in result:
                print(f"🔗 图像URL: {result['image_url']}")
                # 尝试下载图像
                try:
                    import requests
                    response = requests.get(result['image_url'], timeout=30)
                    response.raise_for_status()
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ 图像已保存到: {output_path}")
                except Exception as e:
                    print(f"⚠️ 下载图像失败: {e}")
                    print(f"   请手动访问上述URL获取图像")
                return True
                
            # 如果返回了文本内容（可能包含Base64图像）
            if 'content' in result:
                content = result['content']
                # 尝试从内容中提取Base64图像
                if extract_and_save_image(content, output_path):
                    print(f"✅ 图像已保存到: {output_path}")
                    return True
                else:
                    print("📝 模型返回:")
                    print(content)
                    return True
        
        # 如果是字符串结果
        if isinstance(result, str):
            # 尝试从内容中提取Base64图像
            if extract_and_save_image(result, output_path):
                print(f"✅ 图像已保存到: {output_path}")
                return True
            else:
                print("📝 模型返回:")
                print(result)
                return True
        
        print(f"⚠️ 未知的返回格式: {type(result)}")
        return True
        
    except Exception as e:
        print(f"❌ 图像生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_and_save_image(content: str, output_path: Path) -> bool:
    """从内容中提取Base64图像并保存"""
    import re
    
    # 尝试匹配常见的Base64图像格式
    patterns = [
        r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)',  # data URL格式
        r'!\[.*?\]\(data:image/[^;]+;base64,([A-Za-z0-9+/=]+)\)',  # Markdown图像
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            try:
                image_data = base64.b64decode(match.group(1))
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return True
            except Exception:
                continue
    
    # 尝试直接解析整个内容为Base64（如果看起来像Base64）
    content_stripped = content.strip()
    if len(content_stripped) > 100 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in content_stripped[:100]):
        try:
            image_data = base64.b64decode(content_stripped)
            # 检查是否是有效的图像（PNG或JPEG魔数）
            if image_data[:8] == b'\x89PNG\r\n\x1a\n' or image_data[:2] == b'\xff\xd8':
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return True
        except Exception:
            pass
    
    return False


if __name__ == "__main__":
    main(sys.argv[1:])
