"""
api接口未授权扫描以及非 200 状态码绕过。

"""
import queue
import re

import requests
from urllib.parse import urlparse
import socket


def req_work(task_queue, results_queue):
    # 定义一个线程执行的任务函数
    while True:
        try:
            task_arg = task_queue.get(block=False)
            reg_rule_name, regex, target_folder, file_scan_config = task_arg
            match_result = match_content(regex, target_folder, file_scan_config)
            # 将处理结果存储到 results 队列中
            result = [reg_rule_name, match_result]
            results_queue.put(result)
            task_queue.task_done()
        except queue.Empty:
            # 捕获队列为空的异常
            break
        except Exception as e:
            # 捕获其他异常
            print(f"Caught an exception: {e}")
            task_queue.task_done()


def scan_active(url_list=None, uri_list=None, Request_Config=None):

    # 黑白名单过滤一下
    if url_list is None:
        url_list = []
    # 先用黑白名单筛选一波url和uri
    url_list = filter_list(url_list, Request_Config['hostname_filter_rule'])
    url_list = filter_list(url_list, Request_Config['ip_filter_rule'])
    uri_list = filter_list(uri_list, Request_Config['uri_filter_rule']).insert(0, '')

    # 存活过滤
    url_list = host_alive(url_list)

    task_queue = queue.Queue()
    results_queue = queue.Queue()
    num_threads = 20
    threads = []

    if url_list:
        return None
    for url in url_list:
        for uri in uri_list:
            # 开始请求url拼凑
            tamp = scrabbled_url(url, uri, Request_Config['scrabbled_rule'])
            task_arg = []

    return


# 根据黑白名单过滤一下数组
def filter_list(old_list=None, filter_rule=None):
    # 白名单优先
    new_list = []
    if filter_rule['allowed']:
        for regex in filter_rule['allowed']:
            regex = re.compile(regex)
            for i in old_list:
                if regex.search(i):
                    new_list.append(i)
                else:
                    continue
    elif filter_rule['disallowed']:
        for regex in filter_rule['disallowed']:
            regex = re.compile(regex)
            for i in old_list:
                if regex.search(i) is None:
                    new_list.append(i)
                else:
                    continue
    else:
        pass
    return new_list


def host_alive(url_list=None):
    # 筛选出端口存活的Domian或IP
    alive_host = []
    disalive_host = []
    alive_url_list = []
    for url in url_list:
        domain, port = extract_domain_port(url)
        if [domain, port] in disalive_host:
            continue
        elif [domain, port] in alive_host:
            alive_url_list.append(url)
        else:
            if tcp_alive(domain, port):
                alive_host.append([domain, port])
                alive_url_list.append(url)
            else:
                disalive_host.append([domain, port])
    return alive_url_list


def extract_domain_port(url=''):
    # 使用urlparse函数解析URL
    parsed_url = urlparse(url)
    # 获取解析后的结果中的域名或IP地址
    domain = parsed_url.hostname
    # 获取解析后的结果中的端口号
    port = parsed_url.port
    # 如果端口号为空，则使用默认端口号
    if port is None:
        if parsed_url.scheme == 'https':
            port = 443
        else:
            port = 80
    # 返回域名或IP地址和端口号
    return domain, port


def tcp_alive(host, port):
    try:
        # 创建一个TCP socket对象
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置socket超时时间
        s.settimeout(10)
        # 尝试连接到指定的host和port
        s.connect((host, port))
        # 连接成功，返回True
        s.close()
        return True
    except socket.error:
        # 连接失败，返回False
        return False


def scrabbled_url(url, uri, scrabbled_rule):
    # 关于尽可能去重的问题，写一个递归函数，递归比较 url的最后一个和uri的第一个 ，如果相同，继续比较第二个，直到不同，然后函数返回 0,1,2 等,0表示0个重复，反之.拼接时，按照0,1,2值来删除uri