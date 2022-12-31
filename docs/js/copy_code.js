function addCodeCopy(block) {
    var clip_board = document.createElement('img');
    clip_board.id = 'code_copy';
    clip_board.src = "../../../img/code_copy.png"
    clip_board.onclick = function() {
        clip_board.src = "../../../img/copyed.png"
        navigator.clipboard.writeText(block.firstChild.innerHTML);
    }
    block.appendChild(clip_board)
}

function removeCodeCopy(block) {
    var clip_board = document.getElementById('code_copy')
    block.removeChild(clip_board)
}

// 为所有代码段添加可以复制的标记
var code_blocks = document.getElementsByTagName('pre')
for(var i=0;i<code_blocks.length;i++) {
    const code_block = code_blocks[i];
    code_block.addEventListener("mouseenter",()=>addCodeCopy(code_block))
    code_block.addEventListener("mouseleave",()=>removeCodeCopy(code_block))
}