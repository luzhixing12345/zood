
import os
import time
import re
import shutil
from .MarkdownParser import parse
from .util import *
from .zood import parseConfig


def checkHeader(md_tree,file_name):
    
    md_info = {}
    if md_tree.sub_blocks[0].block_name == 'SplitBlock' \
        and md_tree.sub_blocks[1].block_name == 'ParagraphBlock' \
        and md_tree.sub_blocks[2].block_name == 'SplitBlock':
            zood_header = ''
            for block in md_tree.sub_blocks[1].sub_blocks:
                zood_header += block.input['text'] + '\n'
            match_groups = re.findall('(.*?): (.*)',zood_header)
            try:
                title = match_groups[0][1]
                date = match_groups[1][1]
                md_tree.sub_blocks = md_tree.sub_blocks[3:]
                # modify_time = time.localtime(os.stat(file_name).st_mtime)
                # md_info['modify_time'] = time.strftime("%Y-%m-%d %H:%M:%S",modify_time)
                md_info['title'] = title
                md_info['date'] = date
                md_info['content'] = md_tree.toHTML()
                return md_info
            except:
                printInfo('[zood解析错误]')
                print(f'文件 {file_name} 头不符合zood解析规范')
                exit(0)
    else:
        printInfo('[zood解析错误]')
        print(f'文件 {file_name} 头不符合zood解析规范')
        exit(0)

def parseDocs(dir_name):
    
    directory_tree = {}
    # 只支持二级目录
    for root, dirs, files in os.walk(dir_name):
        
        dir = root.split(os.sep)[-1]
        md_files = []
        for file in files:
            if file.endswith('md'):
                md_files.append(file)
        directory_tree[dir] = md_files
    
    # config_file_path = os.path.join(dir_name,'_config.yml')
    # if not os.path.exists(config_file_path):
    #     raise FileNotFoundError(config_file_path)
    
    # config_file = ReadConfigFile(config_file_path)
    # print(directory_tree)
    for dir, files in directory_tree.items():
        for i in range(len(files)):
            file = files[i]
            if dir == 'md-docs':
                dir = ''
            file_path = os.path.join(dir_name,dir,file)
            with open(file_path,'r',encoding='utf-8') as f:
                md_tree = parse(f.read())
            md_info = checkHeader(md_tree,file_path)
            md_info['name'] = file
            files[i] = md_info
        files.sort(key=lambda item:item['date'])
        
    generateDocs(directory_tree)
    
    
def generateDocs(directory_tree):
    if os.path.exists('docs'):
        print("重新生成/docs")
        shutil.rmtree("docs")
    os.makedirs('docs/articles')
    os.makedirs('docs/js')
    os.makedirs('docs/css')
    os.makedirs('docs/img')
    
    zood_config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
    zood_config = ReadConfigFile(zood_config_path)
    
    html_template = parseConfig(zood_config)
    
    for dir, files in directory_tree.items():
        for md_info in files:
            dir_name = os.path.join("docs","articles",dir,md_info['name'].replace('.md',''))
            os.makedirs(dir_name)
            file_path = os.path.join(dir_name,'index.html')
            with open(file_path,'w',encoding='utf-8') as f:
                f.write(html_template.replace('html-scope',md_info['content']))