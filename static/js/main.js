// Search Functionality
var search = document.getElementById("search");
var oReq = new XMLHttpRequest();
var datalist = document.getElementById("search-results");
search.addEventListener('input', function () {
    var icon = document.getElementById('search-icon');
    icon.className = "icono-sync";
    if (oReq) {
        oReq.abort();
        oReq = new XMLHttpRequest();
        datalist.innerHTML = "";
    }
    oReq.onreadystatechange = function () {
        if (this.readyState > 2) {
            datalist.innerHTML = this.responseText;
        }
        var itemsArr = Array.prototype.slice.call(datalist.children);
        if (itemsArr.length > 1) {
            itemsArr.sort(function (a, b) {
                return b.dataset.score - a.dataset.score;
            });
        }

        for (i = 0; i < itemsArr.length; ++i) {
            datalist.appendChild(itemsArr[i]);
        }
        if (this.readyState >= 4) {
            icon.className = "icono-search";
        }
    };
    oReq.open("get", "/search?stream=true&query=" + encodeURIComponent(search.value), true);
    oReq.send();
});

search.addEventListener('focusout', function () {
    setTimeout(function () {
        datalist.style.opacity = "0";
    }, 50);
    setTimeout(function () {
        datalist.style.display = "none";
    }, 200);
});

search.addEventListener('focus', function () {
    datalist.style.opacity = "1";
    datalist.style.display = "flex";
});

var setlistBtn = document.getElementById("setlist-opener");
var setlist = document.getElementById("setlist");

setlistBtn.addEventListener('click', function () {
    if (setlist.classList.contains('open')) {
        setlist.classList.remove('open');
        setlistBtn.style.width = '5em';
    } else {
        setlist.classList.add('open');
        // We have to use 25% of the body width here, since setlist's width is still 0
        var width = document.body.clientWidth / 4;
        setlistBtn.style.width = width + 'px';
    }
});