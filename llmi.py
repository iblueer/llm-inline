#!/usr/bin/env python3
"""
LLM Inline - OpenAI-compatible command line LLM interface

Usage: llmi ask "your question here" [--file file_path]
"""

import os
import sys
import json
import subprocess
import argparse
from openai import OpenAI
from pathlib import Path


def read_file_content(file_path: str) -> dict:
    """
    读取文件内容，返回文件信息字典
    支持相对路径转换
    """
    try:
        # 支持相对路径
        abs_path = Path(file_path).expanduser().resolve()
        
        if not abs_path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        if not abs_path.is_file():
            return {"error": f"路径不是文件: {file_path}"}
        
        # 检查文件大小，避免上传过大文件
        file_size = abs_path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return {"error": f"文件过大，超过10MB限制: {file_path}"}
        
        # 读取文件内容
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            is_binary = False
        except (UnicodeDecodeError, Exception):
            # 如果是二进制文件，读取为base64
            import base64
            with open(abs_path, 'rb') as f:
                binary_content = f.read()
            content = base64.b64encode(binary_content).decode('utf-8')
            is_binary = True
        
        return {
            "success": True,
            "path": str(abs_path),
            "filename": abs_path.name,
            "content": content,
            "size": file_size,
            "is_binary": is_binary
        }
        
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}


def get_shell_info():
    """获取当前shell环境和目录信息"""
    shell = os.environ.get('SHELL', '/bin/sh')
    current_dir = os.getcwd()
    return {
        "shell": shell,
        "current_directory": current_dir
    }


def create_structured_prompt(user_input: str, shell_info: dict, file_info: dict = None) -> list:
    """
    创建结构化的提示信息
    要求LLM以特定格式返回可直接使用的命令
    """
    
    # 构建系统提示
    system_prompt = f"""你是一个命令行助手，帮助用户解决shell命令相关问题。

当前环境:
- Shell: {shell_info['shell']}
- 当前目录: {shell_info['current_directory']}"""

    # 如果有文件附件，添加文件信息
    if file_info and file_info.get('success'):
        file_info_text = f"""

文件附件信息:
- 文件名: {file_info['filename']}
- 文件路径: {file_info['path']}
- 文件大小: {file_info['size']} bytes
- 是否为二进制文件: {'是' if file_info['is_binary'] else '否'}
- 文件内容: 
{file_info['content'] if not file_info['is_binary'] else '[二进制内容，已编码为base64]'}"""
        
        system_prompt += file_info_text
    
    system_prompt += """

如果用户的问题是关于如何输入bash/zsh命令的，你必须以以下格式返回可以直接使用的命令:
```command
具体的命令内容
```

如果问题不涉及命令，则正常回答即可。

要求:
1. 对于需要命令的问答，必须使用上面的格式将命令包裹在```command代码块中。

示例:
用户: "怎么列出当前目录下的所有文件,并且能看到每个文件的扩展名和文件大小?"

你的回答应该是:
```command
ls -l
```
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    return messages


def call_llm(messages: list) -> str:
    """调用OpenAI兼容的API"""
    try:
        client = OpenAI(
            api_key=os.environ.get('LLM_API_KEY'),
            base_url=os.environ.get('LLM_BASE_URL')
        )

        # 构建API参数
        api_params = {
            "model": os.environ.get('LLM_MODEL_NAME', 'doubao-seed-1.6-flash'),
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.3
        }

        # 如果有文件附件，直接在系统提示中包含文件内容（不使用image_url格式）
        # 我们已经在create_structured_prompt中处理了文件内容
        # 这里不再需要特殊处理

        response = client.chat.completions.create(**api_params)

        return response.choices[0].message.content

    except Exception as e:
        return f"Error calling LLM: {str(e)}"


def extract_command(llm_response: str) -> str:
    """
    从LLM响应中提取命令
    如果找到```command代码块，返回其中的命令内容
    """
    import re

    # 匹配```command代码块
    pattern = r'```command\s*\n(.*?)\n```'
    match = re.search(pattern, llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def ensure_llm_env() -> None:
    """检查必要的环境变量是否存在，不存在则提示后退出"""
    required_vars = ['LLM_API_KEY', 'LLM_BASE_URL', 'LLM_MODEL_NAME']
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"❌ 缺少必要环境变量: {', '.join(missing)}")
        print("请先运行: source llm-switch 并确保已设置 LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME")
        sys.exit(2)


def main():
    # 使用argparse解析命令行参数
    parser = argparse.ArgumentParser(
        description='LLM Inline - OpenAI-compatible command line LLM interface'
    )
    parser.add_argument('ask', help='Ask a question to LLM')
    parser.add_argument('question', nargs='*', help='Your question to the LLM')
    parser.add_argument('--file', '-f', help='File path to attach to the query')
    
    args = parser.parse_args()
    
    # 检查是否有问题
    if not args.question:
        print("❌ 请提供问题")
        print("Usage: llmi ask \"your question here\" [--file file_path]")
        sys.exit(1)
    
    user_input = " ".join(args.question).strip()
    file_path = args.file
    
    print(f"🤔 用户提问: {user_input}")
    if file_path:
        print(f"📎 附件文件: {file_path}")
    print()

    # 获取shell信息
    shell_info = get_shell_info()
    
    # 处理文件附件
    file_info = None
    if file_path:
        print("📂 正在读取文件...")
        file_info = read_file_content(file_path)
        if file_info.get('error'):
            print(f"❌ {file_info['error']}")
            sys.exit(1)
        print(f"✅ 文件读取成功: {file_info['filename']} ({file_info['size']} bytes)")
        print()

    # 创建结构化提示
    messages = create_structured_prompt(user_input, shell_info, file_info)

    # 确保环境
    ensure_llm_env()

    # 调用LLM
    print("🧠 正在思考...")
    llm_response = call_llm(messages)

    if llm_response.startswith("Error"):
        print(f"{llm_response}")
        sys.exit(1)

    # 提取命令
    command = extract_command(llm_response)

    print("\n💡 LLM回答:")
    print(llm_response)
    print()

    # 如果有命令，提示用户可以使用
    if command:
        print("=" * 50)
        print("📋 建议命令:")
        print(command)
        print("\n💡 提示: 您可以使用Tab键快速粘贴此命令")

        # 将命令缓存到文件，供 shell 按键绑定读取
        try:
            cache_dir = Path(os.path.expanduser("~/.cache/llmi"))
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / "last_command").write_text(command + "\n", encoding="utf-8")
        except Exception as _:
            pass

    return command


if __name__ == "__main__":
    main()