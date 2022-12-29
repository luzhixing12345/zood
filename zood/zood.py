
import shutil
import os

def parseConfig(config):
    
    html_tempate_path = os.path.join(os.path.dirname(__file__),'config','template.html')
    css_template_path = os.path.join(os.path.dirname(__file__),'config','index.css')
    
    with open(html_tempate_path,'r',encoding='utf-8') as f:
        basic_html_template = f.read()
    
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
    
    for k,v in config['color'].items():
        # print(k,v)
        basic_css_template = basic_css_template.replace(f'\"<%{k}%>\"',v)
    
    for k,v in config['font'].items():
        # print(k,v)
        basic_css_template = basic_css_template.replace(f'\"<%{k}%>\"',v)
    
    with open('./docs/css/index.css','w',encoding='utf-8') as f:
        f.write(basic_css_template)
    
    return basic_html_template
