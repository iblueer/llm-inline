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
```

## Features
- Reads llm-switch environment variables (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME)
- Structured prompt generation with shell context
- Automatic command extraction for direct use
- OpenTSDB-compatible API integration

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
llmi ask "怎么查看硬盘使用情况?"
```

## Environment Variables Required
- `LLM_API_KEY`: Your API key
- `LLM_BASE_URL": Base URL for the API endpoint

## How It Works
1. Captures current shell environment and directory
2. Builds structured prompt with command format requirements
3. Extracts commands from LLM responses

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