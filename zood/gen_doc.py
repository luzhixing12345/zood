import os
import re
import shutil
import MarkdownParser
from urllib.parse import unquote
import sys
import syntaxlight
import types
import traceback
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


def chdir_md(md_dir_name):
    current_dir = os.getcwd()

    while True:
        target_dir = os.path.join(current_dir, md_dir_name)
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            os.chdir(current_dir)
            return

        # 获取上级目录的路径
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

        # 检查是否已经到达根目录
        if parent_dir == current_dir:
            # 如果到达根目录仍未找到,返回 None
            print(f"找不到 {md_dir_name}")
            exit()

        # 更新当前目录为上级目录
        current_dir = parent_dir


def generate_web_docs(config: DIR_TREE):
    directory_tree, markdown_htmls = parse_markdown(config)
    # directory_tree 为当前项目的目录树
    # markdown_htmls 为markdown 文档对应的 html
    generate_docs(directory_tree, markdown_htmls, config)


def parse_markdown(config: DIR_TREE):
    current_dir = os.getcwd()
    md_dir_name = config["markdown_folder"]
    dir_yml_path = os.path.join(current_dir, md_dir_name, "dir.yml")
    dir_yml = load_yml(dir_yml_path)
    yml_sort(dir_yml)
    directory_tree: List[Dict[str, List[str]]] = []
    markdown_htmls: Dict[str, str] = {}
    markdown_parser = MarkdownParser.Markdown()

    # 将错误信息重定向到 error.log 中
    with open(os.path.join(os.path.dirname(__file__), "config", "error.log"), "w", encoding="utf-8") as error_log:
        sys.stderr = error_log

        github_repo_url = get_github_repo_url()
        for dir_name, files in dir_yml.items():
            file_names = []
            for file in files:
                file_name = list(file.keys())[0]
                file_path = os.path.join(md_dir_name, dir_name, file_name + ".md")
                if not os.path.exists(file_path):
                    zood_info("找不到文件" + file_path)
                    print("如手动删除md文件请同步更新 dir.yml")
                    exit(1)
                else:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = markdown_parser.preprocess_parser(f.read())
                            root = markdown_parser.block_parser(lines)
                            tree = markdown_parser.tree_parser(root)
                            markdown_tree_preprocess(tree, file_path, github_repo_url, md_dir_name)
                            header_navigater = markdown_parser.get_toc(tree)
                            markdown_html = tree.to_html(header_navigater)
                    except Exception as e:
                        zood_info(f"解析文件 {file_path} 失败", "red")
                        # 输出 traceback
                        sys.stderr = sys.__stderr__
                        traceback.print_exc()
                        zood_info(f"欢迎反馈错误信息到 https://github.com/luzhixing12345/zood/issues/new, 感谢您的支持")
                        markdown_html = ""

                    markdown_htmls[file_path] = markdown_html
                    file_names.append(file_name)
            directory_tree.append({dir_name: file_names})

    # 恢复错误信息重定向
    sys.stderr = sys.__stderr__

    global TOTAL_ERROR_NUMBER
    if TOTAL_ERROR_NUMBER != 0:
        zood_info(f"代码段解析出现 {TOTAL_ERROR_NUMBER} 处错误, 已跳过高亮解析, 使用 zood log 查看错误信息")

    return directory_tree, markdown_htmls


