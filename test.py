import argparse

if __name__ == '__main__':
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser()

    parser.add_argument('-hook', action='store_true', help='启用 Hook 功能')

    # 解析命令行参数
    args = parser.parse_args()

    print(args.hook)

