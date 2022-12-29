
import yaml


def ReadConfigFile(file_name):
    '''
    open config.yaml and return configuration
    '''
    with open(file_name, 'r', encoding="utf-8") as f:
        file_data = f.read()

    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def WriteConfigFile(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

def printInfo(msg,color='red'):
    if color == 'red':
        print(f'\033[1;31m{msg}\033[0m')
    elif color == 'green':
        print(f'\033[1;32m{msg}\033[0m')
        