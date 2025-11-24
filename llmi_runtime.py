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
