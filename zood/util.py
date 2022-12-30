
import yaml
import os

def readConfigFile(file_name):
    '''
    open config.yaml and return configuration
    '''
    with open(file_name, 'r', encoding="utf-8") as f:
        file_data = f.read()

    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def writeConfigFile(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def initZoodInfo():
    zood_path = os.path.join(os.path.dirname(__file__),'config','zood.yml')
    zood = readConfigFile(zood_path)
    current_dir = os.getcwd()

    if current_dir not in zood['MD_DOC_PATH']:
        zood['MD_DOC_PATH'].append(current_dir)
    zood[current_dir] = {}
    zood[current_dir]['DIR'] = {}
    writeConfigFile(zood,zood_path)
    
def getSortNumber(dir_name):
    
    zood_path = os.path.join(os.path.dirname(__file__),'config','zood.yml')
    zood = readConfigFile(zood_path)
    current_dir = os.getcwd()
    
    if dir_name in zood[current_dir]['DIR']:
        number = zood[current_dir]['DIR'][dir_name] + 1
        zood[current_dir]['DIR'][dir_name] += 1
        writeConfigFile(zood,zood_path)
        return number
    else:
        zood[current_dir]['DIR'][dir_name] = 1
        writeConfigFile(zood,zood_path)
        return 1

def updateDirYml(dir_name,md_dir_name):
    dir_sort = getSortNumber('md-docs')
    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir,md_dir_name,'dir.yml')
    dir_yml = readConfigFile(dir_yml_path)
    dir_yml['DIR'][dir_name] = dir_sort
    writeConfigFile(dir_yml,dir_yml_path)


def printInfo(msg,color='red'):
    if color == 'red':
        print(f'\033[1;31m{msg}\033[0m')
    elif color == 'green':
        print(f'\033[1;32m{msg}\033[0m')
        