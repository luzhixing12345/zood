
import os
import time
import re
import shutil
from .MarkdownParser import parse
from .util import ReadConfigFile


def checkHeader(md_tree,file_name):
    
    md_info = {}
    if md_tree.sub_blocks[0].block_name == 'SplitBlock' \
        and md_tree.sub_blocks[1].block_name == 'ParagraphBlock' \
        and md_tree.sub_blocks[2].block_name == 'SplitBlock':
            pre_header = md_tree.sub_blocks[1].sub_blocks[0].input['text']
            match_groups = re.match('(.*?):(.*)',pre_header)
            key = match_groups.group(1)
            number = match_groups.group(2)
            if key != 'sort':
                print(f'\033[1;31m[zood解析错误]\033[0m\n文件 {file_name} 中 \"{pre_header}\" 不符合zood解析规范,请使用 sort: <数字>')
                exit(0)
            try:
                number = int(number)
                md_info['sort'] = number
                md_tree.sub_blocks = md_tree.sub_blocks[3:]
                modify_time = time.localtime(os.stat(file_name).st_mtime)
                md_info['modify_time'] = time.strftime("%Y-%m-%d %H:%M:%S",modify_time)
                md_info['content'] = md_tree.toHTML()
                return md_info
            except:
                print('\033[1;31m[zood解析错误]\033[0m')
                print(f'文件 {file_name} 中 \"{pre_header}\" 不符合zood解析规范,请使用 sort: <数字>')
                exit(0)
    else:
        print('\033[1;31m[zood解析错误]\033[0m')
        print(f'文件 {file_name} 文件头不符合zood解析规范,请在文件开头使用如下格式创建排序')
        print('---\nsort: <数字>\n---')
        exit(0)

def parseDocs(dir_name):
    
    directory_tree = {'root':[]}
    # 只支持二级目录
    for root, dirs, files in os.walk(dir_name):
        
        if dirs != []:
            # md-docs根目录
            md_files = []
            for file in files:
                if file.endswith('md'):
                    md_files.append(file)
            directory_tree['root'] = md_files
            for dir in dirs:
                directory_tree[dir] = []
        else:
            dir = root.split(os.sep)[-1]
            md_files = []
            for file in files:
                if file.endswith('md'):
                    md_files.append(file)
            directory_tree[dir] = md_files
    
    config_file_path = os.path.join(dir_name,'_config.yml')
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(config_file_path)
    
    config_file = ReadConfigFile(config_file_path)
    
    for dir, files in directory_tree.items():
        for i in range(len(files)):
            file = files[i]
            if dir == 'root':
                dir = ''
            file_path = os.path.join(dir_name,dir,file)
            with open(file_path,'r',encoding='utf-8') as f:
                md_tree = parse(f.read())
            md_info = checkHeader(md_tree,file_path)
            md_info['name'] = file
            files[i] = md_info
        files.sort(key=lambda item:item['sort'])
        
    generateDocs(directory_tree,config_file)
    
    
def generateDocs(directory_tree,config_file):
    if os.path.exists('docs'):
        print("重新生成/docs")
        shutil.rmtree("docs")
    os.makedirs('docs/articles')
    os.makedirs('docs/js')
    os.makedirs('docs/css')
    os.makedirs('docs/img')
    
    html_tempate_path = os.path.join(os.path.dirname(__file__),'config','template.html')
    with open(html_tempate_path,'r',encoding='utf-8') as f:
        html_template = f.read()
    
    with open('docs/index.html','w',encoding='utf-8') as f:
        f.write(html_template)
    
    for dir, files in directory_tree.items():
        for md_info in files:
            dir_name = os.path.join("docs","articles",dir,md_info['name'].replace('.md',''))
            os.makedirs(dir_name)
            file_path = os.path.join(dir_name,'index.html')
            with open(file_path,'w',encoding='utf-8') as f:
                f.write(html_template.replace('html-scope',md_info['content']))