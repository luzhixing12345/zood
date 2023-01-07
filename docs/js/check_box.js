
var inputs = document.getElementsByTagName('input')
for(var i=0;i<inputs.length;i++) {
    inputs[i].removeAttribute('disabled')
    inputs[i].onclick = function() {
        return false;
    }
}
let markdown_part = document.getElementsByClassName('markdown-body')[0]
markdown_part.className = 'markdown-body markdown-light'