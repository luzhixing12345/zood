// 目录树展开折叠功能
function toggleDirectory(event, linkElement) {
    // 阻止默认的链接跳转行为
    event.preventDefault();
    event.stopPropagation();

    // 获取一级目录的li元素
    const parentLi = linkElement.parentElement;
    // 获取这个li下的所有二级ul元素
    const subUls = parentLi.querySelectorAll('ul');

    if (subUls.length > 0) {
        // 获取第一个二级ul的状态来决定是展开还是折叠
        const isCollapsed = subUls[0].classList.contains('collapsed');

        // 获取目录名称作为存储key
        const dirName = linkElement.textContent.trim();

        // 对所有二级ul应用相同的状态
        subUls.forEach(function (subUl) {
            if (isCollapsed) {
                // 展开
                subUl.classList.remove('collapsed');
                subUl.style.height = 'auto';
            } else {
                // 折叠
                subUl.classList.add('collapsed');
                subUl.style.height = '0';
            }
        });

        // 保存状态到 localStorage
        saveDirTreeState(dirName, !isCollapsed);
    }
}

// 保存目录树状态到 localStorage
function saveDirTreeState(dirName, isCollapsed) {
    try {
        let dirTreeStates = JSON.parse(localStorage.getItem('dirTreeStates') || '{}');
        dirTreeStates[dirName] = isCollapsed;
        localStorage.setItem('dirTreeStates', JSON.stringify(dirTreeStates));
    } catch (e) {
        console.warn('无法保存目录树状态:', e);
    }
}

// 从 localStorage 获取目录树状态
function getDirTreeState(dirName) {
    try {
        let dirTreeStates = JSON.parse(localStorage.getItem('dirTreeStates') || '{}');
        return dirTreeStates[dirName];
    } catch (e) {
        console.warn('无法读取目录树状态:', e);
        return undefined;
    }
}

// 获取当前页面所在的目录名
function getCurrentDirectory() {
    const path = window.location.pathname;
    // 解码URL路径中的中文字符
    const decodedPath = decodeURIComponent(path);

    // 匹配路径模式，可能的格式：
    // /articles/{dir}/{page}/ 或 /articles/{dir}/{page}
    // 或者 /{dir}/{page}/ 或 /{dir}/{page}

    // 首先尝试匹配包含articles的路径
    let match = decodedPath.match(/\/articles\/([^\/]+)\/[^\/]+\/?$/);
    if (match) {
        return match[1];
    }

    // 然后尝试匹配不包含articles的路径
    match = decodedPath.match(/\/([^\/]+)\/[^\/]+\/?$/);
    if (match) {
        return match[1];
    }

    // 最后尝试简单的两级路径
    match = decodedPath.match(/^\/([^\/]+)\/[^\/]+\/?$/);
    if (match) {
        return match[1];
    }

    return null;
}

// 检查目录链接是否指向当前目录
function isCurrentDirectory(linkElement) {
    const currentDir = getCurrentDirectory();
    if (!currentDir) return false;

    const linkHref = linkElement.getAttribute('href');
    if (!linkHref) return false;

    // 获取链接显示的文本作为目录名进行对比
    const linkText = linkElement.textContent.trim();

    // 直接对比目录名（处理中文字符）
    if (linkText === currentDir) {
        return true;
    }

    // 作为备选方案，也尝试从href中提取目录名
    // 对href进行解码处理中文字符
    const decodedHref = decodeURIComponent(linkHref);

    // 可能的格式：../../{dir}/{page} 或 ./{dir}/{page} 或 {dir}/{page}
    let match = decodedHref.match(/(?:\.\.\/)*([^\/]+)\/[^\/]*$/);
    if (match && match[1] === currentDir) {
        return true;
    }

    return false;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    // 找到目录树
    const dirTree = document.querySelector('.dir-tree');
    if (dirTree) {
        const topLevelUls = dirTree.querySelectorAll(':scope > ul');

        topLevelUls.forEach(function (ul) {
            const li = ul.querySelector('li');
            if (li) {
                // 检查这个li是否包含子ul（即有子目录）
                const subUls = li.querySelectorAll('ul');
                if (subUls.length > 0) {
                    // 找到这个li中的第一个链接（一级目录标题）
                    const firstLink = li.querySelector(':scope > a');
                    if (firstLink) {
                        // 为这个链接添加点击事件
                        firstLink.addEventListener('click', function (event) {
                            toggleDirectory(event, this);
                        });

                        // 为一级目录链接添加样式标识
                        firstLink.style.cursor = 'pointer';
                        firstLink.style.userSelect = 'none';
                    }
                }
            }
        });

        // 恢复之前保存的目录树状态
        const subUls = dirTree.querySelectorAll('ul ul');
        subUls.forEach(function (subUl) {
            // 获取父级li元素
            const parentLi = subUl.closest('li');
            if (parentLi) {
                // 获取一级目录的链接
                const firstLink = parentLi.querySelector(':scope > a');
                if (firstLink) {
                    const dirName = firstLink.textContent.trim();
                    const savedState = getDirTreeState(dirName);

                    // 检查是否是当前页面所在的目录
                    const isCurrentDir = isCurrentDirectory(firstLink);

                    if (isCurrentDir) {
                        // 如果是当前目录，强制展开
                        subUl.classList.remove('collapsed');
                        subUl.style.height = 'auto';
                    } else if (savedState === true) {
                        // 其他目录：如果之前是折叠状态，保持折叠
                        subUl.classList.add('collapsed');
                        subUl.style.height = '0';
                    } else {
                        // 其他目录：默认展开状态或之前是展开状态
                        subUl.classList.remove('collapsed');
                        subUl.style.height = 'auto';
                    }
                }
            }
        });

        // 处理完状态后移除loading类，目录树以正确状态显示
        dirTree.classList.remove('loading');
    }
}); 