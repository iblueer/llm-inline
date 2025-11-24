# 技能示例

本目录包含llm-inline技能的开发示例，展示如何创建和分发技能。

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

1. 创建技能目录
2. 编写 `skill.json` 配置
3. 实现 `handler.py` 处理脚本
4. 上传到GitHub并分享raw link
5. 用户可通过 `llmi install <url>` 安装

处理脚本的 `main(args)` 函数会接收到命令行参数数组，成功时返回 `True`，失败时返回 `False`。

## 分享技能

将技能上传到GitHub，用户就可以通过以下方式安装：

```bash
llmi install https://raw.githubusercontent.com/username/repo/main/skill-name/skill.json
```

建议在README中包含完整的使用说明和示例。
