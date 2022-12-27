
import argparse
import os

from .util import ReadConfigFile,WriteConfigFile
from .md_parser import parseDocs

def main():
    
    parser = argparse.ArgumentParser(
        description='zood: web page documentation & comment generation documentation'
    )
    parser.add_argument('init',type=str,nargs='?',help='initialize docs template')
    parser.add_argument('-g','--generate',action='store_true',help='generate html doc')
    parser.add_argument('-s','--save',action='store_true',help='save _config.yml and use in every environment')
    args = parser.parse_args()
    
    md_dir_name = 'md-docs'
    
    if args.init == 'init':
        
        if os.path.exists(md_dir_name):
            print(f"{md_dir_name} already exist")
            return
        else:
            print(f"init [{md_dir_name}]")
            os.mkdir(md_dir_name)
            config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
            with open(config_path,'r',encoding='utf-8') as f:
                config = f.read()
            with open(os.path.join(md_dir_name,'_config.yml'),'w',encoding='utf-8') as f:
                f.write(config)

            # with open('.gitignore','a',encoding='utf-8') as f:
            #     f.write('\nmd-docs/')

            if os.path.exists('README.md'):
                with open('README.md','r',encoding='utf-8') as f:
                    readme = f.read()
            else:
                readme = ''
            with open(os.path.join(md_dir_name,'README.md'),'w',encoding='utf-8') as f:
                f.write(readme)
    
    if args.generate:
        parseDocs(md_dir_name)

if __name__ == "__main__":
    main()