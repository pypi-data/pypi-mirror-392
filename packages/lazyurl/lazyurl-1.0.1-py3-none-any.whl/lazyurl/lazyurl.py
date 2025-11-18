import urllib
import urllib.parse as urlparse


def url_quote(url: str):
    """
    url编码
    """
    return urlparse.quote(url)


def url_unquote(url: str):
    """
    url解码
    """
    return urlparse.unquote(url)


def get_url_params(
        url: str
) -> dict:
    """
    获取url的params参数，返回dict形式
    """
    params_dict = dict()
    params_str = urlparse.urlsplit(url).query
    if params_str:
        params_str_split = params_str.split('&')
        for each in params_str_split:
            if '=' in each:
                each_split = each.split('=', maxsplit=1)
                params_dict[each_split[0]] = each_split[1]
            else:
                continue
    else:
        pass
    return params_dict


def url_info(
        url: str
):
    """
    获取url的基本信息
    :param url:
    :return:
    """
    ana_res = object
    url_info_dict = dict()
    url_info_dict['url'] = url
    if url:
        urlparse_obj = urlparse.urlsplit(url)
        print(urlparse_obj.query)
        url_info_dict['host'] = urlparse_obj.hostname  # 域名
        url_info_dict['path'] = urlparse_obj.path  # 路径
        url_info_dict['scheme'] = urlparse_obj.scheme  # 协议
        url_info_dict['params'] = get_url_params(url)
        ana_res.host = urlparse_obj.hostname
    else:
        pass
    return ana_res

class UrlInfo:
    def __init__(self, url: str):
        self.url = url
        if url.startswith('http://') or url.startswith('https://'):
            self.host = None
        else:
            if "/" not in url:
                self.host = url
        self.urlparse_obj = urlparse.urlsplit(url)

    def domain_ana(self):
        domain_dict = dict()
        if self.host is None:
            hostname = self.urlparse_obj.netloc
        else:
            hostname = self.host
        hostname_split = hostname.split('.')
        domain_dict["hostname"] = hostname
        domain_dict["hostname_split"] = hostname_split
        domain_dict["host_record"] = '.'.join(hostname_split[:len(hostname_split) - 2])
        domain_dict["domain"] = '.'.join(hostname_split[len(hostname_split) - 2:])
        return domain_dict

    @property
    def host_record(self):
        return self.domain_ana().get("host_record")

    @property
    def domain(self):
        return self.domain_ana().get("domain")



if __name__ == '__main__':
    test_url = "https://login.work.weixin.qq.com/wwlogin/monoApi/sso/login/reportOss?lang=zh_CN&ajax=1&f=json&random=636176"
    # res = url_info("https://login.work.weixin.qq.com/wwlogin/monoApi/sso/login/reportOss?lang=zh_CN&ajax=1&f=json&random=636176")
    print(UrlInfo(test_url).domain)