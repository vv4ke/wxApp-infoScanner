import argparse
from modle import unwxapkg, config, infoFinder

if __name__ == '__main__':

    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser()

    # 添加必须的参数
    parser.add_argument("--mode", choices=["sp", "sf", "mf"], help="选择启动模式：sp 扫描指定的小程序包; sf 扫描指定的文件夹; mf 监控微信小程序更新包")

    # 添加可选参数
    parser.add_argument("--config-file", default=r'./config/config.yaml', help="指定配置文件路径, default： ./config/config.yaml")
    parser.add_argument("--wxid", help="微信小程序的 AES secret key")
    parser.add_argument("--folder-path", help="指定的包或文件夹路径")

    # 解析命令行参数
    args = parser.parse_args()

    config = config.load_config(config_yaml_path=args.config_file)

    if args.mode == 'sp':
        if args.folder_path is None:
            print("请用 --folder-path 指定文件")
            exit(1)
        Applet_Packet_Save_Folder = unwxapkg.unveilr_unpacket(args.folder_path, args.wxid, config['File_Config'])
        infoFinder.infoFinder(Applet_Packet_Save_Folder)
    elif args.mode == 'mf':
        unwxapkg.monitor_folder(config)
    elif args.mode == 'sf':
        if args.folder_path is None:
            print("请用 --folder-path 指定文件")
            exit(1)
        infoFinder.infoFinder(args.folder_path, config)
