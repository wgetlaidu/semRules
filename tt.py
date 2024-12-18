import yaml
import json
import requests
import hashlib
import random
import os

def baidu_translate(query, app_id, secret_key, from_lang="en", to_lang="zh"): 
    """
    使用百度翻译 API 翻译文本。
    """
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    salt = str(random.randint(32768, 65536))
    sign = hashlib.md5((app_id + query + salt + secret_key).encode()).hexdigest()

    params = {
        "q": query,
        "from": from_lang,
        "to": to_lang,
        "appid": app_id,
        "salt": salt,
        "sign": sign,
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "trans_result" in result:
        return result["trans_result"][0]["dst"]
    else:
        raise Exception(f"Translation error: {result}")

def translate_and_update_yaml(file_path, app_id, secret_key, vuln_type="android"):
    # 读取 YAML 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    # 递归函数，遍历并处理 message 字段
    def process_messages(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() == 'message' and isinstance(value, str):
                    # 使用百度翻译 API 翻译 message
                    translated_message = baidu_translate(value, app_id, secret_key)

                    # 获取 severity 的值
                    severity = data.get('severity', 'unknown')

                    # 替换 message 的值为 JSON 数据
                    json_data = {
                        "vuln_type": vuln_type,
                        "level": severity,
                        "message": translated_message
                    }

                    data[key] = json.dumps(json_data)

                    

                else:
                    process_messages(value)
        elif isinstance(data, list):
            for item in data:
                process_messages(item)

    process_messages(data)

    # 写回 YAML 文件
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.safe_dump(data, file, default_flow_style=False, allow_unicode=True)

def process_directory(directory, app_id, secret_key):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                try:
                    translate_and_update_yaml(file_path, app_id, secret_key)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

# 替换为你的百度翻译 API 配置
APP_ID = "20241216002229591"       # 替换为你的 AppID
SECRET_KEY = "KbmxPt5_MqCg5VmOjRy9"  # 替换为你的密钥

# 使用示例
directory_path = '/Users/wgetlaidu/Downloads/semgrep-rules-android-security-main/rules'  # 替换为你的目录路径
process_directory(directory_path, APP_ID, SECRET_KEY)
