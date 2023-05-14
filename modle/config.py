import yaml


def load_config(config_yaml_path=None, load_type=None):
    if config_yaml_path is None:
        return False
    with open(config_yaml_path, 'r', encoding='utf-8') as f:
        config = list(yaml.load_all(f.read(), Loader=yaml.FullLoader))[0]
        if load_type is None:
            return config
        elif load_type in config:
            return config[load_type]
        else:
            return False


if __name__ == '__main__':
    # 加载配置文件，并且设置为全局参数
    config_yaml = r'../config/config.yaml'

    # all_config = load_config(config_yaml)
    # globals().update(all_config)  # 设置为全局参数
    # print(all_config)
    #
    # File_Config = load_config(config_yaml, load_type='File_Config')
    # print(File_Config)
    #
    # Regex_Config = load_config(config_yaml, load_type='Regex_Config')
    # print(Regex_Config)
    Request_Config = load_config(config_yaml, load_type='Request_Config')
    if not Request_Config['allow_redirects']:
        print(1)
