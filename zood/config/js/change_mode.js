
var global_sun_src;
var global_moon_src;

function changeThemeMode() {
    let body = document.body;
    let markdown_part = document.getElementsByClassName('markdown-body')[0]
    let box = document.getElementById('changeThemeMode')
    let change_article_boxes = document.getElementsByClassName('change-article')
    if (box.state == null) {
        box.state = false;
    }
    if (box.state) {
        body.className = 'light';
        markdown_part.className = 'markdown-body markdown-light'
        box.src = global_sun_src;
        for(b of change_article_boxes) {
            b.classList.remove('change-dark');
        }
        
    } else {
        body.className = 'dark';
        markdown_part.className = 'markdown-body markdown-dark'
        box.src = global_moon_src;
        for(b of change_article_boxes) {
            b.classList.add('change-dark');
        }
    }
    box.state = !box.state;
}

// 添加切换颜色
function addChangeModeButton(sun_src,moon_src) {
    global_sun_src = sun_src;
    global_moon_src = moon_src;
    var change_mode_button = document.createElement('img')
    change_mode_button.src = sun_src;
    change_mode_button.className = 'changeMode'
    change_mode_button.id = 'changeThemeMode'
    change_mode_button.onclick = changeThemeMode
    document.body.appendChild(change_mode_button)
}
