import re
import os
import yaml


def load_config(config_yaml_path=None):
    if config_yaml_path is None:
        return False
    with open(config_yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.load_all(f.read(), Loader=yaml.FullLoader)
        # print(config)
        # for reg in config:
        #     print(reg)
        return config


def start_scan(reg_config, target_folder):
    match_results = {}
    for reg_rules in reg_config:
        reg = reg_config[reg_rules]
        match_result = match_content(reg, target_folder)
        match_result = clear_list(match_result)
        match_results[reg_rules] = match_result
    return match_results


def match_content(reg, target_folder):
    reg = re.compile(reg)
    match_results = []
    for (current_path, son_folders_name, files_name) in os.walk(target_folder):

        # 先匹配当前文件夹中的文件
        if files_name is not None:
            for file in files_name:
                with open(os.path.join(current_path, file), 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    match_result = reg.findall(file_content)
                    match_result = clear_list(match_result)
                    match_results += match_result

        # 递归匹配子文件夹中的文件
        if son_folders_name is not None:
            for son_folder_name in son_folders_name:
                target_folder = os.path.join(current_path, son_folder_name)
                match_result = match_content(reg, target_folder)
                match_result = clear_list(match_result)
                match_results += match_result

    return match_results


def clear_list(list01):
    tamp_list = []
    for i in list01:
        if not isinstance(i, str):
            i = max(i)
        if i not in tamp_list:
            tamp_list.append(i)
    return tamp_list


def main():
    config = list(load_config(r'./config.yaml'))
    target_folder = r'./test_folder'
    match_results = start_scan(config[0], target_folder)
    for i in match_results:
        print(f'\033[0;32;40m{i}\033[0m: {match_results[i]}')
    return


if __name__ == "__main__":
    main()
