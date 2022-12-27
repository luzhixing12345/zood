
import argparse
import os

def main():
    
    parser = argparse.ArgumentParser(
        description='zood: web page documentation & comment generation documentation'
    )
    parser.add_argument('init',type=str,nargs='?',help='initialize docs template')
    parser.add_argument('-g','--generate',action='store_true',help='generate html doc')
    # parser.add_argument('--export',type=str,nargs='?',help='export and use in other python environment')
    args = parser.parse_args()
    
    if args.init == 'init':
        dir_name = 'md-docs'
        
        if os.path.exists(dir_name):
            print(f"{dir_name} already exist")
            return
        else:
            print(f"init [{dir_name}]")
            os.mkdir(dir_name)
            yml_config_path = os.path.join(os.path.dirname(__file__),'config','_config.yml')
            with open(yml_config_path,'r',encoding='utf-8') as f:
                config = f.read()
            # open(os.path.join(dir_name,'READMD.md'),'r')
            with open(os.path.join(dir_name,'_config.yml'),'w',encoding='utf-8') as f:
                f.write(config)

            with open('.gitignore','a',encoding='utf-8') as f:
                f.write('\nmd-docs/')


if __name__ == "__main__":
    main()