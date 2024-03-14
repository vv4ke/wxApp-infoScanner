import argparse
import yaml
import os
import time

from modules import decomplie_wxapp, info_finder


def load_config(config_yaml_path=None, load_type=None):
    if config_yaml_path is None:
        return False
    with open(config_yaml_path, 'r', encoding='utf-8') as f:
        configs = list(yaml.load_all(f.read(), Loader=yaml.FullLoader))[0]
        if load_type is None:
            return configs
        elif load_type in configs:
            return config[load_type]
        else:
            return False


if __name__ == '__main__':

    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser()
    # 添加必须的参数
    parser.add_argument("--mode", choices=["sp", "sf", "mf"],
                        help="选择启动模式：sp 扫描指定的小程序包; sf 扫描指定的文件夹; mf 监控微信小程序更新包")
    # 添加可选参数
    parser.add_argument("--config-file", default=r'config.yaml', help="指定配置文件路径, default： ./config/config.yaml")
    parser.add_argument("--wxid", help="微信小程序的 AES secret key")
    parser.add_argument("--folder-path", help="指定的包或文件夹路径")
    # 解析命令行参数
    args = parser.parse_args()

    # 配置常量
    config = load_config(config_yaml_path=args.config_file)
    root_path = os.getcwd()
    wxapp = decomplie_wxapp.DecompileWxApp(config_path=args.config_file, root_path=root_path)
    infoFinder = info_finder.InfoFinder(config_path=args.config_file, root_path=root_path)

    # 扫描指定微信小程序包
    if args.mode == 'sp':
        if args.folder_path is None:
            print("请用 --folder-path 指定的包或文件夹路径")
            exit(1)
        # 反编译小程序包
        wx_app_code_save_path = wxapp.unveilr_decompile(args.folder_path, args.wxid)
        # 扫描小程序代码
        results = infoFinder.start_scan(wx_app_code_save_path)
        # 扫描信息存入excel
        infoFinder.write2excel(results)

    # 监听小程序新增状态
    elif args.mode == 'mf':
        # 配置参数
        wx_app_path = config['File_Config']['WX_Applet_Path']
        sleep_time = config['File_Config']['Sleep_Time']

        before = dict([(f, None) for f in os.listdir(wx_app_path)])
        print(before)
        while True:
            time.sleep(sleep_time)  # 间隔休眠再检查一次
            after = dict([(f, None) for f in os.listdir(wx_app_path)])
            added = [f for f in after if not f in before]
            if added:
                print("New folder(s) created:", ", ".join(added))
                for son_folder in added:
                    print("等待程序下载...")
                    time.sleep(sleep_time)
                    # 反编译小程序包
                    wx_app_code_save_path = wxapp.unveilr_decompile(wx_app_path, son_folder)
                    # 扫描小程序代码
                    results = infoFinder.start_scan(wx_app_code_save_path)
                    # 扫描信息存入excel
                    infoFinder.write2excel(results)
            else:
                print(before)
            before = after

    elif args.mode == 'sf':
        if args.folder_path is None:
            print("请用 --folder-path 指定的包或文件夹路径")
            exit(1)
        results = infoFinder.start_scan(args.folder_path)
        infoFinder.write2excel(results)
