
import shutil
import os

from .util import *

def initZood(md_dir_name):
    # 初始化 zood 文件
    
    if os.path.exists(md_dir_name):
        printInfo(f"{md_dir_name} 已存在,请删除文件夹后重试")
        return
    else:
        
        os.mkdir(md_dir_name)
        
        initZoodInfo()
        initDirYml(md_dir_name)
        
        readme = '---\ntitle: README\nsort: 1\n---\n\n'
        if os.path.exists('README.md'):
            with open('README.md','r',encoding='utf-8') as f:
                readme += f.read()

        with open(os.path.join(md_dir_name,'README.md'),'w',encoding='utf-8') as f:
            f.write(readme)

        printInfo(f"已初始化 [{md_dir_name}]",'green')

def initDirYml(md_dir_name):
    # 生成目录记录
    dir_yml = {'Sort':{'README.md':1}}
    writeConfigFile(dir_yml,os.path.join(md_dir_name,'dir.yml'))

def createNewFile(md_dir_name,dir_name,file_name):
    
    file_path = os.path.join(md_dir_name,dir_name,file_name+'.md')
        
    if os.path.exists(file_path):
        printInfo(f'{file_path} 已存在')
        return
    
    if not os.path.exists(os.path.join(md_dir_name,dir_name)):
        os.makedirs(os.path.join(md_dir_name,dir_name))
    
    file_sort_number, dir_sort_number = getSortNumber(dir_name)
    
    if dir_sort_number:
        updateDirYml(file_name,dir_name,dir_sort_number,md_dir_name)

    title = file_name
    with open(file_path,'w',encoding='utf-8') as f:
        basic_info = f'---\ntitle: {title}\nsort: {file_sort_number}\n---\n\n# {file_name}\n'
        f.write(basic_info)
    
    printInfo(f"创建文件 {file_path}",color='green')


def initZoodInfo():
    # 将当前路径加入到 zood.yml
    
    zood_path = os.path.join(os.path.dirname(__file__),'config','zood.yml')
    zood = readConfigFile(zood_path)
    current_dir = os.getcwd()

    if current_dir not in zood['MD_DOC_PATH']:
        zood['MD_DOC_PATH'].append(current_dir)
    zood[current_dir] = {}
    zood[current_dir]['SORT_NUMBER'] = 1
    zood[current_dir]['DIR'] = {}
    writeConfigFile(zood,zood_path)
    
def getSortNumber(dir_name):
    # 得到当前文件在所在文件夹中的排序
    # 并且更新 zood.yml
    
    zood_path = os.path.join(os.path.dirname(__file__),'config','zood.yml')
    zood = readConfigFile(zood_path)
    current_dir = os.getcwd()
    
    file_sort_number = None
    dir_sort_number = None
    
    if dir_name in zood[current_dir]['DIR']:
        file_sort_number = zood[current_dir]['DIR'][dir_name] + 1
        zood[current_dir]['DIR'][dir_name] += 1
    else:
        if dir_name == '.':
            file_sort_number = zood[current_dir]['SORT_NUMBER'] + 1
            dir_sort_number = file_sort_number
            zood[current_dir]['SORT_NUMBER'] += 1
        else:
            file_sort_number = 1
            dir_sort_number = zood[current_dir]['SORT_NUMBER'] + 1
            zood[current_dir]['SORT_NUMBER'] += 1
            zood[current_dir]['DIR'][dir_name] = 1
            
    writeConfigFile(zood,zood_path)
    return file_sort_number, dir_sort_number

def updateDirYml(file_name,dir_name,sort_number,md_dir_name):
    # 更新当前路径下的 dir.yml

    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir,md_dir_name,'dir.yml')
    dir_yml = readConfigFile(dir_yml_path)
    if dir_name == '.':
        dir_yml['Sort'][file_name] = sort_number
    else:
        dir_yml['Sort'][dir_name] = sort_number
    writeConfigFile(dir_yml,dir_yml_path)




def parseConfig(config):
    
    html_tempate_path = os.path.join(os.path.dirname(__file__),'config','template.html')
    css_template_path = os.path.join(os.path.dirname(__file__),'config','index.css')
    
    with open(html_tempate_path,'r',encoding='utf-8') as f:
        basic_html_template = f.read()
    
    js_scope = zoodJSOptions(config)
    
    basic_html_template = basic_html_template.replace('js-scope',js_scope)
    
    with open(css_template_path,'r',encoding='utf-8') as f:
        basic_css_template = f.read()
        
    favicon_url = config['favicon']
    if favicon_url[:4] == 'http':
        basic_html_template = basic_html_template.replace('<%favicon%>',favicon_url)
    else:
        img_name = favicon_url.split(os.sep)[-1]
        shutil.copy(favicon_url,'./docs/img/'+img_name)
        basic_html_template = basic_html_template.replace('<%favicon%>','../../../img/'+img_name)
        
    title = config['title']
    basic_html_template = basic_html_template.replace('<%title%>',title)
    
    custom_options = getCustomOptions(config,['color','font','position'])
    
    for k,v in custom_options:
        # print(k,v)
        basic_css_template = basic_css_template.replace(f'\"<%{k}%>\"',v)
    
    with open('./docs/css/index.css','w',encoding='utf-8') as f:
        f.write(basic_css_template)
    
    return basic_html_template

def getCustomOptions(config,keys):
    
    custom_options = []
    for k in keys:
        custom_options += list(config[k].items())
    return custom_options

def zoodJSOptions(config):
    
    js_scope = ''
    if config['options']['enable_dark']:
    
        shutil.copy(os.path.join(os.path.dirname(__file__),'config','js','change_mode.js'),'docs/js')
        src = "../../../js/change_mode.js"
        change_mode = f"<script type=\"text/javascript\" src=\"{src}\"></script>"
        js_scope += change_mode
        
    if config['options']['copy_btn']:
        
        shutil.copy(os.path.join(os.path.dirname(__file__),'config','js','copy_code.js'),'docs/js')
        src = "../../../js/copy_code.js"
        change_mode = f"<script type=\"text/javascript\" src=\"{src}\"></script>"
        js_scope += change_mode
        
    if config['options']['enable_highlight']:
        # 复制prismjs
        shutil.copy(os.path.join(os.path.dirname(__file__),'config','js','prismjs','prism.css'),'docs/css')
        shutil.copy(os.path.join(os.path.dirname(__file__),'config','js','prismjs','prism.js'),'docs/js')
        src = "../../../js/prism.js"
        highlight = f"<script type=\"text/javascript\" src=\"{src}\"></script>"
        js_scope += highlight
        
    return js_scope