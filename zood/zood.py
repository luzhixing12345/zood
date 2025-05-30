import shutil
import os
from .util import *
import re


def init_zood(md_dir_name):
    # 初始化 zood 文件

    if os.path.exists(md_dir_name):
        zood_info(f"{md_dir_name} 已存在,请删除文件夹后重试")
        return
    else:
        os.mkdir(md_dir_name)

        readme = ""
        if os.path.exists("README.md"):
            with open("README.md", "r", encoding="utf-8") as f:
                readme = f.read()

        init_dir_yml(md_dir_name)

        with open(os.path.join(md_dir_name, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)

        zood_info(f"已初始化 [{md_dir_name}]", "green")


def create_new_file(md_dir_name, dir_name, file_name):
    file_path = os.path.join(md_dir_name, dir_name, file_name + ".md")

    if os.path.exists(file_path):
        zood_info(f"{file_path} 已存在")
        return

    if not os.path.exists(os.path.join(md_dir_name, dir_name)):
        os.makedirs(os.path.join(md_dir_name, dir_name))

    update_dir_yml(file_name, dir_name, md_dir_name)

    with open(file_path, "w", encoding="utf-8") as f:
        basic_info = f"\n# {file_name}\n"
        f.write(basic_info)

    zood_info(f"创建文件 {file_path}", color="green")


def init_dir_yml(md_dir_name):
    # 生成目录记录
    dir_yml = {".": [{"README": 1}]}
    save_yml(dir_yml, os.path.join(md_dir_name, "dir.yml"))


def update_dir_yml(file_name, dir_name, md_dir_name):
    # 更新当前路径下的 dir.yml

    current_dir = os.getcwd()
    dir_yml_path = os.path.join(current_dir, md_dir_name, "dir.yml")
    dir_yml = load_yml(dir_yml_path)

    yml_sort(dir_yml)

    if dir_name in dir_yml.keys():
        number = list(dir_yml[dir_name][-1].values())[0] + 1
        dir_yml[dir_name].append({file_name: number})
    else:
        dir_yml[dir_name] = []
        dir_yml[dir_name].append({file_name: 1})

    save_yml(dir_yml, dir_yml_path)


def parse_config(config):
    html_dir_name = config["html_folder"]
    html_tempate_path = os.path.join(os.path.dirname(__file__), "config", "template.html")
    css_template_path = os.path.join(os.path.dirname(__file__), "config", "index.css")

    with open(html_tempate_path, "r", encoding="utf-8") as f:
        basic_html_template = f.read()

    # js 部分
    js_scope = zood_js_options(config)
    basic_html_template = basic_html_template.replace("js-scope", js_scope)

    # css 部分
    # prism_src = "../../../css/prism.css"
    index_src = "../../../css/index.css"

    css_scope = ""
    # if config["options"]["enable_highlight"]:
    #     css_scope += f"<link rel='stylesheet' href={prism_src} />"
    css_scope += f"<link rel='stylesheet' href={index_src} />"
    basic_html_template = basic_html_template.replace("css-scope", css_scope)

    with open(css_template_path, "r", encoding="utf-8") as f:
        basic_css_template = f.read()
    favicon_url: str = config["favicon"]
    if favicon_url[:4] == "http":
        basic_html_template = basic_html_template.replace("<%favicon%>", favicon_url)

    else:
        img_name = favicon_url.split(os.sep)[-1]
        shutil.copy(favicon_url, f"./{html_dir_name}/img/" + img_name)
        basic_html_template = basic_html_template.replace("<%favicon%>", "../../../img/" + img_name)

    title = config["title"]
    basic_html_template = basic_html_template.replace("<%title%>", title)

    custom_options = get_custom_options(config, ["color", "font", "position"])

    for k, v in custom_options:
        basic_css_template = basic_css_template.replace(f'"<%{k}%>"', v)

    basic_html_template = basic_html_template.replace("css-scope", css_scope)

    with open(f"./{html_dir_name}/css/index.css", "w", encoding="utf-8") as f:
        f.write(basic_css_template)

    return basic_html_template


def get_custom_options(config, keys):
    custom_options = []
    for k in keys:
        custom_options += list(config[k].items())
    return custom_options


def zood_js_options(config):
    js_scope = ""
    html_dir_name = config["html_folder"]

    if config["options"]["enable_next_front"]:
        js_code = insert_js_code("enable_next_front", html_dir_name)
        js_code += f"<script>addLink(<%front_url%>,<%next_url%>,<%control%>);</script>"
        js_scope += js_code

    if config["options"]["enable_change_mode"]:
        js_code = insert_js_code("enable_change_mode", html_dir_name)
        js_code += f'<script>addChangeModeButton("../../../img/sun.png","../../../img/moon.png");</script>'
        js_scope += js_code

    if config["options"]["enable_copy_code"]:
        js_code = insert_js_code("enable_copy_code", html_dir_name)
        js_code += f'<script>addCodeCopy("../../../img/clipboard.svg","../../../img/clipboard-check.svg");</script>'
        js_scope += js_code

    if config["options"]["enable_navigator"]:
        js_code = insert_js_code("enable_navigator", html_dir_name)
        js_scope += js_code

    if config["options"]["enable_picture_title"]:
        js_code = insert_js_code("enable_picture_title", html_dir_name)
        js_scope += js_code

    if config["options"]["enable_picture_preview"]:
        js_code = insert_js_code("enable_picture_preview", html_dir_name)
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

    if config["options"]["enable_comment"]["enable"]:

        # https://github.com/luzhixing12345/zood.git
        # data_repo = {user_name}/{repo_name}
        if GITHUB_REPO_URL == "":
            zood_info("没有从 git 找到有效的 github 地址, 无法启用评论功能")
        else:
            data_repo = re.match(r"https://github.com/([^/]+)/([^/]+).git", GITHUB_REPO_URL).groups()
            data_repo_id = config["options"]["enable_comment"]["repoid"]
            data_category_id = config["options"]["enable_comment"]["categoryid"]
            js_code = f"""
            <script src="https://giscus.app/client.js" data-repo="{data_repo[0]}/{data_repo[1]}" 
            data-repo-id="{data_repo_id}" data-category="Q&A" data-category-id="{data_category_id}" data-mapping="pathname" data-strict="0"
            data-reactions-enabled="1" data-emit-metadata="0" data-input-position="bottom"
            data-theme="preferred_color_scheme" data-lang="zh-CN" crossorigin="anonymous" async>
            </script>
            """
            js_scope += js_code

    js_scope += insert_js_code("dir_tree_toggle", html_dir_name)
    js_scope += insert_js_code("global_js_configuration", html_dir_name)

    return js_scope


def insert_js_code(file_name: str, html_dir_name):
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
