#!/usr/bin/env python3
"""
LLM Inline - OpenAI-compatible command line LLM interface

Usage: llmi ask "your question here" [--file file_path]
"""

import os
import sys
import json
import subprocess
import requests
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


def get_skills_dir() -> Path:
    """获取用户技能目录"""
    return Path.home() / ".llm-inline" / "skills"


def load_skill(skill_name: str) -> dict:
    """加载技能配置"""
    skills_dir = get_skills_dir()
    skill_dir = skills_dir / skill_name
    config_file = skill_dir / "skill.json"
    
    if not config_file.exists():
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def list_skills() -> list:
    """列出所有已安装的技能"""
    skills_dir = get_skills_dir()
    if not skills_dir.exists():
        return []
    
    skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            config = load_skill(skill_dir.name)
            if config:
                skills.append(config)
    return skills


def install_skill_from_url(url: str) -> bool:
    """从URL安装技能"""
    try:
        print(f"📥 正在下载技能配置: {url}")
        
        # 处理file://协议
        if url.startswith('file://'):
            file_path = url[7:]  # 移除file://
            if not os.path.exists(file_path):
                print(f"❌ 文件不存在: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
        
        # 尝试解析JSON
        try:
            config = json.loads(content)
        except json.JSONDecodeError:
            print("❌ 下载的文件不是有效的JSON格式")
            return False
        
        # 验证必要字段
        required_fields = ['name', 'description', 'version']
        for field in required_fields:
            if field not in config:
                print(f"❌ 技能配置缺少必要字段: {field}")
                return False
        
        skill_name = config['name']
        skills_dir = get_skills_dir()
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存配置文件
        config_file = skill_dir / "skill.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 下载处理脚本（如果有）
        if 'handler' in config:
            # 构建handler URL
            if url.startswith('file://'):
                # 对于file://，使用配置文件的目录
                base_path = os.path.dirname(url[7:])
                handler_path = os.path.join(base_path, config['handler'])
                handler_url = f"file://{handler_path}"
            else:
                # 对于HTTP(S) URLs，正常拼接
                handler_url = url.rsplit('/', 1)[0] + '/' + config['handler']
                
            try:
                print(f"📥 正在下载处理脚本: {handler_url}")
                
                # 处理file://协议
                if handler_url.startswith('file://'):
                    handler_file_path = handler_url[7:]  # 移除file://
                    if not os.path.exists(handler_file_path):
                        print(f"❌ 处理脚本文件不存在: {handler_file_path}")
                        return False
                    
                    with open(handler_file_path, 'r', encoding='utf-8') as f:
                        handler_content = f.read()
                else:
                    handler_response = requests.get(handler_url, timeout=30)
                    handler_response.raise_for_status()
                    handler_content = handler_response.text
                
                handler_file = skill_dir / config['handler']
                with open(handler_file, 'w', encoding='utf-8') as f:
                    f.write(handler_content)
                
                # 使脚本可执行
                os.chmod(handler_file, 0o755)
                
            except Exception as e:
                print(f"⚠️ 下载处理脚本失败: {e}")
        
        print(f"✅ 技能 '{skill_name}' 安装成功!")
        return True
        
    except Exception as e:
        print(f"❌ 安装技能失败: {e}")
        return False


def execute_skill(skill_name: str, args: list) -> bool:
    """执行技能"""
    config = load_skill(skill_name)
    if not config:
        print(f"❌ 技能 '{skill_name}' 不存在")
        return False
    
    try:
        skill_dir = get_skills_dir() / skill_name
        
        # 检查是否有处理脚本
        if 'handler' in config:
            handler_file = skill_dir / config['handler']
            if handler_file.exists():
                # 动态导入并执行Python脚本
                sys.path.insert(0, str(skill_dir))
                try:
                    module_name = config['handler'].replace('.py', '')
                    module = __import__(module_name)
                    
                    # 注入LLM运行时环境
                    import llmi_runtime
                    
                    # 调用main函数
                    if hasattr(module, 'main'):
                        result = module.main(args)
                        return result if isinstance(result, bool) else True
                    else:
                        print(f"❌ 技能脚本缺少main函数")
                        return False
                        
                except ImportError as e:
                    print(f"❌ 导入技能脚本失败: {e}")
                    return False
                except Exception as e:
                    print(f"❌ 执行技能脚本失败: {e}")
                    return False
                finally:
                    # 清理sys.path
                    if str(skill_dir) in sys.path:
                        sys.path.remove(str(skill_dir))
            else:
                print(f"❌ 技能处理脚本不存在: {config['handler']}")
                return False
        else:
            # 没有处理脚本，显示技能信息
            print(f"📋 技能: {config['name']}")
            print(f"📝 描述: {config['description']}")
            print(f"📦 版本: {config['version']}")
            if 'parameters' in config:
                print("📥 参数:")
                for param in config['parameters']:
                    required = "必需" if param.get('required', False) else "可选"
                    default = f" (默认: {param['default']})" if 'default' in param else ""
                    print(f"  - {param['name']}: {param['description']} [{required}]{default}")
            return True
            
    except Exception as e:
        print(f"❌ 执行技能失败: {e}")
        return False


def ensure_llm_env() -> None:
    """检查必要的环境变量是否存在，不存在则提示后退出"""
    required_vars = ['LLM_API_KEY', 'LLM_BASE_URL', 'LLM_MODEL_NAME']
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"❌ 缺少必要环境变量: {', '.join(missing)}")
        print("请先运行: source llm-switch 并确保已设置 LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME")
        sys.exit(2)