def markdown_tree_preprocess(tree: MarkdownParser.Block, file_path: str, github_repo_url: str, md_dir_name: str):
    """
    使用 syntaxlight 更新其中代码段的高亮
    https://github.com/luzhixing12345/syntaxlight
    """

    def code_to_html(self: MarkdownParser.Block):
        return f'<pre class="language-{self.input["language"]}"><code>{self.input["code"]}</code></pre>'

    def pic_to_html(self: MarkdownParser.Block):
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
        return f'<a data-lightbox="example-1" href="{url}"><img loading="lazy" src="{url}" alt="{word}"></a>'

    def ref_to_html(self: MarkdownParser.Block):
        url: str = self.input["url"]
        # 判断一下是否是本地的跳转链接
        local_url = os.path.normpath(os.path.join(os.path.dirname(file_path), unquote(url)))
        if not url.startswith("http") and os.path.exists(local_url) and local_url.endswith(".md"):
            local_url = local_url[len(md_dir_name) : -3].lstrip("\\").lstrip("/")
            # 如果 url 没有父目录, 加上 md_dir_name
            if not os.path.dirname(local_url):
                local_url = os.path.join(md_dir_name, local_url)
            url = f"../../{local_url}"
            self.target = "_self"
        content = ""
        for block in self.sub_blocks:
            content += block.to_html()
        return f'<a href="{url}" target="{self.target}">{content}</a>'

    def quote_to_html(self: MarkdownParser.Block):
        content = ""
        for block in self.sub_blocks:
            content += block.to_html()

        # check if content start with bullet list
        built_in_tags = {
            # matched name: ("css class", "tag color", "background color")
            "[!NOTE]": ("note", "#0969da", "#e8f3ff"),
            "[!TIP]": ("tip", "#1a7f37", "#e5f6ea"),
            "[!IMPORTANT]": ("important", "#8250df", "#eee4ff"),
            "[!WARNING]": ("warning", "#9a6700", "#fff4dd"),
            "[!CAUTION]": ("caution", "#d1242f", "#f7e5e6"),
            "[!QUESTION]": ("question", "#f08833", "#ffefe3"),
        }
        # > [!NOTE]
        # > Highlights information that users should take into account, even when skimming.

        # > [!TIP]
        # > Optional information to help a user be more successful.

        # > [!IMPORTANT]
        # > Crucial information necessary for users to succeed.

        # > [!WARNING]
        # > Critical content demanding immediate user attention due to potential risks.

        # > [!CAUTION]
        # > Negative potential consequences of an action.
        blockquote_border_color = None
        blockquote_border_bg_color = None
        for tag, (icon, color, bg_color) in built_in_tags.items():
            if content.startswith(f"<p>{tag}"):
                content = content.replace(
                    tag,
                    f'<div style="color: {color};"><img class="icon-{icon}" loading="lazy" src="../../../img/{icon}.svg" alt="{tag}"> {icon.upper()} </div>',
                    1,
                )
                # change blockquote border-left color
                blockquote_border_color = color
                blockquote_border_bg_color = bg_color
                break

        # print(blockquote_border_color)
        if blockquote_border_color is not None:
            return f'<blockquote style="border-left-color: {blockquote_border_color}; background-color: {blockquote_border_bg_color};">{content}</blockquote>'
        else:
            return f"<blockquote>{content}</blockquote>"

    global LANGUAGE_USED
    global TOTAL_ERROR_NUMBER
    global CODE_BLOCK_NUMBER
    for block in tree.sub_blocks:
        if block.block_name == "CodeBlock":
            language = block.input["language"]
            append_text = block.input["append_text"]
            if syntaxlight.is_language_support(language) or language == "UNKNOWN":
                if language == "UNKNOWN":
                    language = "txt"
                else:
                    language = syntaxlight.clean_language(language)
                block.input["language"] = language
                try:
                    parse_result = syntaxlight.parse(block.input["code"], language, file_path)
                    if append_text == "?" or append_text == "??":
                        zood_info(f"请根据提示信息进行高亮定位 file: {file_path}", "green")
                        show_highlight_position_info(parse_result.parser, show_token_id=append_text == "??")
                        exit()
                    else:
                        highlight_lines, highlight_tokens = parse_highlight_info(append_text)
                    exception = parse_result.error
                except Exception as e:
                    exception = e
                    print(f"解析错误: {file_path}: {exception}")
                    print(f'```{language}\n{block.input["code"]}\n```')

                block.input["code"] = parse_result.parser.to_html(
                    highlight_lines=highlight_lines, highlight_tokens=highlight_tokens
                )
                block.to_html = types.MethodType(code_to_html, block)
                LANGUAGE_USED.add(language)
                if exception is not None:
                    TOTAL_ERROR_NUMBER += 1
                    sys.stderr.write(str(exception))
                CODE_BLOCK_NUMBER += 1
        elif block.block_name == "PictureBlock":
            block.to_html = types.MethodType(pic_to_html, block)
        elif block.block_name == "ReferenceBlock":
            block.to_html = types.MethodType(ref_to_html, block)
        elif block.block_name == "QuoteBlock":
            block.to_html = types.MethodType(quote_to_html, block)

        markdown_tree_preprocess(block, file_path, github_repo_url, md_dir_name)


def generate_docs(directory_tree, markdown_htmls: Dict[str, str], config: DIR_TREE):
    html_dir_name = config["html_folder"]
    md_dir_name = config["markdown_folder"]
    index_README_path = os.path.join(md_dir_name, ".", "README.md")
    if not os.path.exists(index_README_path):
        zood_info(f"您需要保留 {md_dir_name}/README.md 作为首页")
        exit()

    if os.path.exists(html_dir_name):
        remove_directory(html_dir_name)
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
    language_used = list(LANGUAGE_USED)
    language_used.sort()
    syntaxlight.export_css(language_used, os.path.join(html_dir_name, "css"))

    hightlight_css = ""
    for l in language_used:
        hightlight_css += f"<link rel='stylesheet' href=../../../css/{l}.css />"

    html_template = parse_config(config)
    index_html_path = os.path.join(html_dir_name, "index.html")
    html_template = html_template.replace("hightlight-css", hightlight_css)

    # 修正 index html
    with open(index_html_path, "w", encoding="utf-8") as f:
        index_html_template = html_template.replace("../../.", "")
        next_url = next_url.replace("../..", "./articles")
        index_dir_tree_html = dir_tree_html.replace("../..", "./articles")
        index_html_template = index_html_template.replace("../..", "./articles")

        index_html_template = index_html_template.replace("directory-tree-scope", index_dir_tree_html)
        index_html_template = index_html_template.replace("github-icon", github_icon)
        index_html_template = url_replace(index_html_template, front_url, next_url, "ab")

        index_markdown_html = markdown_htmls[index_README_path]
        # 把 index html 中的 ../../../img/{note}.svg 替换为 img/{note}.svg
        index_markdown_html = re.sub(r"../../../img/([a-zA-Z0-9_-]+)\.svg", r"img/\1.svg", index_markdown_html)
        f.write(index_html_template.replace("html-scope", index_markdown_html))

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
