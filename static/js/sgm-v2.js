(function () {
    "use strict";
    var sidebar = document.getElementById("sgmSidebar");
    var overlay = document.getElementById("sgmOverlay");
    var sidebarToggle = document.getElementById("sidebarToggle");
    var themeToggle = document.getElementById("themeToggle");
    var root = document.documentElement;

    function isDesktop(){ return window.innerWidth >= 992; }
    function closeMobileSidebar(){
        if (!sidebar || !overlay) return;
        sidebar.classList.remove("open"); overlay.classList.remove("show"); document.body.style.overflow="";
    }
    function openMobileSidebar(){
        if (!sidebar || !overlay) return;
        sidebar.classList.add("open"); overlay.classList.add("show"); document.body.style.overflow="hidden";
    }
    function applyDesktopSidebar(collapsed){
        document.body.classList.toggle("sgm-sidebar-collapsed", collapsed);
        localStorage.setItem("pgp-sidebar-collapsed", collapsed ? "1" : "0");
        if(sidebarToggle) sidebarToggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }
    if (isDesktop()) applyDesktopSidebar(localStorage.getItem("pgp-sidebar-collapsed") === "1");
    if (sidebarToggle) sidebarToggle.addEventListener("click", function(){
        if(isDesktop()) applyDesktopSidebar(!document.body.classList.contains("sgm-sidebar-collapsed"));
        else if(sidebar && sidebar.classList.contains("open")) closeMobileSidebar(); else openMobileSidebar();
    });
    if(overlay) overlay.addEventListener("click", closeMobileSidebar);

    function applyTheme(theme){
        root.setAttribute("data-theme", theme); localStorage.setItem("sgm-theme", theme);
        if(themeToggle){ var icon=themeToggle.querySelector("i"); if(icon) icon.className=theme === "dark" ? "fa fa-sun-o" : "fa fa-moon-o"; }
    }
    var savedTheme=localStorage.getItem("sgm-theme"); if(savedTheme === "dark" || savedTheme === "light") applyTheme(savedTheme);
    if(themeToggle) themeToggle.addEventListener("click", function(){ applyTheme((root.getAttribute("data-theme") || "light") === "dark" ? "light" : "dark"); });
    window.addEventListener("resize", function(){ if(isDesktop()){ closeMobileSidebar(); applyDesktopSidebar(localStorage.getItem("pgp-sidebar-collapsed") === "1"); } });
}());
