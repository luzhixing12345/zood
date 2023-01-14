
import yaml
import os
import re
import json

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
        
def getZoodConfig():
    
    global_config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
    
    global_zood_config = readConfigFile(global_config_path)
    md_dir_name = global_zood_config['markdown_folder']
    
    local_config_path = os.path.join(md_dir_name,'_config.yml')
    if os.path.exists(local_config_path):
        config_path = local_config_path
    else:
        config_path = global_config_path
        
    return readConfigFile(config_path)

def caculateFrontNext(flat_paths:list,path,md_dir_name):

    dir_name = path.split(os.sep)[1]
    file_name = path.split(os.sep)[2].replace('.md','')
    if dir_name == '.':
        dir_name = md_dir_name
    path = os.path.join(dir_name,file_name)
    pos = flat_paths.index(path)
    
    front_url = '\".\"'
    next_url = '\".\"'
    
    if pos != 0 :
        front_url = htmlRelativeUrl(flat_paths[pos-1])
    if pos != len(flat_paths)-1:
        next_url = htmlRelativeUrl(flat_paths[pos+1])

    return front_url,next_url
    
def htmlRelativeUrl(url:str):
    new_url = url.replace(os.sep,'/')
    new_url = f'\"../../{new_url}\"'
    return new_url
    
def getDirTree(directory_tree,md_dir_name):
    tree_html = ''
    for item in directory_tree:
        dir_name = list(item.keys())[0]
        files = item[dir_name]
        if dir_name == '.':
            dir_name = md_dir_name
            for file in files:
                dir_url_link = f'../../{dir_name}/{file}'
                # print(dir_url_link)
                tree_html += treeItem(file,dir_url_link)
        else:
            sub_tree_html = ''
            for file in files:
                dir_url_link = f'../../{dir_name}/{file}'
                # print(dir_url_link)
                sub_tree_html += treeItem(file,dir_url_link)
                
            first_dir_url_link = f'../../{dir_name}/{files[0]}'
            tree_html += treeItem(dir_name + sub_tree_html,first_dir_url_link)
                
    # print(tree_html)
    return f'<div class=\"dir-tree\">{tree_html}</div>'

def treeItem(name,dir_url_link):
    link = f"<a href=\"{dir_url_link}\" >{name}</a>"
    return f'<ul><li>{link}</li></ul>'

def urlReplace(html_template,front_url,next_url,control):
    
    html_template = html_template.replace('<%front_url%>',front_url).replace('<%next_url%>',next_url)
    html_template = html_template.replace('<%control%>',f'\"{control}\"')
    return html_template

def getAllAPIText(markdown_htmls):
    # print(markdown_htmls)
    all_keys = markdown_htmls.keys()
    API_keys = []
    for key in all_keys:
        if key.split(os.sep)[1] == 'API':
            API_keys.append(key)
    API_text = {}
    for key in API_keys:
        markdown_text = re.sub(r'<.*?>','',markdown_htmls[key])
        path = '../../API/' + key.split(os.sep)[-1].replace('.md','')
        API_text[path] = markdown_text
    
    json_API_text = json.dumps(API_text).replace('\"','\\\"')
    return f'\"{json_API_text}\"'