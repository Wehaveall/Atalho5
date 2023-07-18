
document.addEventListener('DOMContentLoaded', function () {
    window.pywebview.api.get_database_names()
        .then(function (databaseNames) {
            var container = document.getElementById('collapsible');

            for (var i = 0; i < databaseNames.length; i++) {
                var databaseName = databaseNames[i];

                var div = document.createElement('div');
                div.className = 'collapsible';
                div.setAttribute('data-database', databaseName);
                div.innerHTML = databaseName + '<span class="arrow"> ► </span>';

                var content = document.createElement('div');
                content.className = 'content';

                window.pywebview.api.get_table_names(databaseName)
                    .then(function (tableNames) {
                        for (var j = 0; j < tableNames.length; j++) {
                            (function () {  // New scope
                                var tableName = tableNames[j];

                                var p = document.createElement('p');
                                p.innerHTML = tableName;
                                p.addEventListener('click', function () {
                                    // Call the get_data function
                                    window.pywebview.api.get_data(databaseName)
                                        .then(data => populateTable(data))
                                        .catch(error => console.error('Error:', error));
                                });

                                content.appendChild(p);
                            })();  // End new scope
                        }
                    })
                    .catch(function (error) {
                        console.log('Error in get_table_names:', error);
                    });

                div.appendChild(content);

                div.addEventListener('click', function () {
                    this.classList.toggle('active');
                    var content = this.nextElementSibling;
                    var arrow = this.getElementsByClassName('arrow')[0];
                    if (content.style.maxHeight) {
                        content.style.maxHeight = null;
                        arrow.innerHTML = ' ► ';
                    } else {
                        content.style.maxHeight = content.scrollHeight + 'px';
                        arrow.innerHTML = ' ▼ ';
                    }
                });

                container.appendChild(div);
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










// document.addEventListener('click', function (event) {
//     // If the clicked element doesn't have the right selector, bail
//     if (!event.target.matches('.collapsible')) return;
//     // Don't follow the link
//     event.preventDefault();

//     // Call the get_data function
//     var databaseName = event.target.getAttribute('data-database');
//     window.pywebview.api.get_data(databaseName, tableName)
//         .then(data => populateTable(data))
//         .catch(error => console.error('Error:', error));
// }, false);
