window.addEventListener('load', function () {
    // Initialize the editor based on the current dropdown value
    initializeTinyMCE();


});
















//----------------------------------------------------------------------------------------------------------
function initializeTinyMCE() {
    var choice = document.getElementById('escolha').value;
    destroyTinyMCE();

    if (choice === "0") {
        initBasicTinyMCE();
    } else if (choice === "1") {
        initAdvancedTinyMCE();
    }
}




function initBasicTinyMCE() {
    if (window.tinymce) {
        tinymce.init({
            selector: '#editor',
            menubar: false,
            statusbar: false,
            plugins: ['paste'],  // Ensure the paste plugin is included
            toolbar: 'undo redo',
            paste_as_text: true,  // Force pasted content to be plain text
            // ... other configurations
            setup: function (editor) {
                window.newContent = '';
                window.currentRow = null;
                window.contentChanged = false;
                var editedRow = null;  // Newly added variable

                editor.on('keyup change', function () {
                    window.newContent = editor.getContent();
                    window.contentChanged = true;
                    editedRow = window.currentRow;  // Set the editedRow to the currentRow
                });

                setInterval(function () {
                    // Updated condition to check if the editedRow matches the currentRow
                    if (!window.contentChanged || !window.currentRow || editedRow !== window.currentRow) {
                        return;
                    }

                    var shortcut = window.currentRow.dataset.shortcut;
                    var tableName = window.currentRow.dataset.tableName;
                    var groupName = window.currentRow.dataset.groupName;
                    var db_name = window.currentRow.dataset.databaseName;


                    window.pywebview.api.save_changes(groupName, db_name, tableName, shortcut, window.newContent).then(response => {
                        console.log("Changes saved successfully");
                        window.currentRow.dataset.expansion = window.newContent;

                        var plainText = decodeHtml(window.newContent.replace(/<[^>]*>/g, ''));
                        if (window.newContent.includes('<img')) {
                            if (!plainText.includes('(imagem)')) {
                                plainText += ' (imagem)';
                            }
                        } else {
                            plainText = plainText.replace(' (imagem)', '');
                        }

                        window.currentRow.cells[0].firstChild.textContent = plainText;
                        window.contentChanged = false;
                    }).catch((error) => {
                        console.error('Error:', error);
                    });
                }, 1000);
            }
        });

        document.querySelector('#myTable').addEventListener('click', function (e) {
            var row = e.target.closest('tr');
            if (row) {
                window.currentRow = row;
            }
        });
    } else {

    }
}






function initAdvancedTinyMCE() {
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
                var editedRow = null;  // Newly added variable

                editor.on('keyup change', function () {
                    window.newContent = editor.getContent();
                    window.contentChanged = true;
                    editedRow = window.currentRow;  // Set the editedRow to the currentRow
                });

                setInterval(function () {
                    // Updated condition to check if the editedRow matches the currentRow
                    if (!window.contentChanged || !window.currentRow || editedRow !== window.currentRow) {
                        return;
                    }

                    var shortcut = window.currentRow.dataset.shortcut;
                    var tableName = window.currentRow.dataset.tableName;
                    var groupName = window.currentRow.dataset.groupName;
                    var db_name = window.currentRow.dataset.databaseName;



                    window.pywebview.api.save_changes(groupName, db_name, tableName, shortcut, window.newContent).then(response => {
                        console.log("Changes saved successfully");
                        window.currentRow.dataset.expansion = window.newContent;

                        var plainText = decodeHtml(window.newContent.replace(/<[^>]*>/g, ''));
                        if (window.newContent.includes('<img')) {
                            if (!plainText.includes('(imagem)')) {
                                plainText += ' (imagem)';
                            }
                        } else {
                            plainText = plainText.replace(' (imagem)', '');
                        }

                        window.currentRow.cells[0].firstChild.textContent = plainText;
                        window.contentChanged = false;
                    }).catch((error) => {
                        console.error('Error:', error);
                    });
                }, 1000);
            }
        });

        document.querySelector('#myTable').addEventListener('click', function (e) {
            var row = e.target.closest('tr');
            if (row) {
                window.currentRow = row;
            }
        });
    } else {

    }
}



function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}





function destroyTinyMCE() {
    if (tinymce.get('editor')) {
        tinymce.get('editor').remove();
    }
}

