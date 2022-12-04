

import argparse

def main():
    parser = argparse.ArgumentParser(
        description='zood: web page documentation & comment generation documentation'
    )
    parser.add_argument('-g','--generate', help='generate document by code comment')
    parser.add_argument(
        '-c','--code',
        help='generate by code',
        action='store_true',
    )
    parser.add_argument('--init',type=str, nargs='?',help='initialize docs template')
    parser.add_argument('--save',type=str, nargs='?',help='save file to use again')
    parser.add_argument('--export',type=str,nargs='?',help='export and use in other python environment')
    args = parser.parse_args()


    
if __name__ == "__main__":
    main()