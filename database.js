
// The DOMContentLoaded event listener and the populateTable function remain unchanged

document.addEventListener('DOMContentLoaded', function () {
    window.pywebview.api.get_database_names()
        .then(function (databaseNames) {
            var container = document.getElementById('collapsible');
            for (var i = 0; i < databaseNames.length; i++) {
                var databaseName = databaseNames[i];
                // This code has been removed, since it's now in the createCollapsible function in appfunctions.js
            }
        })
        .catch(function (error) {
            console.log('Error in get_database_names:', error);
        });
});

function populateTable(data) {
    var table = document.getElementById('myTable');

    // Remove any existing rows (except for the header)
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    // Add new rows
    for (var i = 0; i < data.length; i++) {
        var row = table.insertRow(-1); // Insert a new row at the end

        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);

        cell1.innerHTML = data[i][0]; // Shortcut
        cell2.innerHTML = data[i][1]; // Expansion
        cell3.innerHTML = data[i][2]; // Label
    }
}

  // The click event listener on the document has been removed, since it's now set up in the createCollapsible function in appfunctions.js
