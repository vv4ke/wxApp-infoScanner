import os
import time

path_to_watch = r"H:\WeChat Files\WeChat Files"  # 替换为您要监视的文件夹路径
before = dict([(f, None) for f in os.listdir(path_to_watch)])

while True:
    time.sleep(10)  # 每隔10秒钟检查一次
    after = dict([(f, None) for f in os.listdir(path_to_watch)])
    added = [f for f in after if not f in before]
    if added:
        print("New folder(s) created:", ", ".join(added))
    before = after
