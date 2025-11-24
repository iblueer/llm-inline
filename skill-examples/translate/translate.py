#!/usr/bin/env python3
"""
翻译技能处理脚本
专注于业务逻辑，LLM接入完全交给llmi
"""

import sys
from pathlib import Path


def main(args):
    """翻译技能的主函数"""
    # 导入llmi运行时API
    import llmi_runtime
    
    try:
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
        
        print(f"🔍 正在翻译文件: {abs_path.name}")
        print(f"🌐 目标语言: {target_lang}")
        if source_lang:
            print(f"🌐 源语言: {source_lang}")
        print()
        
        # 构建翻译prompt（纯业务逻辑）
        if source_lang:
            prompt = f"请将以下{source_lang}内容翻译成{target_lang}，保持原文格式：\n\n{content}"
        else:
            prompt = f"请将以下内容翻译成{target_lang}，保持原文格式：\n\n{content}"
        
        # 通过llmi调用LLM（完全透明！）
        system_prompt = "你是一个专业的翻译助手，请准确翻译用户提供的文本，保持原有的格式和结构。"
        translation = llmi_runtime.call_llm(prompt, system_prompt)
        
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
