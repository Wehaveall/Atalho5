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
                editor.on('change', function () {
                    window.newContent = editor.getContent();
                });

                editor.on('blur', function () {
                    // Get the currently selected row
                    var selectedRow = document.querySelector(".selected");

                    // If there is no selected row, do nothing
                    if (!selectedRow) {
                        console.log('No row selected');
                        return;
                    }

                    // Get the full "shortcut" text from the data attributes
                    var shortcut = selectedRow.dataset.shortcut;

                    // Get the "tableName", "groupName", and "db_name" from the data attributes
                    var tableName = "Articles"
                    var groupName = "Direito"
                    var db_name = "legal"

                    // Call your save_changes function here
                    window.pywebview.api.save_changes(groupName, db_name, tableName, shortcut, window.newContent).then(response => {
                        alert("Changes saved successfully");

                        // Update the data attributes of the row
                        selectedRow.dataset.expansion = window.newContent;

                        // Convert the HTML content to plain text
                        var plainText = window.newContent.replace(/<[^>]*>/g, '');

                        // Update the text in the table cell
                        selectedRow.cells[0].firstChild.textContent = plainText;
                    })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                });
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
