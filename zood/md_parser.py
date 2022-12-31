
import os
import shutil
from .util import *
from .zood import parseConfig,parseMarkdownFiles

def parseDocs(md_dir_name):
    
    directory_tree, markdown_htmls = parseMarkdownFiles(md_dir_name)
    generateDocs(directory_tree,markdown_htmls,md_dir_name)
 
    
def generateDocs(directory_tree,markdown_htmls,md_dir_name):

    if os.path.exists('docs'):
        printInfo("删除原 docs/",color='green')
        shutil.rmtree("docs")
    os.makedirs('docs/articles')
    os.makedirs('docs/js')
    os.makedirs('docs/css')
    os.makedirs('docs/img')
    
    # 复制图片
    for root,_,files in os.walk(os.path.join(os.path.dirname(__file__),'config','img')):
        for img in files:
            shutil.copy(os.path.join(root,img),'docs/img')
    
    zood_config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
    zood_config = readConfigFile(zood_config_path)
    
    html_template = parseConfig(zood_config)
    
    for file_path, markdown_html in markdown_htmls.items():
        dir_name = file_path.split(os.sep)[1]
        file_name = file_path.split(os.sep)[2].replace('.md','')
        if dir_name == '.':
            dir_name = md_dir_name
        doc_path = os.path.join("docs","articles",dir_name,file_name)
        os.makedirs(doc_path)
        file_path = os.path.join(doc_path,'index.html')
        with open(file_path,'w',encoding='utf-8') as f:
            f.write(html_template.replace('html-scope',markdown_html))
    printInfo("已生成 docs/",color='green')            
    