
import shutil
import os
from .MarkdownParser import parse
from .util import *

def initZood(md_dir_name):
    # 初始化 zood 文件
    
    if os.path.exists(md_dir_name):
        printInfo(f"{md_dir_name} 已存在,请删除文件夹后重试")
        return
    else:
        
        os.mkdir(md_dir_name)

        readme = ''
        if os.path.exists('README.md'):
            with open('README.md','r',encoding='utf-8') as f:
                readme = f.read()
        with open('.gitignore','a+',encoding='utf-8') as f:
            gitignore_files = f.read()
            if gitignore_files.find(f'/{md_dir_name}/') != -1:
                gitignore_files += f'\n/{md_dir_name}/\n'
                f.write(gitignore_files)

        initDirYml(md_dir_name)

        with open(os.path.join(md_dir_name,'README.md'),'w',encoding='utf-8') as f:
            f.write(readme)

        printInfo(f"已初始化 [{md_dir_name}]",'green')

def createNewFile(md_dir_name,dir_name,file_name):
    
    file_path = os.path.join(md_dir_name,dir_name,file_name+'.md')
        
    if os.path.exists(file_path):
        printInfo(f'{file_path} 已存在')
        return
    
    if not os.path.exists(os.path.join(md_dir_name,dir_name)):
        os.makedirs(os.path.join(md_dir_name,dir_name))
    
    updateDirYml(file_name,dir_name,md_dir_name)

    with open(file_path,'w',encoding='utf-8') as f:
        basic_info = f'\n# {file_name}\n'
        f.write(basic_info)
    
    printInfo(f"创建文件 {file_path}",color='green')

def initDirYml(md_dir_name):
    # 生成目录记录
    dir_yml = {'.':[{'README':1}]}
    writeConfigFile(dir_yml,os.path.join(md_dir_name,'dir.yml'))

def updateDirYml(file_name,dir_name,md_dir_name):
    # 更新当前路径下的 dir.yml

    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir,md_dir_name,'dir.yml')
    dir_yml = readConfigFile(dir_yml_path)
    
    sort(dir_yml)
    
    if dir_name in dir_yml.keys():
        number = list(dir_yml[dir_name][-1].values())[0] + 1
        dir_yml[dir_name].append({file_name:number})
    else:
        dir_yml[dir_name] = []
        dir_yml[dir_name].append({file_name:1})
    
    writeConfigFile(dir_yml,dir_yml_path)

def parseMarkdownFiles(md_dir_name):
    
    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir,md_dir_name,'dir.yml')
    dir_yml = readConfigFile(dir_yml_path)
    sort(dir_yml)
    directory_tree = []
    markdown_htmls = {}
    for dir_name, files in dir_yml.items():
        file_names = []
        for i in files:
            file_name = list(i.keys())[0]
            file_path = os.path.join(md_dir_name,dir_name,file_name+'.md')
            if not os.path.exists(file_path):
                printInfo('[zood解析失败]: 请检查 dir.yml')
                printInfo('找不到文件 ' + file_path)
                exit(0)
            else:
                with open(file_path,'r',encoding='utf-8') as f:
                    markdown_htmls[file_path] = parse(f.read())
                file_names.append(file_name)
        directory_tree.append({dir_name:file_names})
        
    return directory_tree,markdown_htmls
            

def parseConfig(config):
    
    html_dir_name = config['html_folder']
    html_tempate_path = os.path.join(os.path.dirname(__file__),'config','template.html')
    css_template_path = os.path.join(os.path.dirname(__file__),'config','index.css')
    
    with open(html_tempate_path,'r',encoding='utf-8') as f:
        basic_html_template = f.read()
    
    
    # js 部分
    js_scope = zoodJSOptions(config)
    basic_html_template = basic_html_template.replace('js-scope',js_scope)
    
    # css 部分

    prism_src = '../../../css/prism.css'
    index_src = '../../../css/index.css'

    css_scope = ''
    css_scope += f"<link rel='stylesheet' href={prism_src} />"
    css_scope += f"<link rel='stylesheet' href={index_src} />"
    basic_html_template = basic_html_template.replace('css-scope',css_scope)
    
    with open(css_template_path,'r',encoding='utf-8') as f:
        basic_css_template = f.read()
    favicon_url = config['favicon']
    if favicon_url[:4] == 'http':
        basic_html_template = basic_html_template.replace('<%favicon%>',favicon_url)
    else:
        img_name = favicon_url.split(os.sep)[-1]
        shutil.copy(favicon_url,f'./{html_dir_name}/img/'+img_name)
        basic_html_template = basic_html_template.replace('<%favicon%>','../../../img/'+img_name)
        
    title = config['title']
    basic_html_template = basic_html_template.replace('<%title%>',title)
    
    custom_options = getCustomOptions(config,['color','font','position'])
    
    for k,v in custom_options:
        basic_css_template = basic_css_template.replace(f'\"<%{k}%>\"',v)
        
    
    basic_html_template = basic_html_template.replace('css-scope',css_scope)
    
    with open(f'./{html_dir_name}/css/index.css','w',encoding='utf-8') as f:
        f.write(basic_css_template)
    
    return basic_html_template

def getCustomOptions(config,keys):
    
    custom_options = []
    for k in keys:
        custom_options += list(config[k].items())
    return custom_options

def zoodJSOptions(config):
    
    js_scope = ''
    html_dir_name = config['html_folder']

    if config['options']['enable_change_mode']:
    
        js_code = insertJScode('enable_change_mode',html_dir_name)
        js_code += f"<script>addChangeModeButton(\"../../../img/sun.png\",\"../../../img/moon.png\")</script>"
        js_scope += js_code
        
    if config['options']['enable_copy_code']:
        
        js_code = insertJScode('enable_copy_code',html_dir_name)
        js_code += f"<script>addCodeCopy(\"../../../img/before_copy.png\",\"../../../img/after_copy.png\")</script>"
        js_scope += js_code
        
    if config['options']['enable_highlight']:
        # 复制prismjs
        shutil.copy(os.path.join(os.path.dirname(__file__),'config','js','prismjs','prism.css'),f'{html_dir_name}/css')
        shutil.copy(os.path.join(os.path.dirname(__file__),'config','js','prismjs','prism.js'),f'{html_dir_name}/js')
        src = "../../../js/prism.js"
        highlight = f"<script type=\"text/javascript\" src=\"{src}\"></script>"
        js_scope += highlight
        
    if config['options']['enable_next_front']:
        js_code = insertJScode('enable_next_front',html_dir_name)
        js_code += f"<script>addLink(<%front_url%>,<%next_url%>,<%control%>)</script>"
        js_scope += js_code
        
    if config['options']['enable_picture_title']:
        js_code = insertJScode('enable_picture_title',html_dir_name)
        js_scope += js_code
        
    if config['options']['enable_picture_preview']:
        js_code = insertJScode('enable_picture_preview',html_dir_name)
        js_scope += js_code

    js_scope += insertJScode('enable_check_box',html_dir_name)

    return js_scope

def insertJScode(file_name,html_dir_name):
    file_name = file_name[7:]
    shutil.copy(os.path.join(os.path.dirname(__file__),'config','js',f'{file_name}.js'),f'{html_dir_name}/js')
    src = f"../../../js/{file_name}.js"
    js_code = f"<script type=\"text/javascript\" src=\"{src}\"></script>"
    return js_code
        

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