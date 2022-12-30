
import argparse
import os
import shutil

from .util import *
from .md_parser import parseDocs

def initZood(md_dir_name):
    
    if os.path.exists(md_dir_name):
        printInfo(f"{md_dir_name} 已存在,请删除文件夹后重试")
        return
    else:
        
        os.mkdir(md_dir_name)
        
        initZoodInfo()
        dir_sort = getSortNumber('md-docs')
        dir_yml = {'DIR':{'md-docs':dir_sort}}
        # with open('.gitignore','a+',encoding='utf-8') as f:
        #     text = f.read()
        #     if not text.find(md_dir_name):
        #         f.write('\n/md-docs/')
        writeConfigFile(dir_yml,os.path.join(md_dir_name,'dir.yml'))
        
        printInfo(f"已初始化 [{md_dir_name}]",'green')


def main():
    
    parser = argparse.ArgumentParser(
        description='zood: web page documentation & comment generation documentation'
    )
    parser.add_argument('cmd',type=str,nargs='*',help='initialize docs template')
    parser.add_argument('-g','--generate',action='store_true',help='generate html doc')
    parser.add_argument('-s','--save',action='store_true',help='save _config.yml and use in every environment')
    args = parser.parse_args()
    
    md_dir_name = 'md-docs'
    
    if args.generate:
        if not os.path.exists(md_dir_name):
            printInfo("请先使用 zood init 初始化")
            return
        parseDocs(md_dir_name)
        return

    if len(args.cmd) == 0:
        print('zood使用方法见 https://luzhixing12345.github.io/zood/')
        return
    
    if args.cmd[0] == 'init':
        
        initZood(md_dir_name)
        
    elif args.cmd[0] == 'new':
        if len(args.cmd) == 2:
            dir_name = 'md-docs'
            file_name = args.cmd[1]
        elif len(args.cmd) == 3:
            dir_name = args.cmd[1]
            file_name = args.cmd[2]
            if dir_name == 'md-docs':
                printInfo(f"您不能创建一个和md-docs同名的子文件夹")
                return
        else:
            printInfo(f"创建新文件的命令为 zood new [目录] [文件名]")
            return
        
        if not os.path.exists(md_dir_name):
            initZood(md_dir_name)

        file_path = os.path.join('md-docs',dir_name,file_name+'.md')
        if os.path.exists(file_path):
            printInfo(f'{file_path} 已存在')
            return
        if not os.path.exists(os.path.join('md-docs',dir_name)):
            os.makedirs(os.path.join('md-docs',dir_name))
        
        sort = getSortNumber(dir_name)
        
        updateDirYml(dir_name,md_dir_name)
        title = file_name
        with open(file_path,'w',encoding='utf-8') as f:
            basic_info = f'---\ntitle: {title}\nsort: {sort}\n---\n\n# {file_name}\n'
            f.write(basic_info)
        
        printInfo(f"创建文件 {file_path}",color='green')
    
    elif args.cmd[0] == 'clean':
        shutil.rmtree('docs')
        printInfo(f"已删除 docs")

if __name__ == "__main__":
    main()