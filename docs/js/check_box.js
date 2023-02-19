
var inputs = document.getElementsByTagName('input')
for(var i=0;i<inputs.length;i++) {
    inputs[i].removeAttribute('disabled')
    inputs[i].onclick = function() {
        return false;
    }
}

// checkbox 全局生效
// 这里可以写一些在全局生效的代码

let markdown_part = document.getElementsByClassName('markdown-body')[0]
markdown_part.className = 'markdown-body markdown-light'

var currentUrl = window.location.href.slice(0, -1);
var dirTree = document.querySelector(".dir-tree");
var links = dirTree.querySelectorAll("a");
links.forEach(function(link) {
  if (link.href === currentUrl) {
    link.classList.add("link-active");
  }
});