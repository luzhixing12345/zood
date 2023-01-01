
function addButton(x,text,url) {

    var button = document.createElement('button');
    button.innerText = text;
    button.setAttribute('url',url)
    button.className = 'change-article';
    button.onclick = function () {
        window.location= this.getAttribute('url')
    }
    x.appendChild(button)
}

function addLink(front_url,next_url) {
    let body = document.body;
    var next_front = document.createElement('div')
    next_front.className = 'next-front'

    addButton(next_front,'上一个',front_url)
    addButton(next_front,'下一个',next_url)

    body.appendChild(next_front)
}

