function initTinyMCE() {
    // Check if tinymce is loaded
    if (window.tinymce) {
        tinymce.init({
            selector: '#editor',
            height: '100%',
            plugins: ['code'],
            statusbar: false,
            forced_root_block: false,
            menubar: false,
            toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
            toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
            setup: function (editor) {
                window.newContent = '';
                window.currentRow = null;
                window.contentChanged = false;

                editor.on('keyup', function () {
                    window.newContent = editor.getContent();
                    window.contentChanged = true;
                });

                // Set an interval to save changes every 1 second
                setInterval(function () {
                    // If the content hasn't changed, do nothing
                    if (!window.contentChanged) {
                        return;
                    }

                    // If there is no current row, do nothing
                    if (!window.currentRow) {
                        console.log('No row selected');
                        return;
                    }

                    // Get the full "shortcut" text from the data attributes
                    var shortcut = window.currentRow.dataset.shortcut;

                    // Get the "tableName", "groupName", and "db_name" from the data attributes
                    var tableName = "Articles";
                    var groupName = "Direito";
                    var db_name = "legal";

                    // Call your save_changes function here
                    window.pywebview.api.save_changes(groupName, db_name, tableName, shortcut, window.newContent).then(response => {
                        console.log("Changes saved successfully");

                        // Update the data attributes of the row
                        window.currentRow.dataset.expansion = window.newContent;

                        // Convert the HTML content to plain text
                        var plainText = decodeHtml(window.newContent.replace(/<[^>]*>/g, ''));

                        // Update the text in the table cell
                        window.currentRow.cells[0].firstChild.textContent = plainText;

                        // Reset the "contentChanged" flag
                        window.contentChanged = false;
                    }).catch((error) => {
                        console.error('Error:', error);
                    });
                }, 1000); // 1000 milliseconds = 1 second
            }
        });

        // When a row is selected, set window.currentRow to the selected row
        document.querySelector('#myTable').addEventListener('click', function (e) {
            var row = e.target.closest('tr');
            if (row) {
                window.currentRow = row;
            }
        });
    } else {
        // If tinymce is not loaded yet, retry after 100ms
        setTimeout(initTinyMCE, 100);
    }
}

// Call initTinyMCE when the page loads
window.addEventListener('load', function () {
    initTinyMCE();
});





function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}


