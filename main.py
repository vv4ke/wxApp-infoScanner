import argparse
from modle import unwxapkg, config, infoFinder
import os

if __name__ == '__main__':

    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser()

    # 添加必须的参数
    parser.add_argument("--mode", choices=["sp", "sf", "wf"], help="Specify the mode")
    parser.add_argument("--config-file", required=True, help="Specify the path to the config file")

    # 添加可选参数
    parser.add_argument("--wxid", help="Specify the secret key string")
    parser.add_argument("--folder-path", help="Specify the folder path to scan")

    # 解析命令行参数
    args = parser.parse_args()

    config = config.load_config(config_yaml_path=args.config_file)

    if args.mode == 'sp':
        Applet_Packet_Save_Folder = unwxapkg.unveilr_unpacket(args.sp, args.wxid, config['File_Config'])
        infoFinder.infoFinder(Applet_Packet_Save_Folder)
    elif args.mode == 'wf':
        unwxapkg.monitor_folder(config)
    elif args.mode == 'sf':
        infoFinder.infoFinder(args.sf, config)
