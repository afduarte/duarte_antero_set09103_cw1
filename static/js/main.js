// Util LocalStorage Object
const LocalStorage = {
    getItem: key => JSON.parse(localStorage.getItem(key)),
    getItemOrElse: (key, defaultVal) => {
        try {
            const stored = localStorage.getItem(key);
            if (stored === null) {
                throw new Error();
            }
            return JSON.parse(stored);
        } catch (_) {
            return defaultVal;
        }
    },
    setItem: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    removeItem: key => localStorage.removeItem(key),
};

// Search Functionality
// It uses the old XMLHttpRequest because it's easier to handle request.abort()
const search = document.getElementById("search");
let oReq = new XMLHttpRequest();
const datalist = document.getElementById("search-results");
search.addEventListener('input', function () {
    const icon = document.getElementById('search-icon');
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
        const itemsArr = Array.prototype.slice.call(datalist.children);
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

// Hide/Show search results on focusout
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

// Open/close the setlist sidebar
const setlistBtn = document.getElementById("setlist-opener");
const setlist = document.getElementById("setlist");

function changeSidebar(open) {
    if (open) {
        setlist.classList.add('open');
        // We have to use 25% of the body width here, since setlist's width is still 0
        const width = document.body.clientWidth / 4;
        setlistBtn.style.width = width + 'px';
    } else {
        setlist.classList.remove('open');
        setlistBtn.style.width = '5em'

    }
    LocalStorage.setItem("sidebar.open", open);
}

function toggleSidebar() {
    changeSidebar(!setlist.classList.contains('open'))
}

// Add the event handler
setlistBtn.addEventListener('click', toggleSidebar);

// Initially open or close based on localStorage
changeSidebar(LocalStorage.getItemOrElse("sidebar.open", false));

addListenersToSetlistButtons('#tracks');
addListenersToSetlistButtons('#setlist');

function addListenersToSetlistButtons(where) {
    document.querySelectorAll(`${where} .setlist-changer button`)
        .forEach(btn => {
            btn.addEventListener('click', evt => {
                evt.preventDefault();
                evt.stopPropagation();
                // Find parent form
                const f = evt.path.find(e => e.tagName.toLowerCase() === "form");
                const index = Array.from(document.forms).indexOf(f);
                if (index > -1) {
                    let promise;
                    const form = document.forms[index];
                    const action = form.elements['_action'].value;
                    switch (action) {
                        case "remove":
                            promise = fetch(form.action, {method: "DELETE", credentials: "include"});
                            break;
                        case "add":
                        default:
                            promise = fetch(form.action, {method: "PUT", credentials: "include"});

                    }
                    promise.then(data => {
                        if (data.status === 200) {
                            return fetch("/setlist", {credentials: 'include'})
                                .then(data => data && data.status === 200 ? data.text() : Promise.reject())
                                .then(html => {
                                    document.getElementById('setlist').innerHTML = html;
                                    addListenersToSetlistButtons('#setlist');
                                })
                        } else {
                            return Promise.reject(`Error when submitting ${action} action to ${form.action}`)
                        }
                    }).catch(e => console.error(e))
                }
            })
        });
}
