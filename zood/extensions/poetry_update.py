"""
这个文件的作用是更新 PYPI 包, 修改 pyproject.toml 的 VERSION 版本号并发布, 相当于 poetry build + poetry publish

使用方法

    python update.py                  发布版本更新
    python update.py sub              次版本更新
    python update.py main             主版本更新

"""

import shutil
import re
import os
import json
import subprocess


def print_info(msg, color="red"):
    if color == "red":
        print(f"\033[1;31m{msg}\033[0m")
    elif color == "green":
        print(f"\033[1;32m{msg}\033[0m")
    else:
        print("未知 color: (red, green)")


def update_PYPI_package(choice=None):
    """
    choice = None(default) 发布版本更新
    choice = sub           次版本更新
    choice = main          主版本更新
    """

    pwd = os.getcwd()
    pyproject_path = os.path.join(pwd, "pyproject.toml")
    if not os.path.exists(pyproject_path):
        print("pyproject.toml 不存在")
        return

    try:
        shutil.rmtree("dist")
        print("delete dist")
    except:
        pass

    # check if poetry is installed
    result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print_info("poetry 未安装", "red")
        return

    with open(pyproject_path, "r", encoding="utf-8") as f:
        file = f.read()

    old_version_re = re.search(r"version = \"(\d+)\.(\d+)\.(\d+)\"", file)
    MAIN_VERSION, SUB_VERSION, FIX_VERSION = (
        int(old_version_re.group(1)),
        int(old_version_re.group(2)),
        int(old_version_re.group(3)),
    )

    old_version = f"{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}"

    if choice is None:
        FIX_VERSION = FIX_VERSION + 1
    elif choice == "sub":
        SUB_VERSION = SUB_VERSION + 1
        FIX_VERSION = 0
    elif choice == "main":
        MAIN_VERSION = MAIN_VERSION + 1
        SUB_VERSION = 0
        FIX_VERSION = 0

    new_version = f"{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}"

    new_version_str = f'version = "{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}"'
    new_content = re.sub(r"version = \"(\d+)\.(\d+)\.(\d+)\"", new_version_str, file)
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"{old_version} -> {new_version}")

    result = subprocess.run(["poetry", "build"], capture_output=True, text=True)
    if result.returncode != 0:
        print_info("poetry build failed, pyproject.toml 版本已回退")
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(file)
        return
    result = subprocess.run(["poetry", "publish"], capture_output=True, text=True)
    if result.returncode != 0:
        print_info("poetry publish failed, pyproject.toml 版本已回退")
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(file)
        return
    print_info("更新成功", "green")


def update_vsce_package(choice=None):

    if not os.path.exists("package.json"):
        print("package.json 不存在")
        return

    with open("package.json", "r") as f:
        file = json.load(f)
    version = file["version"]
    major, minor, patch = map(int, version.split("."))
    old_version = f"{major}.{minor}.{patch}"

    if choice is None:
        patch += 1
    elif choice == "sub":
        minor += 1
        patch = 0
    else:
        major += 1
        minor = 0
        patch = 0

    new_version = f"{major}.{minor}.{patch}"
    print(f"{old_version} -> {new_version}")

    result = subprocess.run(["pnpm", "vsce", "package", "--no-dependencies"], capture_output=True, text=True)
    if result.returncode != 0:
        print_info("库更新失败, package.json 版本已回退")
        with open("package.json", "w", encoding="utf-8") as f:
            json.dump(file, f, ensure_ascii=False, indent=4)
        return
    result = subprocess.run(["pnpm", "vsce", "publish", "--no-dependencies"], capture_output=True, text=True)
    if result.returncode != 0:
        print_info("库更新失败, pyproject.toml 版本已回退")
        # 将 json 文件写回
        with open("package.json", "w", encoding="utf-8") as f:
            json.dump(file, f, ensure_ascii=False, indent=4)
        return
    print_info("更新成功", "green")
