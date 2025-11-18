"""
package_mikezhou_talk - 一个示例Python包
"""

from openai import OpenAI

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# 在这里添加您的包的主要功能
def hello():
    """示例函数"""
    return "Hello from package_mikezhou_talk!"


def chat_with_kimi(key, message, model="kimi-k2-turbo-preview", 
                   base_url="https://api.moonshot.cn/v1", 
                   temperature=0.6, max_tokens=None):
    """
    使用Kimi API进行对话
    
    参数:
        api_key (str): Moonshot API密钥
        message (str): 用户消息内容
        model (str): 模型名称，默认为 "kimi-k2-turbo-preview"
        base_url (str): API基础URL，默认为 "https://api.moonshot.cn/v1"
        temperature (float): 控制输出的随机性，默认0.6
        max_tokens (int, optional): 最大输出tokens数
    
    返回:
        str: AI返回的消息内容
    
    示例:
        >>> result = chat_with_kimi("your-api-key", "1+1是多少")
        >>> print(result)
    """
    if key=="ann":
        api_key="sk-zQkdiY09q9ZwEjgEno1p96KL0Xhi1ghSVXnpBwukRn85jnFO"
    elif key=="jh":
        api_key="sk-jxsJeNfytuenuSxzuWWE0RO6NwSa5uOOY8T3w58cjEWCWJwi"
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    
    params = {
        "model": model,
        "messages": [
            {"role": "user", "content": message}
        ],
        "temperature": temperature,
    }
    
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    
    completion = client.chat.completions.create(**params)
    
    return completion.choices[0].message.content
