import syntaxlight.parsers
import yaml
import os
import subprocess
from typing import Dict, List, NewType
import syntaxlight
from importlib.metadata import version
import datetime

DIR_TREE = NewType("DIR_TREE", Dict[str, List[Dict[str, str]]])
zood_error_info = []


def get_github_repo_url() -> str:
    """
    暂时只考虑从 origin 获取的 git 地址
    """
    url = ""
    try:
        output = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).strip()
        url = output.decode("utf-8")
        if url.startswith("git@"):
            parts = url.split(":")
            if len(parts) == 2:
                url = f"https://github.com/{parts[1]}"
    except subprocess.CalledProcessError:
        return url
    return url


def get_version():
    return version("zood")


# 获取 github 地址
GITHUB_REPO_URL = get_github_repo_url()


def load_yml(file_path: str):
    if not os.path.exists(file_path):
        zood_info("找不到文件" + file_path)
        exit(0)

    with open(file_path, "r", encoding="utf-8") as f:
        file_data = f.read()

    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def save_yml(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def yml_sort(yml: DIR_TREE):
    for _, files in yml.items():
        files.sort(key=lambda item: list(item.values())[0])


def zood_info(msg, color="red", hide_zood=False, end="\n"):
    zood_mark = "[zood]: " if not hide_zood else ""
    if color == "red":
        print(f"\033[1;31m{zood_mark}{msg}\033[0m", end=end)
        zood_error_info.append(msg)
    elif color == "green":
        print(f"\033[1;32m{zood_mark}{msg}\033[0m", end=end)
    elif color == "grey":
        print(f"\033[1;30m{zood_mark}{msg}\033[0m", end=end)
    else:
        print(msg, end=end)


def info(msg, color=None, end=""):
    if color == "red":
        print(f"\033[1;31m{msg}\033[0m", end=end)
    elif color == "green":
        print(f"\033[1;32m{msg}\033[0m", end=end)
    elif color == "grey":
        print(f"\033[1;30m{msg}\033[0m", end=end)
    elif color == "blue":
        print(f"\033[1;34m{msg}\033[0m", end=end)
    elif color == "cyan":
        print(f"\033[1;36m{msg}\033[0m", end=end)
    elif color == "strong":
        print(f"\033[1m{msg}\033[0m", end=end)
    else:
        print(msg, end=end)


def show_error_info():
    if zood_error_info:
        info("zood 执行过程中出现错误, 请检查以下信息\n", color="red")
        for i in zood_error_info:
            info(i, color="red", end="\n")

        zood_error_info.clear()


def get_zood_config():
    """
    获取基础配置信息, 优先查找当前目录下 md-docs/ 是否存在 _config.yml
    如果本地不存在则使用全局 _config.yml 作为配置信息
    """
    global_config_path = os.path.join(os.path.dirname(__file__), "config", "_config.yml")

    global_config = load_yml(global_config_path)
    md_dir_name = global_config["markdown_folder"]

    local_config_path = os.path.join(md_dir_name, "_config.yml")
    if os.path.exists(local_config_path):
        # 如果本地 config 比全局 config 的 key 少, 则说明更新了 zood 版本
        local_config = load_yml(local_config_path)
        check_zood_config_key(local_config, global_config)
        return local_config
    else:
        return global_config


def check_zood_config_key(local_config: DIR_TREE, global_config: DIR_TREE, parent_keys=[]):
    """
    递归的判断 zood 配置文件中的 key 是否存在于全局配置文件中
    """
    if set(local_config.keys()) < set(global_config.keys()):
        key_names = set(global_config.keys()) - set(local_config.keys())
        # 同步缺少的全局配置
        for key_name in key_names:
            option_name = ":".join(parent_keys + [key_name])
            zood_info(f"当前 zood 版本更新了配置项: {option_name}: {global_config[key_name]}", color="grey")
            local_config[key_name] = global_config[key_name]
            zood_info(f"已使用默认值, 启用请手动同步\n", color="grey")

    for key in local_config.keys():
        if isinstance(local_config[key], dict):
            check_zood_config_key(local_config[key], global_config[key], parent_keys + [key])


def caculate_front_next_url(flat_paths: list, path: str, md_dir_name):
    dir_name = path.split(os.sep)[1]
    file_name = path.split(os.sep)[2].replace(".md", "")
    if dir_name == ".":
        dir_name = md_dir_name
    path = os.path.join(dir_name, file_name)
    pos = flat_paths.index(path)

    front_url = '"."'
    next_url = '"."'

    if pos != 0:
        front_url = htmlRelativeUrl(flat_paths[pos - 1])
    if pos != len(flat_paths) - 1:
        next_url = htmlRelativeUrl(flat_paths[pos + 1])

    return front_url, next_url


def htmlRelativeUrl(url: str):
    new_url = url.replace(os.sep, "/")
    new_url = f'"../../{new_url}"'
    return new_url


def get_dir_tree(directory_tree, md_dir_name):
    tree_html = ""
    for item in directory_tree:
        dir_name = list(item.keys())[0]
        files = item[dir_name]
        if dir_name == ".":
            dir_name = md_dir_name
            for file in files:
                dir_url_link = f"../../{dir_name}/{file}"
                # print(dir_url_link)
                tree_html += treeItem(file, dir_url_link)
        else:
            sub_tree_html = ""
            for file in files:
                dir_url_link = f"../../{dir_name}/{file}"
                # print(dir_url_link)
                sub_tree_html += treeItem(file, dir_url_link)

            first_dir_url_link = f"../../{dir_name}/{files[0]}"
            tree_html += treeItem(dir_name, first_dir_url_link, sub_tree=sub_tree_html)

    # print(tree_html)
    return f'<div class="dir-tree">{tree_html}</div>'


def treeItem(name, dir_url_link, sub_tree=False):
    if sub_tree:
        link = f'<a href="{dir_url_link}" >{name}</a>'
        return f"<ul><li>{link}{sub_tree}</li></ul>"
    else:
        link = f'<a href="{dir_url_link}" >{name}</a>'
        return f"<ul><li>{link}</li></ul>"


def url_replace(html_template: str, front_url, next_url, control):
    html_template = html_template.replace("<%front_url%>", front_url).replace("<%next_url%>", next_url)
    html_template = html_template.replace("<%control%>", f'"{control}"')
    return html_template


def get_github_icon(enable_github):
    if enable_github is False:
        return ""

    url = GITHUB_REPO_URL
    if url == "":
        return ""
    else:
        return join_github_icon(url)


def join_github_icon(url: str):
    # https://tholman.com/github-corners/
    github_icon = (
        '<a href="'
        + url
        + '" target="_blank" class="github-corner" aria-label="View source on GitHub"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#151513; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a><style>.github-corner:hover .octo-arm{animation:octocat-wave 560ms ease-in-out}@keyframes octocat-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-25deg)}40%,80%{transform:rotate(10deg)}}@media (max-width:500px){.github-corner:hover .octo-arm{animation:none}.github-corner .octo-arm{animation:octocat-wave 560ms ease-in-out}}</style>'
    )
    return github_icon


def remove_directory(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)


def parse_highlight_info(append_text: str):

    if append_text == "" or append_text is None:
        return [], []

    highlight_tokens = []
    highlight_lines = []

    lines = append_text.split(",")
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("#"):
            # 高亮某一个 token
            line = line[1:]
            if line.find("-") != -1:
                start, end = line.split("-")
                for i in range(int(start), int(end) + 1):
                    highlight_tokens.append(i)
            else:
                highlight_tokens.append(int(line))
        else:
            if line.find("-") != -1:
                start, end = line.split("-")
                for i in range(int(start), int(end) + 1):
                    highlight_lines.append(i)
            else:
                highlight_lines.append(int(line))

    return highlight_lines, highlight_tokens


def show_highlight_position_info(parser: syntaxlight.Parser, show_token_id=False):

    current_line = 0
    max_line = parser.token_list[-1].line
    for i, token in enumerate(parser.token_list):
        if current_line != token.line:
            current_line = token.line
            # 以 max_line 对齐
            info(f"{current_line:>{len(str(max_line))}} | ", color="grey")

        info(token.value)
        if show_token_id and token.value not in ["\n", "\r"]:
            info(f"[{i}]", color="grey")

    print("")


# 清屏
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def list_files(md_dir_name: str, config: dict):
    """
    列出 md-docs 目录下的所有文件，类似 tree 命令的格式
    """
    current_dir = os.getcwd()

    # 检查 md 目录是否存在
    md_path = os.path.join(current_dir, md_dir_name)
    if not os.path.exists(md_path):
        zood_info(f"未找到 {md_dir_name} 目录")
        return

    # 显示目录标题
    print(f"\033[1;34m{md_dir_name}/\033[0m")

    # 显示 markdown 文件结构
    _show_markdown_structure(md_path, "", config)


def _show_directory_tree(base_path: str, md_dir_name: str, config: dict, prefix: str = "", is_last: bool = True):
    """
    递归显示目录树
    """
    items = []

    # 收集要显示的项目
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)

        # 跳过隐藏文件和不需要显示的目录
        if item.startswith(".") and item not in [".gitignore", ".github"]:
            continue

        # 跳过一些常见的不需要显示的目录
        if item in ["__pycache__", ".pytest_cache", "node_modules", ".vscode"]:
            continue

        items.append((item, item_path))

    # 按照类型和名称排序：目录在前，文件在后，名称字母序
    items.sort(key=lambda x: (not os.path.isdir(x[1]), x[0].lower()))

    for i, (item, item_path) in enumerate(items):
        is_last_item = i == len(items) - 1

        # 确定树形结构的符号
        if is_last_item:
            current_prefix = "└── "
            next_prefix = prefix + "    "
        else:
            current_prefix = "├── "
            next_prefix = prefix + "│   "

        # 获取文件/目录信息
        if os.path.isdir(item_path):
            # 获取目录中的文件数量
            try:
                dir_count = len([f for f in os.listdir(item_path) if not f.startswith(".") and f != "__pycache__"])
                count_info = f" ({dir_count} items)" if dir_count > 0 else " (empty)"
            except PermissionError:
                count_info = " (permission denied)"

            print(f"{prefix}{current_prefix}\033[1;34m{item}/\033[0m\033[90m{count_info}\033[0m")

            # 特殊处理 md_dir_name 目录，显示其中的 markdown 文件结构
            if item == md_dir_name:
                _show_markdown_structure(item_path, next_prefix, config)
            # 对于其他重要目录，递归显示（但限制深度）
            elif item in ["docs", "src", "lib", "tests", "examples"] and prefix.count("│") < 2:
                _show_directory_tree(item_path, md_dir_name, config, next_prefix, is_last_item)

        else:
            # 显示文件
            try:
                if item.endswith(".md"):
                    # 对于markdown文件，显示修改时间
                    time_info = _format_relative_time(item_path)
                else:
                    # 对于其他文件，显示大小
                    file_size = os.path.getsize(item_path)
                    time_info = _format_file_size(file_size)
            except (OSError, PermissionError):
                time_info = "?"

            # 根据文件类型设置颜色
            file_color = _get_file_color(item)
            print(f"{prefix}{current_prefix}{file_color}{item}\033[0m \033[90m({time_info})\033[0m")


