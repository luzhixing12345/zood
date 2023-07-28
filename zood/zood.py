import shutil
import os
import MarkdownParser
import json
from .util import *


def initZood(md_dir_name):
    # 初始化 zood 文件

    if os.path.exists(md_dir_name):
        print_info(f"{md_dir_name} 已存在,请删除文件夹后重试")
        return
    else:
        os.mkdir(md_dir_name)

        readme = ""
        if os.path.exists("README.md"):
            with open("README.md", "r", encoding="utf-8") as f:
                readme = f.read()
        # with open('.gitignore','a+',encoding='utf-8') as f:
        #     gitignore_files = f.read()
        #     if gitignore_files.find(f'/{md_dir_name}/') == -1:
        #         gitignore_files += f'\n./{md_dir_name}/\n'
        #         f.write(gitignore_files)

        initDirYml(md_dir_name)

        with open(os.path.join(md_dir_name, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)

        print_info(f"已初始化 [{md_dir_name}]", "green")


def createNewFile(md_dir_name, dir_name, file_name):
    file_path = os.path.join(md_dir_name, dir_name, file_name + ".md")

    if os.path.exists(file_path):
        print_info(f"{file_path} 已存在")
        return

    if not os.path.exists(os.path.join(md_dir_name, dir_name)):
        os.makedirs(os.path.join(md_dir_name, dir_name))

    updateDirYml(file_name, dir_name, md_dir_name)

    with open(file_path, "w", encoding="utf-8") as f:
        basic_info = f"\n# {file_name}\n"
        f.write(basic_info)

    print_info(f"创建文件 {file_path}", color="green")


def initDirYml(md_dir_name):
    # 生成目录记录
    dir_yml = {".": [{"README": 1}]}
    writeConfigFile(dir_yml, os.path.join(md_dir_name, "dir.yml"))


def updateDirYml(file_name, dir_name, md_dir_name):
    # 更新当前路径下的 dir.yml

    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir, md_dir_name, "dir.yml")
    dir_yml = readConfigFile(dir_yml_path)

    sort(dir_yml)

    if dir_name in dir_yml.keys():
        number = list(dir_yml[dir_name][-1].values())[0] + 1
        dir_yml[dir_name].append({file_name: number})
    else:
        dir_yml[dir_name] = []
        dir_yml[dir_name].append({file_name: 1})

    writeConfigFile(dir_yml, dir_yml_path)


def parseMarkdownFiles(md_dir_name):
    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir, md_dir_name, "dir.yml")
    dir_yml = readConfigFile(dir_yml_path)
    sort(dir_yml)
    directory_tree = []
    markdown_htmls = {}
    for dir_name, files in dir_yml.items():
        file_names = []
        for i in files:
            file_name = list(i.keys())[0]
            file_path = os.path.join(md_dir_name, dir_name, file_name + ".md")
            if not os.path.exists(file_path):
                print_info("[zood解析失败]: 找不到文件" + file_path)
                print("如手动删除md文件可使用 zood update 更新 dir.yml")
                exit(0)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    markdown_htmls[file_path] = MarkdownParser.parse_toc(f.read())
                file_names.append(file_name)
        directory_tree.append({dir_name: file_names})

    return directory_tree, markdown_htmls


def parseConfig(config, markdown_htmls):
    html_dir_name = config["html_folder"]
    html_tempate_path = os.path.join(os.path.dirname(__file__), "config", "template.html")
    css_template_path = os.path.join(os.path.dirname(__file__), "config", "index.css")

    with open(html_tempate_path, "r", encoding="utf-8") as f:
        basic_html_template = f.read()

    # js 部分
    js_scope = zoodJSOptions(config, markdown_htmls)
    basic_html_template = basic_html_template.replace("js-scope", js_scope)

    # css 部分
    prism_src = "../../../css/prism.css"
    index_src = "../../../css/index.css"

    css_scope = ""
    if config["options"]["enable_highlight"]:
        css_scope += f"<link rel='stylesheet' href={prism_src} />"
    css_scope += f"<link rel='stylesheet' href={index_src} />"
    basic_html_template = basic_html_template.replace("css-scope", css_scope)

    with open(css_template_path, "r", encoding="utf-8") as f:
        basic_css_template = f.read()
    favicon_url = config["favicon"]
    if favicon_url[:4] == "http":
        basic_html_template = basic_html_template.replace("<%favicon%>", favicon_url)

    else:
        img_name = favicon_url.split(os.sep)[-1]
        shutil.copy(favicon_url, f"./{html_dir_name}/img/" + img_name)
        basic_html_template = basic_html_template.replace("<%favicon%>", "../../../img/" + img_name)

    title = config["title"]
    basic_html_template = basic_html_template.replace("<%title%>", title)

    custom_options = getCustomOptions(config, ["color", "font", "position"])

    for k, v in custom_options:
        basic_css_template = basic_css_template.replace(f'"<%{k}%>"', v)

    basic_html_template = basic_html_template.replace("css-scope", css_scope)

    with open(f"./{html_dir_name}/css/index.css", "w", encoding="utf-8") as f:
        f.write(basic_css_template)

    return basic_html_template


