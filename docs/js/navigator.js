
const divElement = document.getElementsByClassName("header-navigator")[0]; // 获取目标div元素
divElement.style.display = "block"; // 将display属性设置为block，以显示元素

let navigator_links = document.querySelectorAll('div a[href^="#"]');
navigator_links.forEach(link => {
    link.addEventListener('click', function (event) {
        event.preventDefault();
        let target = document.querySelector(this.getAttribute('href'));
        target.scrollIntoView({ behavior: 'smooth',block: 'start', inline: 'nearest'});
    });
});