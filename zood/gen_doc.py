import os
import json5
import shutil
import MarkdownParser
from urllib.parse import unquote
import sys
import syntaxlight
import types
from .util import *
from .zood import (
    parse_config,
    caculate_front_next_url,
    get_dir_tree,
    url_replace,
)

LANGUAGE_USED = set()
TOTAL_ERROR_NUMBER = 0
CODE_BLOCK_NUMBER = 1


def generate_web_docs(md_dir_name):
    directory_tree, markdown_htmls = parse_markdown(md_dir_name)
    # directory_tree 为当前项目的目录树
    # markdown_htmls 为markdown 文档对应的 html
    generate_docs(directory_tree, markdown_htmls, md_dir_name)


def parse_markdown(md_dir_name):
    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir, md_dir_name, "dir.yml")
    dir_yml = load_yml(dir_yml_path)
    yml_sort(dir_yml)
    directory_tree: List[Dict[str, List[str]]] = []
    markdown_htmls: Dict[str, str] = {}
    markdown_parser = MarkdownParser.Markdown()

    # 将错误信息重定向到 error.log 中
    error_log_file = open(os.path.join(os.path.dirname(__file__), "config", "error.log"), "w", encoding="utf-8")
    sys.stderr = error_log_file

    github_repo_url = get_github_repo_url()
    for dir_name, files in dir_yml.items():
        file_names = []
        for file in files:
            file_name = list(file.keys())[0]
            file_path = os.path.join(md_dir_name, dir_name, file_name + ".md")
            if not os.path.exists(file_path):
                print_info("[zood解析失败]: 找不到文件" + file_path)
                print("如手动删除md文件可使用 zood update 更新 dir.yml")
                exit(1)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = markdown_parser.preprocess_parser(f.read())
                    root = markdown_parser.block_parser(lines)
                    tree = markdown_parser.tree_parser(root)
                    markdown_tree_preprocess(tree, file_path, github_repo_url, md_dir_name)
                    header_navigater = markdown_parser.get_toc(tree)
                    markdown_html = tree.to_html(header_navigater)

                markdown_htmls[file_path] = markdown_html
                file_names.append(file_name)
        directory_tree.append({dir_name: file_names})

    error_log_file.close()

    global TOTAL_ERROR_NUMBER
    if TOTAL_ERROR_NUMBER != 0:
        print_info(f"[zood]: 代码段解析出现 {TOTAL_ERROR_NUMBER} 处错误, 已跳过高亮解析, 使用 zood log 查看错误信息")

    return directory_tree, markdown_htmls


def markdown_tree_preprocess(tree: MarkdownParser.Block, file_path: str, github_repo_url: str, md_dir_name: str):
    """
    使用 syntaxlight 更新其中代码段的高亮
    https://github.com/luzhixing12345/syntaxlight
    """

    def code_to_html(self):
        return f'<pre class="language-{self.input["language"]}"><code>{self.input["code"]}</code></pre>'

    def pic_to_html(self):
        word: str = self.input["word"]
        url: str = self.input["url"]
        # 判断一下是否是本地图片
        local_url = os.path.normpath(os.path.join(os.path.dirname(file_path), unquote(url)))
        if not url.startswith("http") and os.path.exists(local_url):
            # https://raw.githubusercontent.com/luzhixing12345/paperplotlib/master/
            # https://github.com/luzhixing12345/paperplotlib/

            # 默认 master 分支
            server_url = github_repo_url.replace("github.com", "raw.githubusercontent.com") + "/master/"
            url = server_url + local_url
        return f'<a data-lightbox="example-1" href="{url}"><img src="{url}" alt="{word}"></a>'

    def ref_to_html(self):
        url = self.input["url"]
        # 判断一下是否是本地的跳转链接
        # print(unquote(url))
        local_url = os.path.normpath(os.path.join(os.path.dirname(file_path), unquote(url)))
        if not url.startswith("http") and os.path.exists(local_url) and local_url.endswith(".md"):
            local_url = local_url.rstrip(".md").lstrip(md_dir_name).lstrip("\\").lstrip("/")
            url = f"../../{local_url}"
            self.target = "_self"
        content = ""
        for block in self.sub_blocks:
            content += block.to_html()
        return f'<a href="{url}" target="{self.target}">{content}</a>'

    global LANGUAGE_USED
    global TOTAL_ERROR_NUMBER
    global CODE_BLOCK_NUMBER
    for block in tree.sub_blocks:
        if block.block_name == "CodeBlock":
            language = block.input["language"]
            if syntaxlight.is_language_support(language) or language == "UNKNOWN":
                if language == "UNKNOWN":
                    language = "txt"
                else:
                    language = syntaxlight.clean_language(language)
                block.input["language"] = language

                code, success = syntaxlight.parse(block.input["code"], language, file_path)
                block.input["code"] = code
                block.to_html = types.MethodType(code_to_html, block)
                LANGUAGE_USED.add(language)
                if not success:
                    TOTAL_ERROR_NUMBER += 1
                CODE_BLOCK_NUMBER += 1
        elif block.block_name == "PictureBlock":
            block.to_html = types.MethodType(pic_to_html, block)
        elif block.block_name == "ReferenceBlock":
            block.to_html = types.MethodType(ref_to_html, block)
        else:
            markdown_tree_preprocess(block, file_path, github_repo_url, md_dir_name)


