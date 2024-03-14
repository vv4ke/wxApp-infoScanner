import yaml
import re
import os
import queue
import threading
import pandas as pd
import time


class InfoFinder(object):
    def __init__(self, config_path=r'', root_path=r''):
        # 加载config.yaml 中的信息扫描配置 InfoFinder
        print('init InfoFinder')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = list(yaml.load_all(f.read(), Loader=yaml.FullLoader))[0]['InfoFinder']
        self.root_path = root_path

    def start_scan(self, target_folder):
        # 创建基本变量
        match_results = {}
        task_queue = queue.Queue()
        results_queue = queue.Queue()
        threads = []

        # 任务队列
        for reg_rule_name in self.config['Regex_Config']:
            regex = self.config['Regex_Config'][reg_rule_name]
            task_arg = [reg_rule_name, regex, target_folder]
            task_queue.put(task_arg)

        # 创建线程池
        for i in range(self.config['Scanner_Threads']):
            t = threading.Thread(target=self.worker, args=(task_queue, results_queue))
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

    def worker(self, task_queue, results_queue):
        # 定义一个线程执行的任务函数
        while True:
            try:
                task_arg = task_queue.get(block=False)
                reg_rule_name, regex, target_folder = task_arg
                regex = re.compile(regex)  # 创建对象匹配速度快
                match_result = self.match_content(regex, target_folder)
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

    def match_content(self, regex, target_folder):
        match_results = []
        for (current_path, son_folders_name, files_name) in os.walk(target_folder):
            # 先匹配当前文件夹中的文件
            if files_name is not None:
                for file_name in files_name:
                    if self.check_suffix(file_name):
                        with open(os.path.join(current_path, file_name), 'r', encoding='utf-8', errors='ignore') as f:
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
                    match_result = self.match_content(regex, son_target_folder)
                    match_results += match_result
        return self.clear_list(match_results)

    def clear_list(self, list01):
        black_list = ['http', 'https']
        tamp_list = []
        for i in list01:
            if not isinstance(i, str):  # 检测是否为str对象
                i = list(i)
                for j in range(len(i)):
                    if i[j] in black_list:
                        i[j] = ''
                i = max(i, key=len)
            if i not in tamp_list and self.check_suffix(i):
                tamp_list.append(i)
        return tamp_list

    def check_suffix(self, filename):
        filename_split = filename.split('.')
        if self.config['File_Filter_Config']['Black_Suffix_list']['active']:
            if len(filename_split) > 1 and filename_split[-1] in self.config['File_Filter_Config']['Black_Suffix_list']['suffix_list']:
                return False
            else:
                return True
        elif self.config['File_Filter_Config']['White_Suffix_list']['active']:
            if len(filename_split) > 1 and filename_split[-1] in self.config['File_Filter_Config']['White_Suffix_list']['suffix_list']:
                return True
            else:
                return False

    def write2excel(self, match_results=None):

        if match_results['App_Name_regex']:
            excel_name = f"{match_results['App_Name_regex'][0]}_{time.strftime('%Y_%m_%d_%H_%M_%S')}.xlsx"
        else:
            excel_name = f"{time.strftime('%Y_%m_%d_%H_%M_%S')}.xlsx"

        # 文件路径参数
        excel_folder = os.path.join(self.root_path, self.config['Excel_Folder'])
        excel_file = os.path.join(excel_folder, excel_name)
        print(f'正在写入 {excel_file} 表格中')

        self.check_folder_exists(excel_folder)

        df = pd.DataFrame.from_dict(match_results, orient='index').transpose()

        # 将数据存储到Excel表格中
        writer = pd.ExcelWriter(excel_file, engine='openpyxl')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.book.save(excel_file)

        print(f'写入成功：{excel_file}')

    def check_folder_exists(self, folder_path=None):
        # 检测文件夹是否存在，如果不存在则创建
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"已创建文件夹 {folder_path}")
        return


if __name__ == '__main__':

    test_infoFinder = InfoFinder(r'../config.yaml', r'E:\CodeProject\wxApp-infoScanner')
    results = test_infoFinder.start_scan(r'E:\CodeProject\wxApp-infoScanner\app_code\_wx229fa2ad5c78548c_2024_02_23_00_34_17')
    test_infoFinder.write2excel(results)
