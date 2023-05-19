import re
import os
import queue
import threading
import pandas as pd
import time
from modle import active_request


def worker(task_queue, results_queue):
    # 定义一个线程执行的任务函数
    while True:
        try:
            task_arg = task_queue.get(block=False)
            reg_rule_name, regex, target_folder, file_scan_config = task_arg
            regex = re.compile(regex)   # 创建对象匹配速度快
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


def start_scan(file_scan_config, regex_config, target_folder):
    # 创建基本变量
    match_results = {}
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    num_threads = 20
    threads = []

    # 任务队列
    for reg_rule_name in regex_config:
        regex = regex_config[reg_rule_name]
        task_arg = [reg_rule_name, regex, target_folder, file_scan_config]
        task_queue.put(task_arg)

    # 创建线程池
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(task_queue, results_queue))
        t.start()
        threads.append(t)

    # 阻塞直到所有任务完成
    task_queue.join()

    # 等待所有线程完成
    for t in threads:
        t.join()

    # 将结果取出并存储到列表中
    while not results_queue.empty():
        reg_rule_name, match_result = results_queue.get(block=False)
        match_results[reg_rule_name] = match_result
    return match_results


def match_content(regex, target_folder, file_scan_config):
    match_results = []
    for (current_path, son_folders_name, files_name) in os.walk(target_folder):
        # 先匹配当前文件夹中的文件
        if files_name is not None:
            for file in files_name:
                if check_suffix(file, file_scan_config):
                    with open(os.path.join(current_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        # print(f"正则：{reg}\n文件：{os.path.join(current_path, file)}")
                        match_result = regex.findall(file_content)
                        match_results += match_result
                else:
                    continue
        # 递归匹配子文件夹中的文件
        if son_folders_name is not None:
            for son_folder_name in son_folders_name:
                son_target_folder = os.path.join(current_path, son_folder_name)
                match_result = match_content(regex, son_target_folder, file_scan_config)
                match_results += match_result
    return clear_list(match_results, file_scan_config)


def clear_list(list01, file_scan_config):
    tamp_list = []
    for i in list01:
        if not isinstance(i, str):
            i = max(i)
        if i not in tamp_list and check_suffix(i, file_scan_config):
            tamp_list.append(i)
    return tamp_list


def check_suffix(filename, file_scan_config):
    filename_split = filename.split('.')
    if file_scan_config['Black_Suffix_list']['active']:
        if len(filename_split) > 1 and filename_split[-1] in file_scan_config['Black_Suffix_list']['suffix_list']:
            return False
        else:
            return True
    elif file_scan_config['White_Suffix_list']['active']:
        if len(filename_split) > 1 and filename_split[-1] in file_scan_config['White_Suffix_list']['suffix_list']:
            return True
        else:
            return False


def write2excel(match_results=None, Excel_Folder=None):

    if match_results['App_Name_regex']:
        excel_name = f"{match_results['App_Name_regex'][0]}_{time.strftime('%Y%m%d%H%M%S')}.xlsx"
    else:
        excel_name = f"{time.strftime('%Y%m%d%H%M%S')}.xlsx"

    # 文件路径参数
    current_directory = os.getcwd()
    excel_folder = os.path.join(current_directory, Excel_Folder)
    excel_file = os.path.join(excel_folder, excel_name)
    print(f'正在写入 {excel_file} 表格中')

    check_folder_exists(excel_folder)

    df = pd.DataFrame.from_dict(match_results, orient='index').transpose()

    # 将数据存储到Excel表格中
    writer = pd.ExcelWriter(excel_file, engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.book.save(excel_file)

    print(f'写入成功：{excel_file}')

    return


def check_folder_exists(folder_path=None):
    # 检测文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"已创建文件夹 {folder_path}")
    return


def infoFinder(target_folder='', all_config=None):
    match_results = start_scan(all_config['File_Config'], all_config['Regex_Config'], target_folder)
    # for i in match_results:
    #     print(f'\033[0;32;40m{i}\033[0m: {match_results[i]}')
    write2excel(match_results, all_config['File_Config']['Excel_Folder'])
    active_request.scan_active(match_results['Url_regex'], match_results['Uri_regex'], all_config['Request_Config'])
    return


if __name__ == "__main__":
    folder = r'./test_folder'
    infoFinder(folder)
