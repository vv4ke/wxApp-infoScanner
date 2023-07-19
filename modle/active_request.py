"""
api接口未授权扫描以及非 200 状态码绕过。

"""
import queue
import re
import requests
from urllib.parse import urlparse
import socket
import threading
import urllib3


def req_work(task_queue, results_queue, Request_Config=None):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # 定义一个线程执行的任务函数
    while True:
        try:
            url = task_queue.get(block=False)
            for http_method in Request_Config['http_methods']:
                try:
                    response = requests.request(method=http_method,
                                                url=url,
                                                cookies=Request_Config['cookies'],
                                                headers=Request_Config['headers'],
                                                params=Request_Config['params'],
                                                # data=Request_Config['data'],
                                                json=Request_Config['json'],
                                                allow_redirects=Request_Config['allow_redirects'],
                                                verify=Request_Config['verify'],
                                                timeout=Request_Config['timeout'],
                                                proxies=Request_Config['proxies']
                                                )
                    print(f"[{response.status_code}] [{http_method}] {len(response.text.encode('utf-8')) / 1024}KB {url}")
                    result = [
                        response.status_code,
                        http_method,
                        len(response.text.encode('utf-8')) / 1024,
                        url
                    ]
                    # 将处理结果存储到 results 队列中
                    results_queue.put(result)
                except requests.exceptions.Timeout:  # 处理请求超时的情况
                    pass
                except requests.exceptions.RequestException:  # 处理其他请求异常的情况
                    pass
            task_queue.task_done()
        except queue.Empty:
            # 捕获队列为空的异常
            break
        except Exception as e:
            # 捕获其他异常
            print(f"Caught an exception: {e}")
            task_queue.task_done()


# def print_out(result=None, Request_Config=None):
#     status_code, http_method, resp_len, url = result
#     if status_code


def scan_active(url_list=None, uri_list=None, Request_Config=None):
    if url_list is None:
        url_list = []
    # 先用黑白名单筛选一波url和uri
    url_list = filter_list(url_list, Request_Config['hostname_filter_rule'])
    url_list = filter_list(url_list, Request_Config['ip_filter_rule'])
    uri_list = filter_list(uri_list, Request_Config['uri_filter_rule'])

    # 然后手动筛选一遍domain
    if Request_Config['manual_filter']:
        url_list = manual_filter(url_list)

    # 存活过滤，顺带进行Finger识别
    url_list = host_alive(url_list)

    task_queue = queue.Queue()
    results_queue = queue.Queue()
    num_threads = Request_Config['request_threads']
    threads = []

    if url_list is None:
        return None

    # 填充任务队列
    target_list = []
    for url in url_list:
        for uri in uri_list:
            # 根据拼接策略拼接url
            target = url_target(url, uri)
            if target not in target_list:
                target_list.append(target)
                task_queue.put(target)

    # 创建线程池
    for i in range(num_threads):
        t = threading.Thread(target=req_work, args=(task_queue, results_queue, Request_Config))
        t.start()
        threads.append(t)

    # 阻塞直到所有任务完成
    task_queue.join()

    # 等待所有线程完成
    for t in threads:
        t.join()

    # # 将结果取出并存储到列表中
    # while not results_queue.empty():
    #     status_code, http_method, body_length, url = results_queue.get(block=False)
    #     match_results[reg_rule_name] = match_result
    return results_queue


def manual_filter(url_list=None):
    """
    手动筛选domain
    :param url_list:
    :return:
    """
    new_url_list = []
    black_domain = []
    white_domain = []
    for url in url_list:
        domain = url.split('/')[2]
        # 先对比是否在黑白名单中
        if (domain not in white_domain) and (domain not in black_domain):
            choose_status = True
            while choose_status:
                choose = input(f'域名/IP: {domain} 是否要进行扫描？[y/N] ')
                if choose == 'Y' or choose == 'y':
                    white_domain.append(domain)
                    new_url_list.append(url)
                    choose_status = False
                elif choose == 'N' or choose == 'n' or choose == '':
                    black_domain.append(domain)
                    choose_status = False
        elif domain in white_domain:
            new_url_list.append(url)
        else:
            continue
    return new_url_list


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
                # Finger识别
                #
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


def url_target(url, uri):
    """
    :param url:
    :param uri:
    :param scrabbled_rule:
    :return: uriList
    针对url和uri的多种情况：
    1.对于存在get参数的url，选择不拼接uri，直接返回即可。
    2.要根据路由绕过策略选择拼接方式，例如shiro的绕过、spring的绕过、nginx代理的绕过策略，特殊头的绕过等。
        2.1.shiro：https://www.freebuf.com/vuls/362341.html
        2.2.spring：
    3.为了减少发包数量，提高命中正确率，应该对比url中的uri和uri。合理的”去重“，例如 http://www.baidu.com/a/b/c /b/d，应该拼接为 http://www.baidu.com/a/b/d
    """
    if is_page(url):
        return url
    else:
        return scrabbled_url(url, uri)


def is_page(url=''):
    if '?' in url:
        return True
    elif '.' in url.split('/')[-1]:
        return True
    else:
        return False


def scrabbled_url(url, uri):
    urlList = url.split('/')
    if len(urlList) == 3:  # url中的路径为空
        return url + '/' + uri
    elif len(urlList) == 4:  # url中的路径为 /
        return url + uri
    elif uri.startswith('.'):  # uri以.开头
        if url.endswith('/'):
            return url + uri
        else:
            return url + '/' + uri
    else:
        if not uri.startswith('/'):
            uri = '/' + uri
        uri_start = uri.split('/')[1]
        url_path_list = urlList[3:]
        for i in range(len(url_path_list)):
            if url_path_list[i] == uri_start:
                return '/'.join(urlList[0:3 + i]) + uri
        return url + uri


if __name__ == '__main__':
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc', 'qwe/zxc'))
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc/', 'qwe/zxc'))
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc', '/qwe/zxc'))
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc', '/qwe/zxc/'))
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc/', '/zxc/a/zxc/'))
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc/', './qwe/zxc'))
    # print(scrabbled_url('https://www.baidu.com/qwe/asd/zxc', '../../qwe/zxc'))
    url_list = [
        'https://www.baidu.com/qwe/asd/zxc',
        'https://www.baidu.com/qwe/asd/zxc',
        'https://www.1baidu.com/qwe/asd/zxc',
        'https://www.2baidu.com/qwe/asd/zxc',
        'https://www.4baidu.com/qwe/asd/zxc',
        'https://www.4baidu.com/qwe/asd/zxc',
        'https://www.5baidu.com:8080/qwe/asd/zxc'
    ]
    print(manual_filter(url_list))
