# LLM Inline

OpenAI-compatible command line LLM interface powered by llm-switch environment variables.

## Installation
```bash
# Activate the installation
./activate.sh
```

## Usage
```bash
# Ask questions about commands
llmi ask "怎么列出当前目录下的所有文件,并且能看到每个文件的扩展名和文件大小?"

# Ask questions with file attachments
llmi ask "这个文件的主要内容是什么？" --file path/to/file.txt
llmi ask "分析这个代码文件" -f ./script.py
```

## Features
- Reads llm-switch environment variables (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME)
- Structured prompt generation with shell context
- Automatic command extraction for direct use
- OpenTSDB-compatible API integration
- **File attachment support** for text and binary files
- **Relative path resolution** for file attachments
- **File size limiting** (10MB max) for safety
- **Base64 encoding** for binary file handling

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
# Basic usage
llmi ask "怎么查看硬盘使用情况?"

# With file attachment
llmi ask "分析这个配置文件" --file /etc/hosts
llmi ask "这个脚本有什么问题？" -f ./debug.sh
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
llmi ask "这个Python函数有什么bug？" --file script.py

# Review configuration
llmi ask "这个nginx配置正确吗？" -f nginx.conf

# Process log files
llmi ask "分析错误日志找出问题" --file /var/log/error.log

# Handle images
llmi ask "这个截图显示什么？" --file screenshot.png
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