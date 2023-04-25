import re
import os
import yaml
import queue
import threading
import pandas as pd


# 定义一个线程执行的任务函数
def worker(task_queue, results_queue):
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


def load_config(config_yaml_path=None):
    if config_yaml_path is None:
        return False
    with open(config_yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.load_all(f.read(), Loader=yaml.FullLoader)
        # print(config)
        # for reg in config:
        #     print(reg)
        return config


def start_scan(file_scan_config, regex_config, target_folder):
    # 创建基本变量
    match_results = {}
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    num_threads = 5
    threads = []

    # 任务队列
    for reg_rule_name in regex_config:
        regex = regex_config[reg_rule_name]
        task_arg = [reg_rule_name.split('_'), regex, target_folder, file_scan_config]
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


def match_content(reg, target_folder, file_scan_config):
    reg = re.compile(reg)
    match_results = []
    for (current_path, son_folders_name, files_name) in os.walk(target_folder):

        # 先匹配当前文件夹中的文件
        if files_name is not None:
            for file in files_name:
                if check_suffix(file, file_scan_config):
                    with open(os.path.join(current_path, file), 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        match_result = reg.findall(file_content)
                        # match_result = clear_list(match_result)
                        match_results += match_result
                else:
                    continue

        # 递归匹配子文件夹中的文件
        if son_folders_name is not None:
            for son_folder_name in son_folders_name:
                target_folder = os.path.join(current_path, son_folder_name)
                match_result = match_content(reg, target_folder)
                # match_result = clear_list(match_result)
                match_results += match_result

    return clear_list(match_results)


def clear_list(list01):
    tamp_list = []
    for i in list01:
        if not isinstance(i, str):
            i = max(i)
        if i not in tamp_list:
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


def write2excel(match_results):
    df = pd.DataFrame.from_dict(match_results, orient='index').transpose()

    # 将数据存储到Excel表格中
    writer = pd.ExcelWriter('data.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.book.save('data.xlsx')
    return


def main():
    config = list(load_config(r'./config.yaml'))
    file_scan_config = config[0]
    regex_config = config[1]
    requests_config = config[2]
    target_folder = r'./test_folder'
    match_results = start_scan(file_scan_config, regex_config, target_folder)
    for i in match_results:
        print(f'\033[0;32;40m{i}\033[0m: {match_results[i]}')

    write2excel(match_results)
    return


if __name__ == "__main__":
    main()
