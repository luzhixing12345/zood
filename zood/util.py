
import yaml
import os

import json
from urllib import request
from pkg_resources import parse_version
import ssl


def readConfigFile(file_path:str):
    if not os.path.exists(file_path):
        printInfo('找不到文件' + file_path)
        exit(0)
    
    with open(file_path, 'r', encoding="utf-8") as f:
        file_data = f.read()

    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def writeConfigFile(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f,allow_unicode=True)

def sort(yml):
    
    for _,files in yml.items():
        files.sort(key=lambda item: list(item.values())[0])

def printInfo(msg,color='red'):
    if color == 'red':
        print(f'\033[1;31m{msg}\033[0m')
    elif color == 'green':
        print(f'\033[1;32m{msg}\033[0m')
        
def getZoodConfig():
    
    global_config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
    
    global_zood_config = readConfigFile(global_config_path)
    md_dir_name = global_zood_config['markdown_folder']
    
    local_config_path = os.path.join(md_dir_name,'_config.yml')
    if os.path.exists(local_config_path):
        config_path = local_config_path
    else:
        config_path = global_config_path
        
    return readConfigFile(config_path)

def versions(pkg_name):
    ssl._create_default_https_context = ssl._create_unverified_context
    url = f'https://pypi.python.org/pypi/{pkg_name}/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    return sorted(releases, key=parse_version, reverse=True)
