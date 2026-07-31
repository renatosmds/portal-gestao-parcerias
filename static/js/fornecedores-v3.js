(function () {
    "use strict";

    var form = document.querySelector(".suppliers-toolbar");
    var search = form ? form.querySelector('input[type="search"]') : null;

    if (!form || !search) {
        return;
    }

    search.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && search.value) {
            search.value = "";
            form.submit();
        }
    });
}());
