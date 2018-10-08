// Search Functionality
var search = document.getElementById("search");
var oReq = new XMLHttpRequest();
var datalist = document.getElementById("search-results");
search.addEventListener('input', function () {
    if (oReq) {
        oReq.abort();
        oReq = new XMLHttpRequest();
        datalist.innerHTML = "";
    }
    oReq.onreadystatechange = function () {
        if (this.readyState > 2) {
            datalist.innerHTML = this.responseText;
        }
        var itemsArr = datalist.children;

        itemsArr.sort(function (a, b) {
            return a.dataset.score > b.dataset.score;
        });

        for (i = 0; i < itemsArr.length; ++i) {
            datalist.appendChild(itemsArr[i]);
        }
    };
    oReq.open("get", "/search?stream=true&query=" + encodeURIComponent(search.value), true);
    oReq.send();
});