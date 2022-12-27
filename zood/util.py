
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
