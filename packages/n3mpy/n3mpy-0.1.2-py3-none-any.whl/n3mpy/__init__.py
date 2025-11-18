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


def array(key, message, model="kimi-k2-turbo-preview", 
                   base_url="https://api.moonshot.cn/v1", 
                   temperature=0.6, max_tokens=None):
    if key=="ann":
        api_key="sk-zQkdiY09q9ZwEjgEno1p96KL0Xhi1ghSVXnpBwukRn85jnFO"
    elif key=="jh":
        api_key="sk-jxsJeNfytuenuSxzuWWE0RO6NwSa5uOOY8T3w58cjEWCWJwi"
    elif key=="q":
        api_key="sk-z1VbE3gNGANfaXN3OSA4tDADuqcmJwDcVoMnwrWYxGW8QgGO"
    elif key=="l":
        api_key="sk-gNh0xgsfMfoW7AJnuGnCteHYwyjEP8Jq8zf1YmmFfvOK5qXU"
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
