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

# 添加全局变量来跟踪引用关系
REFERENCE_GRAPH = {}  # 存储文档间的引用关系 {source_file: [target_files]}
CURRENT_FILE_PATH = ""  # 当前正在处理的文件路径


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
            sys.exit(1)

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
                    sys.exit(1)
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
                        sys.exit(1)
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

built_in_icon_svgs = {
    "note": '<svg xmlns="http://www.w3.org/2000/svg" width="1.8em" height="1.8em" viewBox="0 0 24 24"><g fill="none" stroke="#0969da"><path stroke-linecap="round" stroke-linejoin="round" d="M11 10.5h.5a.5.5 0 0 1 .5.5v4a.5.5 0 0 0 .5.5h.5m-1-7h.01"/><path d="M13.39 19.879A8 8 0 1 0 10.61 4.12a8 8 0 0 0 2.78 15.758Z"/></g></svg>',
    "tip": '<svg xmlns="http://www.w3.org/2000/svg" width="1.6em" height="1.6em" viewBox="0 0 24 24"><path fill="#1a7f37" d="M12 2.5c-3.81 0-6.5 2.743-6.5 6.119c0 1.536.632 2.572 1.425 3.56c.172.215.347.422.527.635l.096.112c.21.25.427.508.63.774c.404.531.783 1.128.995 1.834a.75.75 0 0 1-1.436.432c-.138-.46-.397-.89-.753-1.357a18 18 0 0 0-.582-.714l-.092-.11c-.18-.212-.37-.436-.555-.667C4.87 12.016 4 10.651 4 8.618C4 4.363 7.415 1 12 1s8 3.362 8 7.619c0 2.032-.87 3.397-1.755 4.5c-.185.23-.375.454-.555.667l-.092.109c-.21.248-.405.481-.582.714c-.356.467-.615.898-.753 1.357a.751.751 0 0 1-1.437-.432c.213-.706.592-1.303.997-1.834c.202-.266.419-.524.63-.774l.095-.112c.18-.213.355-.42.527-.634c.793-.99 1.425-2.025 1.425-3.561C18.5 5.243 15.81 2.5 12 2.5M8.75 18h6.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1 0-1.5m.75 3.75a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 0 1.5h-3.5a.75.75 0 0 1-.75-.75"/></svg>',
    "important": '<svg xmlns="http://www.w3.org/2000/svg" width="1.6em" height="1.6em" viewBox="0 0 56 56"><path fill="#8250df" d="M16.586 52.246c1.172 0 1.969-.61 3.375-1.875l8.11-7.195h15.023c6.984 0 10.734-3.867 10.734-10.735V14.488c0-6.867-3.75-10.734-10.734-10.734H12.906c-6.96 0-10.734 3.844-10.734 10.734v17.953c0 6.891 3.773 10.735 10.734 10.735h1.125v6.093c0 1.805.938 2.977 2.555 2.977m.96-4.289V41.16c0-1.265-.468-1.758-1.757-1.758h-2.86c-4.757 0-6.984-2.414-6.984-6.984v-17.93c0-4.57 2.227-6.96 6.985-6.96h30.164c4.734 0 6.96 2.39 6.96 6.96v17.93c0 4.57-2.226 6.984-6.96 6.984H27.906c-1.289 0-1.968.188-2.86 1.102Zm10.618-19.758c1.125 0 1.781-.633 1.805-1.851l.328-12.375c.023-1.196-.914-2.086-2.156-2.086c-1.266 0-2.157.867-2.133 2.062l.328 12.399c.024 1.195.656 1.851 1.828 1.851m0 7.617c1.36 0 2.531-1.078 2.531-2.437c0-1.36-1.148-2.438-2.53-2.438c-1.384 0-2.532 1.102-2.532 2.438s1.172 2.437 2.531 2.437"/></svg>',
    "warning": '<svg xmlns="http://www.w3.org/2000/svg" width="1.6em" height="1.6em" viewBox="0 0 20 20"><path fill="#9a6700" d="M9.562 3.262a.5.5 0 0 1 .88 0l6.5 12a.5.5 0 0 1-.44.739H3.5a.5.5 0 0 1-.44-.738zm1.758-.476c-.567-1.048-2.07-1.048-2.637 0l-6.502 12a1.5 1.5 0 0 0 1.318 2.215h13.003a1.5 1.5 0 0 0 1.319-2.215zM10.5 7.5a.5.5 0 0 0-1 0v4a.5.5 0 1 0 1 0zm.25 6.25a.75.75 0 1 1-1.5 0a.75.75 0 0 1 1.5 0"/></svg>',
    "caution": '<svg xmlns="http://www.w3.org/2000/svg" width="1.6em" height="1.6em" viewBox="0 0 256 256"><path fill="#d1242f" d="M120 136V80a8 8 0 0 1 16 0v56a8 8 0 0 1-16 0m112-44.45v72.9a15.86 15.86 0 0 1-4.69 11.31l-51.55 51.55a15.86 15.86 0 0 1-11.31 4.69h-72.9a15.86 15.86 0 0 1-11.31-4.69l-51.55-51.55A15.86 15.86 0 0 1 24 164.45v-72.9a15.86 15.86 0 0 1 4.69-11.31l51.55-51.55A15.86 15.86 0 0 1 91.55 24h72.9a15.86 15.86 0 0 1 11.31 4.69l51.55 51.55A15.86 15.86 0 0 1 232 91.55m-16 0L164.45 40h-72.9L40 91.55v72.9L91.55 216h72.9L216 164.45ZM128 160a12 12 0 1 0 12 12a12 12 0 0 0-12-12"/></svg>',
    "question": '<svg xmlns="http://www.w3.org/2000/svg" width="1.6em" height="1.6em" viewBox="0 0 24 24"><g fill="none"><path d="m12.593 23.258l-.011.002l-.071.035l-.02.004l-.014-.004l-.071-.035q-.016-.005-.024.005l-.004.01l-.017.428l.005.02l.01.013l.104.074l.015.004l.012-.004l.104-.074l.012-.016l.004-.017l-.017-.427q-.004-.016-.017-.018m.265-.113l-.013.002l-.185.093l-.01.01l-.003.011l.018.43l.005.012l.008.007l.201.093q.019.005.029-.008l.004-.014l-.034-.614q-.005-.018-.02-.022m-.715.002a.02.02 0 0 0-.027.006l-.006.014l-.034.614q.001.018.017.024l.015-.002l.201-.093l.01-.008l.004-.011l.017-.43l-.003-.012l-.01-.01z"/><path fill="#f08833" d="M12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12S6.477 2 12 2m0 2a8 8 0 1 0 0 16a8 8 0 0 0 0-16m0 12a1 1 0 1 1 0 2a1 1 0 0 1 0-2m0-9.5a3.625 3.625 0 0 1 1.348 6.99a.8.8 0 0 0-.305.201c-.044.05-.051.114-.05.18L13 14a1 1 0 0 1-1.993.117L11 14v-.25c0-1.153.93-1.845 1.604-2.116a1.626 1.626 0 1 0-2.229-1.509a1 1 0 1 1-2 0A3.625 3.625 0 0 1 12 6.5"/></g></svg>',
}
built_in_tags = {
    # matched name: ("css class", "tag color", "background color")
    "[!NOTE]": ("note", "#0969da", "#e8f3ff"),
    "[!TIP]": ("tip", "#1a7f37", "#e5f6ea"),
    "[!IMPORTANT]": ("important", "#8250df", "#eee4ff"),
    "[!WARNING]": ("warning", "#9a6700", "#fff4dd"),
    "[!CAUTION]": ("caution", "#d1242f", "#f7e5e6"),
    "[!QUESTION]": ("question", "#f08833", "#ffefe3"),
}

