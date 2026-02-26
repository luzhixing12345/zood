# zood

zood 网页文档生成的 python 库, 可以将本地 Markdown 文件转为 Web 网页

zood 的页面风格更倾向于纯文档内容而非博客, 您可利用 Github Pages 为每一个仓库部署单独的网页文档

zood 基于 [MarkdownParser](https://github.com/luzhixing12345/MarkdownParser) 完成 Markdown 文件的解析和转换

您可前往 [【项目分享】zood:项目文档生成工具](https://www.bilibili.com/video/BV1dK411r77d) 浏览一个相关视频介绍

## changelog

- 2026/02/26: 代码块复制按钮改为内联 SVG（copy/copy-success）并支持横向滚动时固定在右上角；引用区 reference-icon 与 Quote 内置标签（NOTE/TIP/IMPORTANT/WARNING/CAUTION/QUESTION）图标改为内联 SVG（不再依赖 `img/*.svg`）；移除 change_mode/next_front 相关脚本与暗色主题分支并清理对应静态资源；优化 server 启动信息显示与 WSL 浏览器打开方式
- 2026/01/12: 修复 github pages 上根页面路径判断错误导致页面显示出错的问题
- 2026/01/09: 支持 zood 服务器多开，分配不同的 websocket 端口
- 2026/01/07: 分离 dir-tree 结构保存为单独的 html 文件
