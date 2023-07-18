import json
import os
import time
import platform
import subprocess
import config
from modle import infoFinder


def monitor_folder(all_config):
    File_Config = all_config['File_Config']
    WX_Applet_Path = File_Config['WX_Applet_Path']

    before = dict([(f, None) for f in os.listdir(WX_Applet_Path)])
    print(before)

    while True:
        time.sleep(File_Config['Sleep_Time'])  # 间隔休眠再检查一次
        after = dict([(f, None) for f in os.listdir(WX_Applet_Path)])
        added = [f for f in after if not f in before]
        if added:
            print("New folder(s) created:", ", ".join(added))
            for son_folder in added:
                print("等待程序下载...")
                time.sleep(File_Config['Sleep_Time'])   # 等待程序下载
                Applet_Packet_Save_Folder = unveilr_unpacket(WX_Applet_Path, son_folder, File_Config)
                infoFinder.infoFinder(Applet_Packet_Save_Folder, all_config)
        else:
            print(before)
        before = after


def unveilr_unpacket(mon_folder='', son_folder='', File_Config=None):

    print('开始解包和反编译咯')

    current_path = os.getcwd()
    wx_secret = son_folder
    Applet_Packet_Save_Folder = os.path.join(current_path, File_Config['Applet_Packet_Save_Path'], wx_secret)  # 反编译代码存放木佬
    applet_packet_config_path = os.path.join(Applet_Packet_Save_Folder, 'app.json')  # 小程序配置文件

    # cmd: .\unveilr@2.0.1-win-x64 wx 'app_path' -d 2 -o 'output_path'
    cmd = f"cd {File_Config['Unveilr_Path']};./{File_Config['Unveilr_Program_Name']} " \
          f"wx '{os.path.join(mon_folder, son_folder)}' " \
          f"-d {File_Config['Unveilr_Depth']} " \
          f"-o '{Applet_Packet_Save_Folder}' " \
          f"--clear-output"
    if platform.system() == 'Windows':
        cmd = 'powershell;' + cmd

    # 运行unveilr
    sub = subprocess.run(cmd, shell=True, encoding='utf-8')
    while True:
        if sub.returncode == 0:
            break

    # 重命名一下包名，提高可阅读性
    time.sleep(1)
    try:
        with open(applet_packet_config_path, 'r', encoding='utf-8') as f:
            app_name = json.loads(f.read())['window']['navigationBarTitleText']
    except:
        app_name = ''
    New_Applet_Packet_Save_Folder = os.path.join(current_path, File_Config['Applet_Packet_Save_Path'], f"{app_name}_{wx_secret}_{time.strftime('%Y_%m_%d_%H_%M_%S')}")
    os.rename(Applet_Packet_Save_Folder, New_Applet_Packet_Save_Folder)
    print(f'解包和反编译搞定：{New_Applet_Packet_Save_Folder}')
    return New_Applet_Packet_Save_Folder


if __name__ == '__main__':
    config_yaml = r'./config.yaml'
    all_Config = config.load_config(config_yaml)
    monitor_folder(all_Config)
