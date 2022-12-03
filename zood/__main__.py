
import argparse
from .Parser import test

def main():
    
    parser = argparse.ArgumentParser(
        description='zood: web page documentation & comment generation documentation'
    )
    parser.add_argument('-g','--generate', help='generate document by code comment')
    parser.add_argument(
        '-d','--deploy',
        help='deploy to Github',
        action='store_true',
    )
    args = parser.parse_args()
    print(args)
    print("hello zood!")
    a = test.A()
    a.fun()


def run():
    main()


if __name__ == "__main__":
    main()