document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.blurloader img').forEach(function (img) {
        if (!img.complete) {
            img.parentElement.classList.add("rotate");
            img.addEventListener('load', function () {
                img.style.opacity = "1";
                img.parentElement.classList.remove("rotate");
                img.parentElement.style.filter = "none";
            });
        } else {
            img.style.opacity = "1";
            img.parentElement.style.filter = "none";
            img.parentElement.classList.remove("rotate");
        }
    });
});