def main():
    import sys
    
    # 检查是否有参数
    if len(sys.argv) < 2:
        print("❌ 请提供问题或指令")
        print("Usage:")
        print("  llmi \"your question here\" [--file file_path]  # 询问问题")
        print("  llmi ask \"your question here\" [--file file_path]  # 询问问题(兼容模式)")
        print("  llmi install <url>  # 安装技能")
        print("  llmi list  # 列出已安装的技能")
        print("  llmi use <tool> [args]  # 使用工具")
        print("  llmi translate <file> [args]  # 翻译文件")
        sys.exit(1)
    
    # 获取所有参数
    args = sys.argv[1:]
    
    # 检查第一个参数是否是'ask'指令
    first_arg = args[0]
    
    if first_arg == 'ask':
        # 兼容模式的ask指令
        if len(args) < 2:
            print("❌ ask指令需要提供问题")
            print("Usage: llmi ask \"your question here\" [--file file_path]")
            sys.exit(1)
        
        # 将剩余参数合并为问题
        user_input = " ".join(args[1:]).strip()
        
        file_path = None
        # 检查是否有--file参数
        if '--file' in args or '-f' in args:
            try:
                file_index = args.index('--file') if '--file' in args else args.index('-f')
                if file_index + 1 < len(args):
                    file_path = args[file_index + 1]
                    # 从user_input中移除--file和file_path
                    file_part = f"--file {file_path}" if '--file' in args else f"-f {file_path}"
                    user_input = user_input.replace(file_part, "").strip()
            except ValueError:
                pass
    elif first_arg in ['use', 'translate', 'list', 'install']:
        # 技能相关指令
        if first_arg == 'install':
            # 安装技能
            if len(args) < 2:
                print("❌ install指令需要提供技能URL")
                print("Usage: llmi install <skill_url>")
                sys.exit(1)
            
            skill_url = args[1]
            success = install_skill_from_url(skill_url)
            sys.exit(0 if success else 1)
            
        elif first_arg == 'list':
            # 列出已安装的技能
            skills = list_skills()
            if not skills:
                print("📂 暂无已安装的技能")
                print("使用 'llmi install <url>' 安装技能")
            else:
                print("📂 已安装的技能:")
                for skill in skills:
                    print(f"  📦 {skill['name']} v{skill['version']}")
                    print(f"     {skill['description']}")
                    if 'author' in skill:
                        print(f"     作者: {skill['author']}")
                    print()
            sys.exit(0)
            
        else:
            # 执行技能
            skill_name = first_arg
            skill_args = args[1:] if len(args) > 1 else []
            
            # 检查技能是否存在
            if not load_skill(skill_name):
                print(f"❌ 技能 '{skill_name}' 不存在")
                print("使用 'llmi list' 查看已安装的技能")
                print("使用 'llmi install <url>' 安装新技能")
                sys.exit(1)
            
            # 执行技能
            success = execute_skill(skill_name, skill_args)
            sys.exit(0 if success else 1)
            
    else:
        # 默认行为：将所有参数作为问题处理
        user_input = " ".join(args).strip()
        file_path = None
        
        # 检查是否有--file参数
        if '--file' in args or '-f' in args:
            try:
                file_index = args.index('--file') if '--file' in args else args.index('-f')
                if file_index + 1 < len(args):
                    file_path = args[file_index + 1]
                    # 从user_input中移除--file和file_path
                    file_part = f"--file {file_path}" if '--file' in args else f"-f {file_path}"
                    user_input = user_input.replace(file_part, "").strip()
            except ValueError:
                pass
    
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