def getCustomOptions(config, keys):
    custom_options = []
    for k in keys:
        custom_options += list(config[k].items())
    return custom_options


def zoodJSOptions(config, markdown_htmls):
    js_scope = ""
    html_dir_name = config["html_folder"]
    md_dir_name = config["markdown_folder"]

    if config["options"]["enable_next_front"]:
        js_code = insertJScode("enable_next_front", html_dir_name)
        js_code += f"<script>addLink(<%front_url%>,<%next_url%>,<%control%>)</script>"
        js_scope += js_code

    if config["options"]["enable_change_mode"]:
        js_code = insertJScode("enable_change_mode", html_dir_name)
        js_code += (
            f'<script>addChangeModeButton("../../../img/sun.png","../../../img/moon.png")</script>'
        )
        js_scope += js_code

    if config["options"]["enable_copy_code"]:
        js_code = insertJScode("enable_copy_code", html_dir_name)
        js_code += f'<script>addCodeCopy("../../../img/before_copy.png","../../../img/after_copy.png")</script>'
        js_scope += js_code

    if config["options"]["enable_navigator"]:
        js_code = insertJScode("enable_navigator", html_dir_name)
        js_scope += js_code

    if config["options"]["enable_highlight"]:
        # 复制prismjs
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "config", "js", "prismjs", "prism.css"),
            f"{html_dir_name}/css",
        )
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "config", "js", "prismjs", "prism.js"),
            f"{html_dir_name}/js",
        )
        src = "../../../js/prism.js"
        highlight = f'<script type="text/javascript" src="{src}"></script>'
        js_scope += highlight

    if config["options"]["enable_picture_title"]:
        js_code = insertJScode("enable_picture_title", html_dir_name)
        js_scope += js_code

    if config["options"]["enable_picture_preview"]:
        js_code = insertJScode("enable_picture_preview", html_dir_name)
        js_scope += js_code

    if config["options"]["enable_search"]["enable"]:
        js_code = insertJScode("enable_search", html_dir_name)
        all_api_text = getAllAPIText(
            markdown_htmls,
            config["options"]["enable_search"]["search_scope"],
            md_dir_name,
        )
        js_code += f'<script>addSearchBar({all_api_text},"../../../img/search.svg","../../../img/enter.svg","Ctrl+K")</script>'
        js_scope += js_code

    if config["options"]["enable_mermaid"]:
        js_code = "<script type=\"module\">\
const codeBlocks = document.querySelectorAll('.language-mermaid');\
codeBlocks.forEach(codeBlock => {\
    codeBlock.classList.remove('language-mermaid');\
    codeBlock.classList.add('mermaid');\
});\
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';\
mermaid.initialize({ startOnLoad: true });\
</script>"
        js_scope += js_code

    if config["options"]["enable_latex"]:
        js_code = """
        <script>
            MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']]
            }
            };
            </script>
        <script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
        </script>
        """
        js_scope += js_code

    js_scope += insertJScode("global_js_configuration", html_dir_name)

    return js_scope


def insertJScode(file_name: str, html_dir_name):
    if file_name.startswith("enable_"):
        # 跳过enable_
        file_name = file_name[7:]
    js_file_name = os.path.join(os.path.dirname(__file__), "config", "js", f"{file_name}.js")
    if os.path.exists(js_file_name):
        shutil.copy(
            js_file_name,
            f"{html_dir_name}/js",
        )
    src = f"../../../js/{file_name}.js"
    js_code = f'<script type="text/javascript" src="{src}"></script>'
    return js_code
