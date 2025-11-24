# LLM Inline

OpenAI-compatible command line LLM interface powered by llm-switch environment variables.

## Installation

### Online Installation (Recommended)
```bash
# Install from GitHub (one-liner)
curl -fsSL https://raw.githubusercontent.com/maemolee/llm-inline/main/install.sh | sh

# Or with custom GitHub mirror
GITHUB_RAW_BASE=raw.fastgit.org curl -fsSL https://raw.githubusercontent.com/maemolee/llm-inline/main/install.sh | sh
```

### Local Installation
```bash
# Clone and install locally
git clone https://github.com/maemolee/llm-inline.git
cd llm-inline
./install-locally.sh
```

### Uninstallation
```bash
# Uninstall online version
curl -fsSL https://raw.githubusercontent.com/maemolee/llm-inline/main/uninstall.sh | sh

# Or run locally if you have the repo
./uninstall.sh
```

## Usage
```bash
# Direct question (simplified) - recommended
llmi "怎么列出当前目录下的所有文件,并且能看到每个文件的扩展名和文件大小?"

# Traditional way (backward compatible)
llmi ask "这个文件的主要内容是什么？" --file path/to/file.txt
llmi ask "分析这个代码文件" -f ./script.py

# File attachments work with both methods
llmi "这个配置文件有什么问题？" --file nginx.conf
llmi ask "分析错误日志" -f /var/log/error.log
```

## Command Format
- **Direct questions**: `llmi "your question"` (simplified, no `ask` needed)
- **File attachments**: `llmi "question" --file path/to/file`
- **Backward compatibility**: `llmi ask "question"` still works
- **Skill management**: 
  - `llmi install <url>` - Install skills from GitHub or other sources
  - `llmi list` - List installed skills
  - `llmi use <tool>` - Use installed tools
  - `llmi translate <file>` - Translate files (example skill)

## Features
- Reads llm-switch environment variables (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME)
- Structured prompt generation with shell context
- Automatic command extraction for direct use
- OpenTSDB-compatible API integration
- **File attachment support** for text and binary files
- **Relative path resolution** for file attachments
- **File size limiting** (10MB max) for safety
- **Base64 encoding** for binary file handling
- **Skill system** - extensible plugin architecture for custom commands
- **One-click install** skills from GitHub or any URL

### Example Workflow

1. **Setup LLM environment** (using llm-switch):
```bash
source llm-switch
export LLM_PROVIDER=qiniu
export LLM_API_KEY=your_key
export LLM_BASE_URL=your_base_url
export LLM_MODEL_NAME=doubao-seed-1.6-flash
```

2. **Use llmi**:
```bash
# Simplified usage (recommended)
llmi "怎么查看硬盘使用情况?"

# With file attachments
llmi "分析这个配置文件" --file /etc/hosts
llmi "这个脚本有什么问题？" -f ./debug.sh

# Traditional way (still works)
llmi ask "怎么查看系统负载?"
```

## Skill System

### Installing Skills
Skills are community-created extensions that add new functionality to llmi.

```bash
# Install a skill from GitHub
llmi install https://raw.githubusercontent.com/iblueer/llm-inline/main/skill-examples/translate/skill.json

# List installed skills
llmi list

# Use a skill
llmi translate file.txt en
llmi use python-tool --arg value
```

### Skill Examples
Check the [skill-examples/](./skill-examples/) directory for complete skill examples and development guides.

- **translate**: Translate files using LLM
- More examples coming soon...

### Creating Skills
A skill consists of two parts:

1. **skill.json** - Configuration and metadata
2. **handler.py** (optional) - Python implementation

#### Example skill.json:
```json
{
  "name": "translate",
  "description": "使用LLM翻译文件内容",
  "version": "1.0.0",
  "author": "your-name",
  "parameters": [
    {
      "name": "file",
      "type": "file",
      "required": true,
      "description": "要翻译的文件路径"
    },
    {
      "name": "target_lang",
      "type": "string",
      "default": "en",
      "description": "目标语言代码"
    }
  ],
  "handler": "translate.py"
}
```

#### Example handler.py:
```python
#!/usr/bin/env python3

def main(args):
    # Handle skill logic here
    file_path = args[0]
    target_lang = args[1] if len(args) > 1 else "en"
    
    # Your implementation
    print(f"Translating {file_path} to {target_lang}")
    
    return True
```

### Skill Directory Structure
```
~/.llm-inline/skills/
├── translate/
│   ├── skill.json
│   └── translate.py
├── use/
│   └── skill.json
└── custom-tool/
    ├── skill.json
    └── handler.py
```

## Environment Variables Required
- `LLM_API_KEY`: Your API key
- `LLM_BASE_URL": Base URL for the API endpoint
- `LLM_MODEL_NAME`: Model name (optional, defaults to 'doubao-seed-1.6-flash')

## File Attachment Support

### Supported File Types
- **Text files**: Source code, configuration files, logs, documents
- **Binary files**: Images, executables, archives (encoded as base64)

### Usage Examples
```bash
# Analyze source code
llmi "这个Python函数有什么bug？" --file script.py

# Review configuration
llmi "这个nginx配置正确吗？" -f nginx.conf

# Process log files
llmi "分析错误日志找出问题" --file /var/log/error.log

# Handle images
llmi "这个截图显示什么？" --file screenshot.png

# Traditional approach (also works)
llmi ask "分析这段代码" --file script.js
```

### File Path Handling
- **Absolute paths**: `/home/user/file.txt`
- **Relative paths**: `./config.yml`, `../data/input.csv`
- **Home directory**: `~/documents/file.txt`

### Limitations
- Maximum file size: 10MB
- Binary files are automatically encoded as base64
- File content is included in the prompt context

## How It Works
1. Captures current shell environment and directory
2. Processes file attachments (if provided) with path resolution and encoding
3. Builds structured prompt with command format requirements and file content
4. Extracts commands from LLM responses

## Project Structure
```
llm-inline/
├── llmi.py           # Main script
├── activate.sh       # Installation script
├── requirements.txt   # Dependencies
└── __init__.py       # Package initialization
```

## Compatibility
Works with any OpenAI-compatible API endpoint.