def generate_docs(directory_tree, markdown_htmls: Dict[str, str], md_dir_name):
    config = get_zood_config()
    html_dir_name = config["html_folder"]

    index_README_path = os.path.join(md_dir_name, ".", "README.md")
    if not os.path.exists(index_README_path):
        print_info(f"您需要保留 {md_dir_name}/README.md 作为首页")
        exit()

    if os.path.exists(html_dir_name):
        shutil.rmtree(html_dir_name)
    os.makedirs(os.path.join(html_dir_name, "articles"))
    os.makedirs(os.path.join(html_dir_name, "js"))
    os.makedirs(os.path.join(html_dir_name, "css"))
    os.makedirs(os.path.join(html_dir_name, "img"))

    # 复制图片
    imgs_path = os.path.join(os.path.dirname(__file__), "config", "img")
    for root, _, files in os.walk(imgs_path):
        for img in files:
            shutil.copy(os.path.join(root, img), os.path.join(html_dir_name, "img"))

    flat_paths = []  # 扁平化之后的所有文件的路径
    for item in directory_tree:
        dir_name = list(item.keys())[0]
        files = item[dir_name]
        if dir_name == ".":
            dir_name = md_dir_name
        for file in files:
            flat_paths.append(os.path.join(dir_name, file))

    # 目录树
    dir_tree_html = get_dir_tree(directory_tree, md_dir_name)
    front_url, next_url = caculate_front_next_url(flat_paths, index_README_path, md_dir_name)
    github_icon = get_github_icon(config["options"]["enable_github"])

    global LANGUAGE_USED
    LANGUAGE_USED = list(LANGUAGE_USED)
    LANGUAGE_USED.sort()
    syntaxlight.export_css(LANGUAGE_USED, os.path.join(html_dir_name, "css"))

    hightlight_css = ""
    for l in LANGUAGE_USED:
        hightlight_css += f"<link rel='stylesheet' href=../../../css/{l}.css />"

    html_template = parse_config(config)
    index_html_path = os.path.join(html_dir_name, "index.html")
    html_template = html_template.replace("hightlight-css", hightlight_css)
    with open(index_html_path, "w", encoding="utf-8") as f:
        # index 的地址做一些修改
        index_html_template = html_template.replace("../../.", "")
        next_url = next_url.replace("../..", "./articles")
        index_dir_tree_html = dir_tree_html.replace("../..", "./articles")
        index_html_template = index_html_template.replace("../..", "./articles")

        index_html_template = index_html_template.replace("directory-tree-scope", index_dir_tree_html)
        index_html_template = index_html_template.replace("github-icon", github_icon)
        index_html_template = url_replace(index_html_template, front_url, next_url, "ab")
        f.write(index_html_template.replace("html-scope", markdown_htmls[index_README_path]))

    html_template = html_template.replace("directory-tree-scope", dir_tree_html)
    html_template = html_template.replace("github-icon", github_icon)
    for file_path, markdown_html in markdown_htmls.items():
        dir_name = file_path.split(os.sep)[1]
        file_name = file_path.split(os.sep)[2].replace(".md", "")
        if dir_name == ".":
            dir_name = md_dir_name
        doc_path = os.path.join(html_dir_name, "articles", dir_name, file_name)
        os.makedirs(doc_path)
        html_path = os.path.join(doc_path, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            front_url, next_url = caculate_front_next_url(flat_paths, file_path, md_dir_name)
            # print(html_path,front_url,next_url)
            final_html = url_replace(html_template, front_url, next_url, "ab")
            f.write(final_html.replace("html-scope", markdown_html))

    print_info(f"[zood]: 已生成 {html_dir_name}/", color="green")

    # 对于 vscode 的 live server 的优化
    vscode_settings = os.path.join(".vscode", "settings.json")

    if os.path.exists(vscode_settings):
        with open(vscode_settings, "r", encoding="utf-8") as f:
            settings = json5.load(f)
            if "liveServer.settings.port" in settings:
                print(
                    f'\nVscode live server: http://127.0.0.1:{settings["liveServer.settings.port"]}/docs/index.html\n'
                )
    else:
        print(f"\nVscode live server: http://127.0.0.1:5500/docs/index.html\n")
