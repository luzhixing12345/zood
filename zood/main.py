
import argparse
import os
import shutil

from .util import *
from .md_parser import parseDocs
from .zood import *

version = "0.3.1"

def main():
    
    parser = argparse.ArgumentParser(
        description='zood: web page documentation & comment generation documentation'
    )
    parser.add_argument('cmd',type=str,nargs='*',help='initialize docs template')
    parser.add_argument('-g','--generate',action='store_true',help='generate html doc')
    parser.add_argument('-s','--save',action='store_true',help='save _config.yml and use in every environment')
    args = parser.parse_args()
    
    config = getZoodConfig()
    md_dir_name = config['markdown_folder']
    
    local_config_path = os.path.join(md_dir_name,'_config.yml')
    global_config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
    
    global version
    
    if args.generate:
        if not os.path.exists(md_dir_name):
            printInfo("请先使用 zood init 初始化")
            return
        parseDocs(md_dir_name)
        return
    
    if args.save:
        if os.path.exists(local_config_path):
            shutil.copy(local_config_path,global_config_path)
            printInfo("已更新全局配置文件 _config.yml",color='green')
        else:
            print('未找到',local_config_path)
        
        if os.path.exists(os.path.join(md_dir_name,'prismjs')):
            global_prism_css_path = os.path.join(os.path.dirname(__file__),'config','js','prismjs','prism.css')
            global_prism_js_path = os.path.join(os.path.dirname(__file__),'config','js','prismjs','prism.js')
            shutil.copy(os.path.join(md_dir_name,'prismjs','prism.css'),global_prism_css_path)
            shutil.copy(os.path.join(md_dir_name,'prismjs','prism.js'),global_prism_js_path)
            printInfo("已更新全局配置文件 prismjs")
        else:
            print('未找到',os.path.join(md_dir_name,'prismjs'))

        return

    if len(args.cmd) == 0:
        print('zood使用方法见 https://luzhixing12345.github.io/zood/')
        return
    
    if args.cmd[0] == 'init':
        
        initZood(md_dir_name)
        
    elif args.cmd[0] == 'new':
        if len(args.cmd) == 2:
            dir_name = '.'
            file_name = args.cmd[1]
        elif len(args.cmd) == 3:
            dir_name = args.cmd[1]
            file_name = args.cmd[2]
            if dir_name == md_dir_name:
                printInfo(f"您不能创建一个和 {md_dir_name} 同名的子文件夹")
                return
        else:
            printInfo(f"创建新文件的命令为 zood new [目录] [文件名]")
            return
        
        if not os.path.exists(md_dir_name):
            initZood(md_dir_name)

        createNewFile(md_dir_name,dir_name,file_name)
    
    elif args.cmd[0] == 'clean':
        shutil.rmtree('docs')
        printInfo(f"已删除 docs")
        
    elif args.cmd[0] == 'config':
        shutil.copy(global_config_path,local_config_path)
        printInfo(f"生成配置文件 {local_config_path}",color='green')
        
    # elif args.cmd[0] == 'update':
    #     print(f"当前zood版本为 {version}, 正在查询最新zood版本...")
    #     latest_zood_version = versions('zood')[0]
    #     print(f'最新zood版本为', latest_zood_version)
    #     if latest_zood_version == version:
    #         return
    #     else:
    #         download = input(f'是否要下载最新版 zood=={latest_zood_version} (yes/no)[yes] ')
    #         if download == '' or download == 'yes':
    #             print('正在准备更新...')
    #             try:
    #                 os.system('pip install --upgrade zood')
    #                 print('完成更新')
    #             except:
    #                 print('更新异常,请检查网络或代理,使用 pip install --upgrade zood 更新')
                
    #         else:
    #             print('退出更新程序')
                
    # elif args.cmd[0] == 'version':
    #     print(f"当前zood版本为 {version}")

    else:
        print(f'未找到指令 zood {args.cmd[0]}')