def markdown_tree_preprocess(tree: MarkdownParser.Block, file_path: str, github_repo_url: str, md_dir_name: str):
    """
    使用 syntaxlight 更新其中代码段的高亮
    https://github.com/luzhixing12345/syntaxlight
    """

    global CURRENT_FILE_PATH, REFERENCE_GRAPH
    CURRENT_FILE_PATH = file_path
    file_path = file_path.replace(os.sep, "/")

    # 初始化当前文件的引用列表
    if file_path not in REFERENCE_GRAPH:
        REFERENCE_GRAPH[file_path] = []

    def code_to_html(self: MarkdownParser.Block):
        return f'<pre class="language-{self.input["language"]}"><code>{self.input["code"]}</code></pre>'

    def pic_to_html(self: MarkdownParser.Block):
        word: str = self.input["word"]
        url: str = self.input["url"]
        if word.endswith("|mid"):
            word = word[:-4]
            pic_size = "middle"
        elif word.endswith("|small"):
            word = word[:-6]
            pic_size = "small"
        else:
            pic_size = "big"
        # 判断一下是否是本地图片
        local_url = os.path.normpath(os.path.join(os.path.dirname(file_path), unquote(url)))
        if not url.startswith("http") and os.path.exists(local_url):
            # https://raw.githubusercontent.com/luzhixing12345/paperplotlib/master/
            # https://github.com/luzhixing12345/paperplotlib/

            # 默认 master 分支
            server_url = github_repo_url.replace("github.com", "raw.githubusercontent.com") + "/master/"
            url = server_url + local_url

        return f'<a data-lightbox="example-1" href="{url}"><img loading="lazy" src="{url}" alt="{word}" class="pic-{pic_size}"></a>'

    def ref_to_html(self: MarkdownParser.Block):
        global CURRENT_FILE_PATH, REFERENCE_GRAPH
        url: str = self.input["url"]
        # 判断一下是否是本地的跳转链接
        local_url = os.path.normpath(os.path.join(os.path.dirname(file_path), unquote(url)))
        if not url.startswith("http") and local_url.endswith(".md"):
            if not os.path.exists(local_url):
                zood_info(f"[!] 文件 {file_path} 引用不存在的文件 {local_url}", "red")
                sys.exit(1)
            else:
                # 记录引用关系
                normalized_target = local_url.replace(os.sep, "/")
                normalized_source = CURRENT_FILE_PATH.replace(os.sep, "/")

                if normalized_target not in REFERENCE_GRAPH[normalized_source]:
                    REFERENCE_GRAPH[normalized_source].append(normalized_target)

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
                icon_html = built_in_icon_svgs[icon].replace(
                    "<svg ",
                    f'<svg class="icon-{icon}" aria-hidden="true" ',
                    1,
                )
                content = content.replace(
                    f"<p>{tag}",
                    f'<div style="color: {color};">{icon_html} {icon.upper()} </div><p>',
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
                        sys.exit()
                    else:
                        highlight_lines, highlight_tokens = parse_highlight_info(append_text)
                    exception = parse_result.error
                except Exception as e:
                    exception = e
                    print(f"解析错误: {file_path}: {exception}")
                    print(f'```{language}\n{block.input["code"]}\n```')
                    sys.exit()

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


def generate_reference_section(current_file_path: str, md_dir_name: str, directory_tree) -> str:
    """
    生成本文引用和本文被引用的HTML部分,使用选项卡形式
    """
    global REFERENCE_GRAPH

    # 标准化当前文件路径
    normalized_current = current_file_path.replace(os.sep, "/")

    # 获取本文引用的文件
    references_out = REFERENCE_GRAPH.get(normalized_current, [])

    # 获取引用本文的文件
    references_in = []
    for source_file, target_files in REFERENCE_GRAPH.items():
        if normalized_current in target_files:
            references_in.append(source_file)

    # 如果没有任何引用关系,返回空字符串
    if not references_out and not references_in:
        return ""

    # 构建文件路径到标题的映射
    file_to_title = {}
    for item in directory_tree:
        dir_name = list(item.keys())[0]
        files = item[dir_name]
        actual_dir = md_dir_name if dir_name == "." else dir_name
        for file_name in files:
            file_path = os.path.join(actual_dir, file_name + ".md").replace(os.sep, "/")
            # 简单使用文件名作为标题,你也可以从markdown中提取实际标题
            title = file_name.replace("_", " ").replace("-", " ")
            file_to_title[file_path] = title

    html_parts = []

    # 创建选项卡容器
    html_parts.append('<div class="references-tabs-container">')

    # 创建选项卡导航
    html_parts.append('<div class="references-tabs-nav">')

    if references_out:
        html_parts.append('<button class="references-tab-btn active" data-tab="references-out">本文引用</button>')

    if references_in:
        active_class = "active" if not references_out else ""
        html_parts.append(
            f'<button class="references-tab-btn {active_class}" data-tab="references-in">本文被引用</button>'
        )

    html_parts.append("</div>")

    # 创建选项卡内容
    html_parts.append('<div class="references-tabs-content">')

    # 本文引用选项卡内容
    if references_out:
        html_parts.append('<div class="references-tab-pane active" id="references-out">')
        html_parts.append('<ul class="reference-list">')
        for ref_file in references_out:
            title = file_to_title.get(ref_file, os.path.basename(ref_file).replace(".md", ""))
            # 构建相对URL
            ref_path = ref_file[len(md_dir_name) :].lstrip("/").replace(".md", "")
            if "/" not in ref_path:
                ref_path = f"{md_dir_name}/{ref_path}"
            ref_url = f"../../{ref_path}"
            html_parts.append(
                f'<li><a href="{ref_url}"><span class="reference-icon" aria-hidden="true"></span><span class="reference-title">{title}</span></a></li>'
            )
        html_parts.append("</ul>")
        html_parts.append("</div>")

    # 本文被引用选项卡内容
    if references_in:
        active_class = "active" if not references_out else ""
        html_parts.append(f'<div class="references-tab-pane {active_class}" id="references-in">')
        html_parts.append('<ul class="reference-list">')
        for ref_file in references_in:
            title = file_to_title.get(ref_file, os.path.basename(ref_file).replace(".md", ""))
            # 构建相对URL
            ref_path = ref_file[len(md_dir_name) :].lstrip("/").replace(".md", "")
            if "/" not in ref_path:
                ref_path = f"{md_dir_name}/{ref_path}"
            ref_url = f"../../{ref_path}"
            html_parts.append(
                f'<li><a href="{ref_url}"><span class="reference-icon" aria-hidden="true"></span><span class="reference-title">{title}</span></a></li>'
            )
        html_parts.append("</ul>")
        html_parts.append("</div>")

    html_parts.append("</div>")  # 结束 references-tabs-content
    html_parts.append("</div>")  # 结束 references-tabs-container

    return "\n".join(html_parts)


def generate_docs(directory_tree, markdown_htmls: Dict[str, str], config: DIR_TREE):
    html_dir_name = config["html_folder"]
    md_dir_name = config["markdown_folder"]
    index_README_path = os.path.join(md_dir_name, ".", "README.md")
    if not os.path.exists(index_README_path):
        zood_info(f"您需要保留 {md_dir_name}/README.md 作为首页")
        sys.exit()

    if os.path.exists(html_dir_name):
        robust_rmtree(html_dir_name)
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
    dir_tree_path = os.path.join(html_dir_name, "dir-tree.html")
    with open(dir_tree_path, "w", encoding="utf-8") as f:
        f.write(dir_tree_html)
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
        index_html_template = index_html_template.replace("../..", "./articles")
        index_html_template = index_html_template.replace("github-icon", github_icon)
        index_html_template = url_replace(index_html_template, front_url, next_url, "ab")

        index_markdown_html = markdown_htmls[index_README_path]
        # 把 index html 中的 ../../../img/{note}.svg 替换为 img/{note}.svg
        index_markdown_html = re.sub(r"../../../img/([a-zA-Z0-9_-]+)\.svg", r"img/\1.svg", index_markdown_html)
        f.write(index_html_template.replace("html-scope", index_markdown_html))

    # html_template = html_template.replace("directory-tree-scope", dir_tree_html)
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
            # 生成引用信息的JavaScript数据
            reference_section = generate_reference_section(file_path, md_dir_name, directory_tree)
            # 将引用信息嵌入到JavaScript中
            if reference_section:
                reference_js = f"""
                <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var markdownBody = document.querySelector('.markdown-body');
                    var giscusDiv = markdownBody.querySelector('.giscus');
                    var referenceHtml = `{reference_section}`;
                    
                    if (giscusDiv) {{
                        giscusDiv.insertAdjacentHTML('beforebegin', referenceHtml);
                    }} else {{
                        markdownBody.insertAdjacentHTML('beforeend', referenceHtml);
                    }}
                    
                    // 添加选项卡切换功能
                    setTimeout(function() {{
                        var tabButtons = document.querySelectorAll('.references-tab-btn');
                        var tabPanes = document.querySelectorAll('.references-tab-pane');
                        
                        tabButtons.forEach(function(button) {{
                            button.addEventListener('click', function() {{
                                var targetTab = this.getAttribute('data-tab');
                                
                                // 移除所有active类
                                tabButtons.forEach(btn => btn.classList.remove('active'));
                                tabPanes.forEach(pane => pane.classList.remove('active'));
                                
                                // 添加active类到当前选中的选项卡
                                this.classList.add('active');
                                var targetPane = document.getElementById(targetTab);
                                if (targetPane) {{
                                    targetPane.classList.add('active');
                                }}
                            }});
                        }});
                    }}, 100);
                }});
                </script>
                """
                markdown_html_with_refs = markdown_html + reference_js
            else:
                markdown_html_with_refs = markdown_html
            # print(html_path,front_url,next_url)
            final_html = url_replace(html_template, front_url, next_url, "ab")
            f.write(final_html.replace("html-scope", markdown_html_with_refs))
