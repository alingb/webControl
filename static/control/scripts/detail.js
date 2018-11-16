$(document).ready(function(){
    main();
});
function main() {
    show("fru");
    show("sel");
    show("locate");
    show("smart");
}

function show(id) {
    var num = 400
    var show = "....show all"
    var hidden = "hidden"
    var box = document.getElementById(id);
    var text = box.innerHTML;
    var newBox = document.createElement("div");
    var btn = document.createElement("a");

    newBox.innerHTML = text.substring(0, num);
    btn.innerHTML = text.length > num ? show : "";
    btn.href = "###";
    btn.onclick = function () {
        if (btn.innerHTML == show) {
            btn.innerHTML = hidden;
            newBox.innerHTML = text;
        } else {
            btn.innerHTML = show;
            newBox.innerHTML = text.substring(0, num);
        }
    };
    box.innerHTML = "";
    box.appendChild(newBox);
    box.appendChild(btn);
}
