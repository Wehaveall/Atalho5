
// The DOMContentLoaded event listener and the populateTable function remain unchanged

window.addEventListener('load', function () {
    // First part of the script
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


    // Second part of the script
    var table = document.getElementById("myTable");
    for (var i = 0; i < table.rows.length; i++) {
        table.rows[i].onclick = function () {
            var selected = document.getElementsByClassName("selected");
            if (selected[0]) selected[0].className = '';
            this.className = 'selected';

            // Get the full expansion and shortcut from the row's data attributes
            var expansion = this.dataset.expansion;
            var shortcut = this.dataset.shortcut;

            // Load the full expansion into the TinyMCE editor
            tinymce.get('editor').setContent(expansion);

            // Load the shortcut into the shortcut input field
            document.querySelector('input[placeholder="Atalho:"]').value = shortcut;
        };
    }
});

//Aqui também era windows.onload - ok







