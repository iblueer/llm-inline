#!/usr/bin/env python3
"""
llm-inline运行时API
为技能提供LLM调用接口，屏蔽LLM接入细节
"""

import os
from openai import OpenAI


class LLMMRuntime:
    """LLM运行时环境，为技能提供统一的LLM接口"""
    
    def __init__(self):
        """初始化LLM客户端，使用llmi的环境变量"""
        api_key = os.environ.get('LLM_API_KEY')
        base_url = os.environ.get('LLM_BASE_URL')
        model_name = os.environ.get('LLM_MODEL_NAME', 'doubao-seed-1.6-flash')
        
        if not api_key or not base_url:
            raise ValueError("❌ 缺少LLM环境变量，请先运行: source llm-switch")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
    
    def chat_completion(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        发送聊天完成请求
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            **kwargs: 其他OpenAI参数
            
        Returns:
            LLM响应文本
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # 默认参数
        default_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.3
        }
        
        # 合并用户参数
        default_params.update(kwargs)
        
        response = self.client.chat.completions.create(**default_params)
        return response.choices[0].message.content


# 全局LLM运行时实例
_llm_runtime = None


def get_llm_runtime() -> LLMMRuntime:
    """获取全局LLM运行时实例（单例模式）"""
    global _llm_runtime
    if _llm_runtime is None:
        _llm_runtime = LLMMRuntime()
    return _llm_runtime


def call_llm(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """
    技能调用LLM的简化接口
    
    Args:
        prompt: 用户提示
        system_prompt: 系统提示（可选）
        **kwargs: 其他参数
        
    Returns:
        LLM响应文本
    """
    runtime = get_llm_runtime()
    return runtime.chat_completion(prompt, system_prompt, **kwargs)


def check_llm_env() -> bool:
    """检查LLM环境是否配置"""
    required_vars = ['LLM_API_KEY', 'LLM_BASE_URL']
    return all(os.environ.get(var) for var in required_vars)


def get_file_content(arg_value) -> dict:
    """
    获取预处理后的文件内容
    
    Args:
        arg_value: 参数值，可能是文件路径字符串或文件信息字典
        
    Returns:
        文件信息字典，包含content等字段
    """
    # 如果是字典，说明已经由llmi预处理过
    if isinstance(arg_value, dict):
        return arg_value
    
    # 如果是字符串，按传统方式处理（向后兼容）
    print("⚠️  检测到未预处理的文件参数，建议在技能配置中声明type='file'")
    
    # 传统文件读取逻辑
    from pathlib import Path
    import base64
    
    abs_path = Path(arg_value).expanduser().resolve()
    
    if not abs_path.exists():
        return {'error': f"文件不存在: {arg_value}"}
    
    if not abs_path.is_file():
        return {'error': f"路径不是文件: {arg_value}"}
    
    file_size = abs_path.stat().st_size
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        return {'error': f"文件过大，超过10MB限制: {arg_value}"}
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        is_binary = False
    except (UnicodeDecodeError, Exception):
        with open(abs_path, 'rb') as f:
            binary_content = f.read()
        content = base64.b64encode(binary_content).decode('utf-8')
        is_binary = True
    
    return {
        'path': str(abs_path),
        'name': abs_path.name,
        'size': file_size,
        'content': content,
        'is_binary': is_binary
    }


class VisionLLMRuntime:
    """Vision LLM运行时环境，使用LLM_VISION_*环境变量"""
    
    def __init__(self):
        """初始化Vision LLM客户端，使用llm-switch的Vision环境变量"""
        # 优先使用VISION专属变量，否则回退到通用变量
        api_key = os.environ.get('LLM_VISION_API_KEY') or os.environ.get('LLM_API_KEY')
        base_url = os.environ.get('LLM_VISION_BASE_URL') or os.environ.get('LLM_BASE_URL')
        model_name = os.environ.get('LLM_VISION_MODEL_NAME') or os.environ.get('LLM_VISION_MODEL') or os.environ.get('LLM_MODEL_NAME', 'gemini-3-pro-image')
        
        if not api_key or not base_url:
            raise ValueError("❌ 缺少Vision LLM环境变量，请先运行: llm-switch visionuse <name>")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
    
    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs) -> dict:
        """
        调用Vision模型生成图像
        
        Args:
            prompt: 图像生成提示词
            size: 图像尺寸 (如: "1024x1024", "1280x720")
            **kwargs: 其他参数
            
        Returns:
            包含生成结果的字典
        """
        # 默认参数
        default_params = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
        }
        
        # 添加size参数到extra_body
        extra_body = kwargs.pop('extra_body', {})
        extra_body['size'] = size
        default_params['extra_body'] = extra_body
        
        # 合并用户参数
        default_params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**default_params)
            content = response.choices[0].message.content
            
            # 返回结果
            return {
                'content': content,
                'model': self.model_name,
                'size': size
            }
        except Exception as e:
            return {
                'error': str(e)
            }


# 全局Vision LLM运行时实例
_vision_llm_runtime = None


def get_vision_llm_runtime() -> VisionLLMRuntime:
    """获取全局Vision LLM运行时实例（单例模式）"""
    global _vision_llm_runtime
    if _vision_llm_runtime is None:
        _vision_llm_runtime = VisionLLMRuntime()
    return _vision_llm_runtime


def vision_call_llm(prompt: str, size: str = "1024x1024", **kwargs) -> dict:
    """
    技能调用Vision LLM的简化接口
    
    使用llm-switch的visionuse命令设置的环境变量
    
    Args:
        prompt: 图像生成提示词
        size: 图像尺寸，支持:
              - "1024x1024" (1:1)
              - "1280x720" (16:9)
              - "720x1280" (9:16)
              - "1216x896" (4:3)
        **kwargs: 其他参数
        
    Returns:
        包含生成结果的字典，可能包含:
        - content: 模型返回的内容
        - image_data: Base64编码的图像数据
        - image_url: 图像URL
        - error: 错误信息
    """
    runtime = get_vision_llm_runtime()
    return runtime.generate_image(prompt, size, **kwargs)


def check_vision_llm_env() -> bool:
    """检查Vision LLM环境是否配置"""
    # 检查Vision专属变量或通用变量
    has_vision = bool(os.environ.get('LLM_VISION_API_KEY') and os.environ.get('LLM_VISION_BASE_URL'))
    has_general = bool(os.environ.get('LLM_API_KEY') and os.environ.get('LLM_BASE_URL'))
    return has_vision or has_general
