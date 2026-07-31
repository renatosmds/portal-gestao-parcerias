(function () {
    "use strict";

    var search = document.getElementById("employeeSearch");
    var rows = Array.prototype.slice.call(
        document.querySelectorAll("[data-employee-row]")
    );
    var noResult = document.getElementById("employeesNoResult");
    var employeeCount = document.getElementById("employeeCount");
    var activeCount = document.getElementById("activeEmployeeCount");
    var vacationCount = document.getElementById("vacationEmployeeCount");

    function updateSummary(visibleRows) {
        var active = visibleRows.filter(function (row) {
            return row.getAttribute("data-active") === "true";
        }).length;

        var vacation = visibleRows.filter(function (row) {
            return row.getAttribute("data-vacation") === "true";
        }).length;

        if (employeeCount) employeeCount.textContent = visibleRows.length;
        if (activeCount) activeCount.textContent = active;
        if (vacationCount) vacationCount.textContent = vacation;
    }

    function filterRows() {
        var term = search ? search.value.trim().toLowerCase() : "";
        var visibleRows = [];

        rows.forEach(function (row) {
            var text = row.textContent.toLowerCase();
            var visible = !term || text.indexOf(term) !== -1;
            row.classList.toggle("d-none", !visible);

            if (visible) visibleRows.push(row);
        });

        if (noResult) {
            noResult.classList.toggle("d-none", visibleRows.length !== 0 || rows.length === 0);
        }

        updateSummary(visibleRows);
    }

    if (search) {
        search.addEventListener("input", filterRows);
    }

    updateSummary(rows);
}());
