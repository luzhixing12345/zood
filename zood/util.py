
import yaml
import os

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
        