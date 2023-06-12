
'''
这个文件的作用是更新 PYPI 包, 修改 pyproject.toml 的 VERSION 版本号并发布, 相当于 poetry build + poetry publish

使用方法

    python update.py                  发布版本更新
    python update.py sub              次版本更新
    python update.py main             主版本更新

'''

import shutil
import re,os


def print_info(msg,color='red'):
    if color == 'red':
        print(f'\033[1;31m{msg}\033[0m')
    elif color == 'green':
        print(f'\033[1;32m{msg}\033[0m')
    else:
        print("未知 color: (red, green)")

def update_package(choice = None):
    '''
    choice = None(default) 发布版本更新
    choice = sub           次版本更新
    choice = main          主版本更新
    '''

    pwd = os.getcwd()
    pyproject_path = os.path.join(pwd, 'pyproject.toml')
    if not os.path.exists(pyproject_path):
        print("pyproject.toml 不存在")
        return

    try:
        shutil.rmtree("dist")
        print('delete dist')
    except:
        pass

    with open(pyproject_path,'r', encoding='utf-8') as f:
        file = f.read()

    old_version_re = re.search(r'version = \"(\d+)\.(\d+)\.(\d+)\"',file)
    MAIN_VERSION, SUB_VERSION, FIX_VERSION = int(old_version_re.group(1)),int(old_version_re.group(2)),int(old_version_re.group(3))

    old_version = f'{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}'

    if choice is None:
        FIX_VERSION = FIX_VERSION + 1
    elif choice == 'sub':
        SUB_VERSION = SUB_VERSION + 1
        FIX_VERSION = 0
    elif choice == 'main':
        MAIN_VERSION = MAIN_VERSION + 1
        SUB_VERSION = 0
        FIX_VERSION = 0

    new_version = f'{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}'

    new_version_str = f'version = \"{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}\"'
    new_content = re.sub(r'version = \"(\d+)\.(\d+)\.(\d+)\"',new_version_str,file)
    with open(pyproject_path,'w',encoding='utf-8') as f:
        f.write(new_content)
    
    print(f'{old_version} -> {new_version}')

    try:
        os.system("poetry build")
        os.system("poetry publish")
        print_info("更新成功", color='green')
    except:
        print_info("库更新失败, pyproject.toml 版本已回退")
        with open(pyproject_path,'w',encoding='utf-8') as f:
            f.write(file)