def _show_markdown_structure(md_path: str, prefix: str, config: dict):
    """
    显示 markdown 目录的结构，优先基于 dir.yml 文件，否则直接显示目录结构
    """
    dir_yml_path = os.path.join(md_path, "dir.yml")

    if os.path.exists(dir_yml_path):
        try:
            dir_yml = load_yml(dir_yml_path)

            # 按照 dir.yml 的结构显示，保持原有顺序
            dir_items = list(dir_yml.items())
            for idx, (dir_name, files) in enumerate(dir_items):
                is_last_dir = idx == len(dir_items) - 1
                dir_prefix = "└── " if is_last_dir else "├── "

                if dir_name == ".":
                    # 根目录下的文件，按照 dir.yml 中的顺序排序
                    if files:
                        # 按照文件在 dir.yml 中定义的顺序值排序
                        sorted_files = sorted(files, key=lambda x: list(x.values())[0] if isinstance(x, dict) else 0)

                        for i, file_info in enumerate(sorted_files):
                            if isinstance(file_info, dict):
                                file_name = list(file_info.keys())[0]
                                file_path = os.path.join(md_path, f"{file_name}.md")
                                if os.path.exists(file_path):
                                    file_time = _format_relative_time(file_path)
                                    is_last_file = (i == len(sorted_files) - 1) and is_last_dir
                                    file_prefix = "└── " if is_last_file else "├── "
                                    print(
                                        f"{prefix}{file_prefix}\033[92m{file_name}.md\033[0m \033[90m({file_time})\033[0m"
                                    )
                else:
                    # 子目录
                    sub_dir_path = os.path.join(md_path, dir_name)
                    if os.path.exists(sub_dir_path):
                        file_count = len(files) if files else 0
                        print(
                            f"{prefix}{dir_prefix}\033[1;34m{dir_name}/\033[0m\033[90m ({file_count} md files)\033[0m"
                        )

                        # 显示子目录中的文件，按照 dir.yml 中的顺序
                        next_prefix = prefix + ("    " if is_last_dir else "│   ")
                        if files:
                            # 按照文件在 dir.yml 中定义的顺序值排序
                            sorted_files = sorted(
                                files, key=lambda x: list(x.values())[0] if isinstance(x, dict) else 0
                            )

                            for i, file_info in enumerate(sorted_files):
                                if isinstance(file_info, dict):
                                    file_name = list(file_info.keys())[0]
                                    file_path = os.path.join(sub_dir_path, f"{file_name}.md")
                                    if os.path.exists(file_path):
                                        file_time = _format_relative_time(file_path)
                                        is_last_file = i == len(sorted_files) - 1
                                        file_prefix = "└── " if is_last_file else "├── "
                                        print(
                                            f"{next_prefix}{file_prefix}\033[92m{file_name}.md\033[0m \033[90m({file_time})\033[0m"
                                        )

        except Exception as e:
            print(f"{prefix}├── \033[91mError reading dir.yml: {str(e)}\033[0m")
            # 出错时回退到直接显示目录结构
            _show_directory_files(md_path, prefix)
    else:
        # 如果没有 dir.yml，直接显示目录结构
        _show_directory_files(md_path, prefix)


