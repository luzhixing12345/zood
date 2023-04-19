
var global_api_text; // API目录下所有的文章内容
var selected_item_index = -1; // 被选中的项
var searched_result_length = 0; // 所有搜索结果的长度

var enter_img_src;

var center_search_div = document.createElement('div')
center_search_div.className = 'center-search'

// header
var center_search_header = document.createElement('div')
center_search_header.className = 'search-header'

var center_search_img = document.createElement('img')
var center_search_input = document.createElement('input')
center_search_input.placeholder = '请输入查询内容'

center_search_header.appendChild(center_search_input)
center_search_header.appendChild(center_search_img)

// search result
var center_search_result = document.createElement('div')
center_search_result.className = 'search-result'

center_search_div.appendChild(center_search_header)
center_search_div.appendChild(center_search_result)
document.body.appendChild(center_search_div)


var is_display = false;
center_search_input.onfocus = function() {
    selected_item_index = -1;
    center_search_result.innerHTML = ''
}




function displayCenterSearch() {

    if (!is_display) {
        center_search_div.style.display = 'block';
        black_overlay.style.display = 'block';
        center_search_input.focus();
        is_display = !is_display;
    }
}


function closeCenterSearch() {
    center_search_div.style.display = 'none';
    black_overlay.style.display = 'none';
    is_display = !is_display;
    center_search_input.value = '';
    // deactivate_searched_items();
    center_search_result.innerHTML = ''
    selected_item_index = -1;
}



function startSearch(word) {
    center_search_result.innerHTML = ''
    var front_word_length = 15;
    var back_word_length = 15;

    var start_index;
    searched_result_length = 0;

    for (var i in global_api_text) {
        var api_text = global_api_text[i];
        var index = api_text.toLowerCase().indexOf(word);

        if (index != -1) {
            // 最多搜索数8
            if (searched_result_length == 8) {
                break;
            }
            searched_result_length += 1;
            const search_result = document.createElement('div');
            search_result.className = 'search-result-item';
            search_result.src = i;
            const enter_img = document.createElement('img');
            enter_img.className = 'enter-img';
            
            if (index > front_word_length) start_index = index - front_word_length;
            else start_index = 0;

            search_result.innerHTML = api_text.substr(start_index, index-start_index) + '<code>' + word + '</code>' + api_text.substr(index + word.length, back_word_length);
            search_result.appendChild(enter_img)
            center_search_result.appendChild(search_result)
        }
    }
    selected_item_index = 0;
    deactivate_searched_items();
    activeSelectedItem();
}

function deactivate_searched_items() {
    var items = document.getElementsByClassName('search-result-item');
    for (var i = 0; i < items.length; i++) {
        items[i].classList.remove('search-selected');
        items[i].lastChild.src = ''
    }
}


function activeSelectedItem() {

    if (searched_result_length == 0) {
        selected_item_index = -1;
        return;
    }

    center_search_input.blur();
    selected_item_index = (selected_item_index + searched_result_length) % searched_result_length;
    // console.log(selected_item_index,searched_result_length)
    var selected_item = document.getElementsByClassName('search-result-item')[selected_item_index];
    selected_item.classList.add('search-selected');
    selected_item.lastChild.src = enter_img_src;
}


function addSearchBar(API_text, search_src, enter_src, key_map) {

    global_api_text = JSON.parse(API_text);
    // console.log(global_api_text)
    center_search_img.src = search_src;
    enter_img_src = enter_src;

    var search_bar = document.createElement('div');
    search_bar.className = 'search-bar';

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        if (savedTheme == 'dark') {
            search_bar.style.backgroundColor = "#252D38";
        } else {
            search_bar.style.backgroundColor = "#f6f8fa";
        }
    }

    var search_img = document.createElement('img');
    var search_keymap = document.createElement('div');
    search_keymap.className = 'search-keymap';
    search_keymap.innerText = 'Search ' + key_map;
    search_img.src = search_src;
    search_bar.appendChild(search_img);
    search_bar.appendChild(search_keymap);
    search_bar.onclick = displayCenterSearch;
    document.body.appendChild(search_bar);
}

document.onkeydown = function (e) {
    // event.preventDefault();
    var ev = window.event || e;
    if (ev.key === 'k' && ev.ctrlKey) {
        displayCenterSearch()
        ev.preventDefault()
    }
    if (ev.keyCode == 27) {
        // ESC
        closeCenterSearch()
        ev.preventDefault()
    }
    if (ev.which === 13) {
        // enter
        var word = center_search_input.value.trim();
        if (word === '') {
            closeCenterSearch()
            return;
        }
        if (selected_item_index == -1) {
            // 没有开始选择
            startSearch(word)
        } else {
            window.location = document.getElementsByClassName('search-result-item')[selected_item_index].src
        }

    }
    if (ev.keyCode == 38) {
        // 上
        selected_item_index -= 1;
        deactivate_searched_items()
        activeSelectedItem()
        ev.preventDefault()
    } else if (ev.keyCode == 40) {
        // 下
        selected_item_index += 1;
        deactivate_searched_items()
        activeSelectedItem()
        ev.preventDefault()
    }
}