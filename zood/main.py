import argparse
import os
import shutil

from .util import *
from .gen_doc import generate_web_docs, chdir_md
from .zood import *
from .extensions import update_PYPI_package, update_vsce_package
from .server import start_http_server, set_start_time


def main():
    parser = argparse.ArgumentParser(description="zood: web page documentation & comment generation documentation")
    parser.add_argument("cmd", type=str, nargs="*", help="initialize docs template")
    parser.add_argument("-g", "--generate", action="store_true", help="generate html doc")
    parser.add_argument("-s", "--save", action="store_true", help="save global config")
    # start http server
    parser.add_argument("-o", "--open", action="store_true", help="start http server")
    parser.add_argument("-p", "--port", type=int, help="http server port", default=36001)
    parser.add_argument("-v", "--version", action="store_true", help="show version")
    args = parser.parse_args()

    config = get_zood_config()  # 获取配置信息
    md_dir_name = config["markdown_folder"]

    local_config_path = os.path.join(md_dir_name, "_config.yml")
    global_config_path = os.path.join(os.path.dirname(__file__), "config", "_config.yml")

    if args.generate:
        chdir_md(md_dir_name)
        generate_web_docs(config)
        zood_info("已生成文档 docs/", color="green")
        return

    if args.version:
        print(f"zood version: {get_version()}")
        return

    if args.open:
        set_start_time()
        chdir_md(md_dir_name)
        generate_web_docs(config)
        start_http_server(config, args.port)
        return

    if args.save:
        if os.path.exists(local_config_path):
            shutil.copy(local_config_path, global_config_path)
            zood_info("已更新全局配置文件 _config.yml", color="green")
        else:
            print("未找到", local_config_path)

        return

    if len(args.cmd) == 0 or args.cmd[0] == "help":
        show_help_info()
        return

    if args.cmd[0] == "init":
        init_zood(md_dir_name)

    elif args.cmd[0] == "new":
        if len(args.cmd) == 2:
            dir_name = "."
            file_name = args.cmd[1]
        elif len(args.cmd) == 3:
            dir_name = args.cmd[1]
            file_name = args.cmd[2]
            if dir_name == md_dir_name:
                zood_info(f"您不能创建一个和 {md_dir_name} 同名的子文件夹")
                return
        else:
            zood_info(f"创建新文件的命令为 zood new [目录] [文件名]")
            return

        if not os.path.exists(md_dir_name):
            init_zood(md_dir_name)

        create_new_file(md_dir_name, dir_name, file_name)

    elif args.cmd[0] == "clean":
        if not os.path.exists(config["html_folder"]):
            zood_info(f"没有找到 {config['html_folder']}")
            return
        shutil.rmtree(config["html_folder"])
        zood_info(f"已删除 docs")

    elif args.cmd[0] == "config":
        shutil.copy(global_config_path, local_config_path)
        zood_info(f"生成配置文件 {local_config_path}", color="green")

    elif args.cmd[0] == "update":
        current_dir = os.getcwd()
        dir_yml_path = os.path.join(current_dir, md_dir_name, "dir.yml")
        dir_yml = load_yml(dir_yml_path)
        yml_sort(dir_yml)

        removed_files = []
        for dir_name, files in dir_yml.items():
            for i in range(len(files)):
                file_name = list(files[i].keys())[0]
                file_path = os.path.join(md_dir_name, dir_name, file_name + ".md")
                if not os.path.exists(file_path):
                    zood_info(f"未找到文件 {file_path}, 已删除对应项", color="green")
                    removed_files.append(file_name)
                files[i][file_name] = i + 1

        for file_name in removed_files:
            del dir_yml[file_name]
        save_yml(dir_yml, dir_yml_path)
        print("已更新排序")

    elif args.cmd[0] == "poetry":
        if len(args.cmd) > 2:
            zood_info("peotry 接收0/1个参数")
            show_help_info()
            return

        choice = None
        if len(args.cmd) == 2:
            choice = args.cmd[1]
            if choice not in ("sub", "main"):
                zood_info("choice 选项为 (sub, main)")
                show_help_info()
                return
        update_PYPI_package(choice)

    elif args.cmd[0] == "vsce":
        if len(args.cmd) > 2:
            zood_info("vsce 接收0/1个参数")
            show_help_info()
            return

        choice = None
        if len(args.cmd) == 2:
            choice = args.cmd[1]
            if choice not in ("sub", "main"):
                zood_info("choice 选项为 (sub, main)")
                show_help_info()
                return
        update_vsce_package(choice=choice)

    elif args.cmd[0] == "log":
        # 输出错误日志信息
        with open(os.path.join(os.path.dirname(__file__), "config", "error.log"), "r", encoding="utf-8") as f:
            print(f.read())

    elif args.cmd[0] == "list":
        list_files(md_dir_name, config)

    else:
        zood_info(f"未找到指令 zood {args.cmd[0]}")
        show_help_info()


def show_help_info():
    print("zood使用方法见 https://luzhixing12345.github.io/zood/\n")
    print("{:<20}初始化仓库".format("  zood init"))
    print("{:<20}创建A目录下的B文件".format("  zood new A B"))
    print("{:<20}创建根目录下的A文件".format("  zood new A"))
    print("{:<20}启动 http 服务器".format("  zood -o"))
    print("{:<20}更新配置文件".format("  zood -s"))
    print("{:<20}列出所有文件(tree格式)".format("  zood list"))
    print("{:<20}更新dir.yml顺序".format("  zood update"))
    print("{:<20}生成docs/目录".format("  zood -g"))
    print("{:<20}删除docs/目录".format("  zood clean"))
    print("{:<20}获取配置文件".format("  zood config"))
    print("{:<20}输出错误信息".format("  zood log"))

    print("\n其他:")
    print("{:<25}更新PYPI库版本\n".format("  zood poetry <choice>"))
    indent = 12
    print(" " * indent, "choice = None(default) 发布版本更新")
    print(" " * indent, "choice = sub           次版本更新")
    print(" " * indent, "choice = main          主版本更新")
    print("")
    print("{:<25}更新Vscode扩展版本\n".format("  zood vsce <choice>"))
    indent = 12
    print(" " * indent, "choice = None(default) 发布版本更新")
    print(" " * indent, "choice = sub           次版本更新")
    print(" " * indent, "choice = main          主版本更新")
    print("")
