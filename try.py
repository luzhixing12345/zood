import json
from urllib import request
from pkg_resources import parse_version
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def versions(pkg_name):
    url = f'https://pypi.python.org/pypi/{pkg_name}/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    return releases


if __name__ == '__main__':
    # name = input() # 这个可以接收输入
    name = "request" # 这是要查询的库名称
    print("正在查询：{}".format(name))
    value_list = versions(name)
    print(value_list)