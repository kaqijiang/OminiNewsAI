import requests
import re
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # self.base_url = 'https://api.ominiai.cn/v1'

    def request_grop_api(self, prompt: str, title: str, original_content: str, source_url: str, model: str):
        if len(original_content) > 15000:
            return None, None
        base_url = 'https://ai.ominiai.cn/v1'

        client = OpenAI(api_key=self.api_key, base_url=base_url)
        user_content = f"the link：{source_url}. the title：{title}. the original content：{original_content}"
        messages = [{'role': 'system',
                     'content': prompt},
                    {'role': 'user',
                     'content': user_content}
                    ]
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None
            )
            full_content = ""
            for choice in response.choices:
                full_content += choice.message.content

            full_content = full_content.replace("：", ":")
            parts = full_content.split('内容:')

            split_result = parts[0].split('标题:')
            if len(split_result) > 1:
                title_part = split_result[1].strip().strip('#').strip('\n')
            else:
                title_part = split_result[0]
            content_part = parts[1].strip().strip('\n') if len(parts) > 1 else None  # 提取内容部分，并去除多余空白

            if title_part and content_part:
                print(title_part, content_part)
                return title_part, content_part
            else:
                return None, None
        except Exception as e:
            print(f"发生错误: {e}")
            return None,None

    # def request_openai_api(self, prompt: str, title: str, original_content: str, source_url: str):
    #     """
    #     通用的请求 OpenAI API 的函数
    #     """
    #     headers = {
    #         'Authorization': f'Bearer {self.api_key}',
    #         'Content-Type': 'application/json'
    #     }
    #
    #     data = {
    #         "model": "gpt-4o",
    #         "messages": [
    #             {"role": "system", "content": prompt},
    #             {"role": "user", "content": f"链接：{source_url} 标题：{title}"}
    #         ]
    #     }
    #
    #     try:
    #         response = requests.post(self.base_url, headers=headers, json=data)
    #         response.raise_for_status()  # 如果响应状态码不是200，抛出异常
    #
    #         completion = response.json()
    #         content = completion['choices'][0]['message']['content']
    #         title_match = re.search(r'标题：(.*?)\n', content)
    #         content_match = re.search(r'内容：(.*)', content, re.DOTALL)
    #
    #         if title_match and content_match:
    #             return title_match.group(1).strip(), content_match.group(1).strip()
    #         else:
    #             return None, None
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"请求 OpenAI API 出错: {e}")
    #         return None, None
