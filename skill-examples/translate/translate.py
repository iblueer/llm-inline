#!/usr/bin/env python3
"""
翻译技能处理脚本
使用LLM翻译文件内容
"""

import os
import sys
import json
from pathlib import Path


def main(args):
    """翻译技能的主函数"""
    try:
        from openai import OpenAI
        
        # 解析参数
        if len(args) == 0:
            print("❌ 请提供要翻译的文件")
            print("Usage: llmi translate <file> [target_lang] [source_lang]")
            return False
        
        file_path = args[0]
        target_lang = args[1] if len(args) > 1 else "en"
        source_lang = args[2] if len(args) > 2 else None
        
        # 检查文件
        abs_path = Path(file_path).expanduser().resolve()
        if not abs_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        if not abs_path.is_file():
            print(f"❌ 路径不是文件: {file_path}")
            return False
        
        # 读取文件内容
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print("❌ 不支持翻译二进制文件")
            return False
        
        if not content.strip():
            print("⚠️ 文件内容为空")
            return True
        
        # 检查LLM环境
        if not os.environ.get('LLM_API_KEY') or not os.environ.get('LLM_BASE_URL'):
            print("❌ 缺少LLM环境变量，请先运行: source llm-switch")
            return False
        
        print(f"🔍 正在翻译文件: {abs_path.name}")
        print(f"🌐 目标语言: {target_lang}")
        if source_lang:
            print(f"🌐 源语言: {source_lang}")
        print()
        
        # 构建翻译提示
        if source_lang:
            prompt = f"请将以下{source_lang}内容翻译成{target_lang}，保持原文格式：\n\n{content}"
        else:
            prompt = f"请将以下内容翻译成{target_lang}，保持原文格式：\n\n{content}"
        
        # 调用LLM
        client = OpenAI(
            api_key=os.environ.get('LLM_API_KEY'),
            base_url=os.environ.get('LLM_BASE_URL')
        )
        
        response = client.chat.completions.create(
            model=os.environ.get('LLM_MODEL_NAME', 'doubao-seed-1.6-flash'),
            messages=[
                {"role": "system", "content": "你是一个专业的翻译助手，请准确翻译用户提供的文本，保持原有的格式和结构。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.3
        )
        
        translation = response.choices[0].message.content
        
        print("📝 翻译结果:")
        print("=" * 50)
        print(translation)
        print("=" * 50)
        
        # 保存翻译结果
        output_path = abs_path.parent / f"{abs_path.stem}_{target_lang}{abs_path.suffix}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translation)
        
        print(f"\n✅ 翻译完成，结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 翻译失败: {e}")
        return False


if __name__ == "__main__":
    main(sys.argv[1:])
