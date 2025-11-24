# 技能示例

本目录包含llm-inline技能的开发示例，展示如何创建和分发技能。

## 🎯 设计理念

**技能完全依赖llmi的基础设施**

llm-inline采用插件架构，让技能开发者专注于业务逻辑，无需关心LLM接入细节：

- **llmi负责LLM接入**: 统一处理API密钥、模型选择、网络连接等
- **技能专注功能**: 开发者只需实现具体的prompt处理和业务逻辑  
- **环境共享**: 所有技能共享同一套LLM环境变量
- **简化开发**: 大幅降低技能开发门槛

## 技能结构

每个技能通常包含：

```
skill-name/
├── skill.json    # 技能配置文件
└── handler.py     # 处理脚本（可选）
```

## translate 技能示例

`translate/` 目录是一个完整的翻译技能示例：

### 安装示例
```bash
# 从本目录安装（测试用）
llmi install file:///path/to/llm-inline/skill-examples/translate/skill.json

# 从GitHub安装（生产用）
llmi install https://raw.githubusercontent.com/iblueer/llm-inline/main/skill-examples/translate/skill.json
```

### 使用方法
```bash
# 翻译为英文
llmi translate document.txt en

# 翻译为日文
llmi translate document.txt ja

# 指定源语言
llmi translate document.txt fr en
```

### 技能配置说明

**skill.json** 字段说明：
- `name`: 技能名称（必须唯一）
- `description`: 技能描述
- `version`: 版本号
- `author`: 作者信息
- `parameters`: 参数定义数组
- `handler`: 处理脚本文件名

**参数类型**：
- `file`: 文件路径
- `string`: 字符串
- `number`: 数字
- `boolean`: 布尔值

## 开发自己的技能

### 1. 创建技能目录
```bash
mkdir my-skill
cd my-skill
```

### 2. 编写 skill.json 配置
定义技能的基本信息和参数结构。

### 3. 实现 handler.py 处理脚本
**关键原则：完全依赖llmi运行时环境**

```python
#!/usr/bin/env python3

def main(args):
    # 导入llmi运行时API
    import llmi_runtime
    
    # 解析参数（文件可能已由llmi预处理）
    file_param = args[0]
    target_lang = args[1] if len(args) > 1 else "en"
    
    # 获取文件内容（llmi统一处理）
    file_info = llmi_runtime.get_file_content(file_param)
    if 'error' in file_info:
        print(f"❌ {file_info['error']}")
        return False
    
    content = file_info['content']
    
    # 构建业务prompt
    prompt = f"请将以下内容翻译成{target_lang}：\n\n{content}"
    
    # 通过llmi调用LLM（完全透明！）
    translation = llmi_runtime.call_llm(
        prompt,
        system_prompt="你是一个专业的翻译助手，请准确翻译用户提供的文本，保持原有的格式和结构。"
    )
    
    print(translation)
    return True
```

**架构优势**：
- **文件统一处理**: llmi自动处理文件I/O、编码检测、大小限制
- **零配置代码**: 技能无需检查环境变量或初始化客户端
- **统一接口**: 所有技能使用相同的 `llmi_runtime.call_llm()` 
- **参数透传**: `max_tokens`, `temperature` 等参数可直接传递
- **环境透明**: 完全不知道LLM来源，只管调用

### 4. 上传到GitHub并分享
将技能上传到GitHub，用户就可以通过以下方式安装：

```bash
llmi install https://raw.githubusercontent.com/username/repo/main/skill-name/skill.json
```

### ✅ 开发优势
- **零配置代码**: 无需处理API密钥、模型选择、环境检查
- **透明LLM接口**: 调用 `llmi_runtime.call_llm()` 即可
- **统一体验**: 所有技能使用相同的LLM后端和配置
- **环境安全**: llmi统一管理敏感信息，技能无权限问题
- **极简开发**: 专注业务逻辑，5分钟即可完成技能
- **参数透传**: `max_tokens`, `temperature` 等LLM参数可直接传递

## 分享技能

将技能上传到GitHub，用户就可以通过以下方式安装：

```bash
llmi install https://raw.githubusercontent.com/username/repo/main/skill-name/skill.json
```

建议在README中包含完整的使用说明和示例。