def _show_directory_files(base_path: str, prefix: str = ""):
    """
    直接显示目录中的文件结构（不依赖dir.yml）
    """
    items = []

    # 收集所有项目
    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            # 跳过隐藏文件和配置文件
            if item.startswith(".") or item in ["_config.yml", "dir.yml"]:
                continue

            items.append((item, item_path))
    except PermissionError:
        print(f"{prefix}├── \033[91m(permission denied)\033[0m")
        return

    # 排序：目录在前，文件在后
    items.sort(key=lambda x: (not os.path.isdir(x[1]), x[0].lower()))

    for i, (item, item_path) in enumerate(items):
        is_last_item = i == len(items) - 1
        current_prefix = "└── " if is_last_item else "├── "
        next_prefix = prefix + ("    " if is_last_item else "│   ")

        if os.path.isdir(item_path):
            # 统计目录中的 .md 文件数量
            try:
                md_files = [f for f in os.listdir(item_path) if f.endswith(".md") and not f.startswith(".")]
                file_count = len(md_files)
                count_info = f" ({file_count} md files)" if file_count > 0 else " (empty)"
            except PermissionError:
                count_info = " (permission denied)"

            print(f"{prefix}{current_prefix}\033[1;34m{item}/\033[0m\033[90m{count_info}\033[0m")

            # 递归显示子目录（限制深度为1层）
            if prefix.count("│") < 1:
                _show_directory_files(item_path, next_prefix)
        else:
            # 显示文件
            try:
                if item.endswith(".md"):
                    # 对于markdown文件，显示修改时间
                    time_info = _format_relative_time(item_path)
                else:
                    # 对于其他文件，显示大小
                    file_size = os.path.getsize(item_path)
                    time_info = _format_file_size(file_size)
            except (OSError, PermissionError):
                time_info = "?"

            file_color = _get_file_color(item)
            print(f"{prefix}{current_prefix}{file_color}{item}\033[0m \033[90m({time_info})\033[0m")


