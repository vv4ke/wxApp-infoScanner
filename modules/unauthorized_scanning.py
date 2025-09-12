import yaml
import re

from urllib.parse import urlparse


class UnauthorizedScanning(object):
    def __init__(self, config_path, root_path=r''):
        # 加载config.yaml 中的反编译配置
        print('init DecompileWxApp')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = list(yaml.load_all(f.read(), Loader=yaml.FullLoader))[0]['Request_Config']
        self.root_path = root_path
        self.config_path = config_path

    def url_filter(self, url_list):
        """
        根据 domain、ip、suffix、key_Blacklist 筛除 url
        筛除逻辑:
        考虑 domain 和 ip 存在黑白名单配置问题,两个独立筛除的,然后筛除结果汇总

        :param url_list:
        :return:
        """

        # 首先是domain筛除，判断启用白名单还是黑名单
        url_list_cache_01 = []
        for url in url_list:
            if self.config['host_filter_rule']['domain_rule']['allowed'] == "":
                for domain_black in self.config['host_filter_rule']['domain_rule']['disallowed']:
                    if domain_black.startswith('*') and domain_black[1:] in url:
                        pass
                    elif domain_black in url:
                        pass
                    else:
                        url_list_cache_01.append(url)
            else:
                for domain_white in self.config['host_filter_rule']['domain_rule']['allowed']:
                    if domain_white.startswith('*') and domain_white[1:] in url:
                        url_list_cache_01.append(url)
                    elif domain_white in url:
                        url_list_cache_01.append(url)
                    else:
                        pass

        # 在 url_list_cache_01 中筛选 ip，默认筛除内网IP，
        url_list_cache_02 = []
        for ip_filter_reg in self.config['host_filter_rule']['ip_filter_rule']:
            reg = re.compile(ip_filter_reg)
            for url in url_list_cache_01:
                if reg.search(url):
                    pass
                else:
                    url_list_cache_02.append(url)

        # 然后是 suffix 去除,去除一些静态资源文件
        url_list_cache_03 = []
        black_suffix = tuple(self.config['host_filter_rule']['black_uri_suffix_list'])
        for url in url_list_cache_02:
            path = urlparse(url).path
            if path.endswith(black_suffix):
                pass
            else:
                url_list_cache_03.append(url)

        # 最后是根据 key_Blacklist 去除
        url_list_cache_04 = []
        dangerous_keys = self.config['host_filter_rule']['dangerous_keys']
        for url in url_list_cache_03:
            if any(dangerous_key in url for dangerous_key in dangerous_keys):
                pass
            else:
                url_list_cache_04.append(url)

        return url_list_cache_04

    def uri_filter(self, uri_list):
        """
        根据 suffix、key_Blacklist 筛除 uri
        :param uri_list:
        :return:
        """
        uri_list_1 = []
        # for uri in uri_list:
        #     # for self.config


        return

    def stitch_url(self):
        """
        1、根据 url列表，提取出明显的接口地址，规则 .do\.php\.jsp\.html 等
        2、根据 url列表，提取出疑似的接口跟路由，规则 
        :return:
        """
        # 根据 base_url 和 uri_list，拼接 url
        return

    def clear_url_list(self):
        # url
        return

