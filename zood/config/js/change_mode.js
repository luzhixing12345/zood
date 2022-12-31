function changeMode() {
    let body = document.body;
    let markdown_part = document.getElementById('markdown')
    let box = document.getElementById('changeMode')
    if (box.state == null) {
        box.state = false;
    }
    if (box.state) {
        body.className = 'light';
        markdown_part.className = 'markdown-body markdown-light'
        box.src = "../../../img/sun-line.png"
    } else {
        body.className = 'dark';
        markdown_part.className = 'markdown-body markdown-dark'
        box.src = "../../../img/moon-line.png"
    }
    box.state = !box.state;
}




// 添加切换颜色

var change_mode_button = document.createElement('img')
change_mode_button.src = "../../../img/sun-line.png"
change_mode_button.className = 'changeMode'
change_mode_button.id = 'changeMode'
change_mode_button.innerText = '切换颜色'
change_mode_button.onclick = changeMode
document.body.appendChild(change_mode_button)