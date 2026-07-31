(function () {
    "use strict";

    var sidebar = document.getElementById("sgmSidebar");
    var overlay = document.getElementById("sgmOverlay");
    var sidebarToggle = document.getElementById("sidebarToggle");
    var themeToggle = document.getElementById("themeToggle");
    var root = document.documentElement;

    function closeSidebar() {
        if (!sidebar || !overlay) return;
        sidebar.classList.remove("open");
        overlay.classList.remove("show");
        document.body.style.overflow = "";
    }

    function openSidebar() {
        if (!sidebar || !overlay) return;
        sidebar.classList.add("open");
        overlay.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", function () {
            if (sidebar && sidebar.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
        localStorage.setItem("sgm-theme", theme);

        if (themeToggle) {
            var icon = themeToggle.querySelector("i");
            if (icon) {
                icon.className = theme === "dark" ? "fa fa-sun-o" : "fa fa-moon-o";
            }
        }
    }

    var savedTheme = localStorage.getItem("sgm-theme");
    if (savedTheme === "dark" || savedTheme === "light") {
        applyTheme(savedTheme);
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            var current = root.getAttribute("data-theme") || "light";
            applyTheme(current === "dark" ? "light" : "dark");
        });
    }

    window.addEventListener("resize", function () {
        if (window.innerWidth >= 992) {
            closeSidebar();
        }
    });
}());
