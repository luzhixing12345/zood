

var images = document.getElementsByTagName('img');
for(var i=0;i<images.length;i++) {
    if (images[i].className == 'changeMode') continue;
    const p = document.createElement('p');
    p.innerText = images[i].getAttribute('alt');
    images[i].parentNode.appendChild(p);
}