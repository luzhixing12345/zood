
var inputs = document.getElementsByTagName('input')
for(var i=0;i<inputs.length;i++) {
    console.log(inputs[i])
    inputs[i].removeAttribute('disabled')
    inputs[i].onclick = function() {
        return false;
    }
}