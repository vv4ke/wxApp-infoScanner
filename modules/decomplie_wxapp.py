import yaml
import time
import os
import platform
import subprocess
import json


class DecompileWxApp(object):
    def __init__(self, config_path, root_path=r''):
        # 加载config.yaml 中的反编译配置
        print('init DecompileWxApp')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = list(yaml.load_all(f.read(), Loader=yaml.FullLoader))[0]['File_Config']
        self.root_path = root_path
        self.config_path = config_path

    def unveilr_decompile(self, mon_folder='', son_folder=''):

        print('开始解包和反编译咯')

        wx_secret = son_folder
        # 反编译获得的代码存放位置
        wx_app_code_save_path = os.path.join(self.root_path, self.config['Applet_Packet_Save_Path'], wx_secret)
        # 小程序配置文件
        applet_packet_config_path = os.path.join(wx_app_code_save_path, 'app.json')

        # cmd: .\unveilr@2.0.1-win-x64 wx 'app_path' -d 2 -o 'output_path'
        cmd = f"cd {os.path.join(self.root_path ,self.config['Unveilr_Path'])};./{self.config['Unveilr_Program_Name']} " \
              f"wx '{os.path.join(mon_folder, son_folder)}' " \
              f"-d {self.config['Unveilr_Depth']} " \
              f"-o '{wx_app_code_save_path}' " \
              f"--clear-output"
        if platform.system() == 'Windows':
            cmd = 'powershell;' + cmd

        # 运行unveilr
        sub = subprocess.run(cmd, shell=True, encoding='utf-8')
        while True:
            if sub.returncode == 0:
                break
        time.sleep(1)

        # 重命名一下包名，提高可阅读性
        try:
            with open(applet_packet_config_path, 'r', encoding='utf-8') as f:
                app_name = json.loads(f.read())['window']['navigationBarTitleText']
        except:
            app_name = ''
        new_wx_app_code_save_path = os.path.join(self.root_path, self.config['Applet_Packet_Save_Path'],
                                                 f"{app_name}_{wx_secret}_{time.strftime('%Y_%m_%d_%H_%M_%S')}")
        os.rename(wx_app_code_save_path, new_wx_app_code_save_path)
        print(f'解包和反编译搞定：{new_wx_app_code_save_path}')
        return new_wx_app_code_save_path


if __name__ == '__main__':
    test = DecompileWxApp(r'../config.yaml', r'E:\CodeProject\wxApp-infoScanner')
    new_wx_app_code_save_path = test.unveilr_decompile(r'D:\software\WeChat\WeChat Files\WeChat Files\Applet', 'wx229fa2ad5c78548c')
    print(new_wx_app_code_save_path)
