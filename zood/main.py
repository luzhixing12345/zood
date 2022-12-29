
import argparse
import os
import time

from .util import printInfo
from .md_parser import parseDocs

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
        
        if os.path.exists(md_dir_name):
            printInfo(f"{md_dir_name} 已存在,请删除文件夹后重试")
            return
        else:
            printInfo(f"已初始化 [{md_dir_name}]",'green')
            os.mkdir(md_dir_name)
            # config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
            # with open(config_path,'r',encoding='utf-8') as f:
            #     config = f.read()
            # with open(os.path.join(md_dir_name,'_config.yml'),'w',encoding='utf-8') as f:
            #     f.write(config)

            with open('.gitignore','a+',encoding='utf-8') as f:
                text = f.read()
                if not text.find(md_dir_name):
                    f.write('\n/md-docs/')

            # if os.path.exists('README.md'):
            #     with open('README.md','r',encoding='utf-8') as f:
            #         readme = f.read()
            # else:
            #     readme = ''
            # with open(os.path.join(md_dir_name,'index.md'),'w',encoding='utf-8') as f:
            #     f.write(readme)
    
    elif args.cmd[0] == 'new':
        if len(args.cmd) == 2:
            dir_name = '.'
            file_name = args.cmd[1]
        elif len(args.cmd) == 3:
            dir_name = args.cmd[1]
            file_name = args.cmd[2]
        else:
            printInfo(f"创建新文件的命令为 zood new [目录] [文件名]")
            return    

        file_path = os.path.join('md-docs',dir_name,file_name+'.md')
        if os.path.exists(file_path):
            printInfo(f'{file_path} 已存在')
            return
        if not os.path.exists(os.path.join('md-docs',dir_name)):
            os.makedirs(os.path.join('md-docs',dir_name))
        title = file_name
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(file_path,'w',encoding='utf-8') as f:
            basic_info = f'---\ntitle: {title}\ndate: {date}\n---\n\n# {title}\n'
            f.write(basic_info)
    
    

if __name__ == "__main__":
    main()