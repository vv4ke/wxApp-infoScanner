import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

try:
    # 发送HTTP请求
    response = requests.get('http://devmap02.mcd.com.cn/')

    # 处理HTTP响应
    if response.status_code == 200:
        print(response.text)
    else:
        response.raise_for_status()  # 抛出HTTP错误
except ConnectionError as e:
    print('Connection Error:', e)
except Timeout as e:
    print('Timeout Error:', e)
except RequestException as e:
    print('Request Error:', e)