(function () {
    "use strict";

    var form = document.querySelector(".departments-toolbar");
    var search = form ? form.querySelector('input[type="search"]') : null;

    if (!search || !form) {
        return;
    }

    search.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && search.value) {
            search.value = "";
            form.submit();
        }
    });
}());