def _format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes // (1024 * 1024)}MB"
    else:
        return f"{size_bytes // (1024 * 1024 * 1024)}GB"


def _format_relative_time(file_path: str) -> str:
    """
    格式化文件的相对修改时间显示
    """
    try:
        # 获取文件的最后修改时间
        mtime = os.path.getmtime(file_path)
        file_time = datetime.datetime.fromtimestamp(mtime)
        current_time = datetime.datetime.now()

        # 计算时间差
        time_diff = current_time - file_time
        total_seconds = int(time_diff.total_seconds())

        if total_seconds < 60:
            return "刚刚"
        elif total_seconds < 3600:  # 1小时内
            minutes = total_seconds // 60
            return f"{minutes}分钟前"
        elif total_seconds < 86400:  # 24小时内
            hours = total_seconds // 3600
            return f"{hours}小时前"
        elif total_seconds < 604800:  # 7天内
            days = total_seconds // 86400
            return f"{days}天前"
        elif total_seconds < 2592000:  # 30天内
            weeks = total_seconds // 604800
            return f"{weeks}周前"
        elif total_seconds < 31536000:  # 12个月内
            months = total_seconds // 2592000
            return f"{months}个月前"
        else:
            # 超过12个月，显示具体日期
            return file_time.strftime("%Y-%m-%d")

    except (OSError, PermissionError):
        return "未知"


