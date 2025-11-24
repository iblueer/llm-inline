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
**关键原则：完全依赖llmi环境**

```python
#!/usr/bin/env python3
import os

def main(args):
    # 解析参数
    input_file = args[0]
    
    # 构建业务prompt
    prompt = f"请处理这个文件: {input_file}"
    
    # 直接使用llmi提供的LLM环境
    from openai import OpenAI
    client = OpenAI(
        api_key=os.environ.get('LLM_API_KEY'),      # llmi提供
        base_url=os.environ.get('LLM_BASE_URL')      # llmi提供
    )
    
    response = client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),        # llmi提供
        messages=[{"role": "user", "content": prompt}]
    )
    
    print(response.choices[0].message.content)
    return True
```

### 4. 上传到GitHub并分享
将技能上传到GitHub，用户就可以通过以下方式安装：

```bash
llmi install https://raw.githubusercontent.com/username/repo/main/skill-name/skill.json
```

### ✅ 开发优势
- **零配置**: 无需处理API密钥、模型选择
- **统一体验**: 所有技能使用相同的LLM后端
- **环境安全**: llmi统一管理敏感信息
- **快速开发**: 专注业务逻辑，5分钟即可完成技能

## 分享技能

将技能上传到GitHub，用户就可以通过以下方式安装：

```bash
llmi install https://raw.githubusercontent.com/username/repo/main/skill-name/skill.json
```

建议在README中包含完整的使用说明和示例。
