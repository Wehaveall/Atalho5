
// The DOMContentLoaded event listener and the populateTable function remain unchanged

window.onload = function () {
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
}

//------------------------------- Popular dados dos bancos de dados no elemento myTable
// function populateTable(data) {
//     var table = document.getElementById('myTable');

//     // Remove any existing rows (except for the header)
//     while (table.rows.length > 1) {
//         table.deleteRow(1);
//     }

//     // Create a DocumentFragment to build with
//     var fragment = document.createDocumentFragment();

//     // Add new rows
//     data.forEach(function (item) {
//         var row = document.createElement('tr');  // create row node
//         var cell1 = document.createElement('td');  // create first cell node
//         var cell2 = document.createElement('td');  // create second cell node
//         var cell3 = document.createElement('td');  // create third cell node

//         cell1.textContent = item[0]; // Shortcut
//         cell2.textContent = item[1]; // Expansion
//         cell3.textContent = item[2]; // Label

//         row.appendChild(cell1);  // append first cell to row
//         row.appendChild(cell2);  // append second cell to row
//         row.appendChild(cell3);  // append third cell to row

//         fragment.appendChild(row);  // append row to fragment
//     });

//     table.appendChild(fragment);  // append fragment to table
// }


  // The click event listener on the document has been removed, since it's now set up in the createCollapsible function in appfunctions.js