def _get_file_color(filename: str) -> str:
    """
    根据文件扩展名返回对应的颜色代码
    """
    ext = os.path.splitext(filename)[1].lower()

    color_map = {
        # 文档文件
        ".md": "\033[92m",  # 绿色
        ".txt": "\033[97m",  # 白色
        ".pdf": "\033[91m",  # 红色
        ".doc": "\033[94m",  # 蓝色
        ".docx": "\033[94m",  # 蓝色
        # 代码文件
        ".py": "\033[93m",  # 黄色
        ".js": "\033[93m",  # 黄色
        ".ts": "\033[94m",  # 蓝色
        ".html": "\033[96m",  # 青色
        ".css": "\033[96m",  # 青色
        ".json": "\033[93m",  # 黄色
        ".yml": "\033[95m",  # 品红色
        ".yaml": "\033[95m",  # 品红色
        ".toml": "\033[95m",  # 品红色
        # 图片文件
        ".png": "\033[95m",  # 品红色
        ".jpg": "\033[95m",  # 品红色
        ".jpeg": "\033[95m",  # 品红色
        ".gif": "\033[95m",  # 品红色
        ".svg": "\033[95m",  # 品红色
        # 可执行文件
        ".exe": "\033[91m",  # 红色
        ".sh": "\033[92m",  # 绿色
        ".bat": "\033[92m",  # 绿色
    }

    return color_map.get(ext, "\033[97m")  # 默认白色
