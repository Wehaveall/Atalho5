//richTextEditor.js
var dropdownChanged = false;

window.addEventListener('load', function () {
    // Initialize editor and other load events
    initializeEditorBasedOnDropdown();

    // Call the function to conditionally show the dropdown option
    //showDropdownOptionIfTableIsNot('aTable');
});


//////////////////////////////////////////////////////////////////////////////////////////////////////////////



///////////////////////////////////////////////////////////////////////////////////////////








//Editor oculto para as formatações
tinymce.init({
    selector: '#hiddenEditor',
    height: '100%',
    plugins:
        "a11ychecker advcode advlist advtable anchor autocorrect autosave editimage image link linkchecker lists media mediaembed pageembed powerpaste searchreplace table template tinymcespellchecker typography visualblocks wordcount",
    toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
    toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
    paste_as_text: false,
    // suas outras configurações aqui, idênticas à instância visível
});


/// Event listener for custom select change - Format Value - ID: "escolha"
    const customSelectElement = document.querySelector('.custom-select-container');
    

customSelectElement.addEventListener('valueSelected', function (event) {
 
    const choice = event.detail.value;

    if (isEditorUpdate || !window.currentRow) {
        return;
    }

   
    // Gathering data from the currentRow (unchanged from your original code)
    const groupName = window.currentRow.dataset.groupName;
    const databaseName = window.currentRow.dataset.databaseName;
    const tableName = window.currentRow.dataset.tableName;
    const indexValue = window.currentRow.dataset.indexValue;
    const shortcut = window.currentRow.dataset.shortcut;
    // ver newcontent
    // Convert the 'choice' directly to a boolean for formatValue
    const formatValue = choice === "1";
   

    const label = window.currentRow.dataset.label;
    const caseChoice = document.getElementById('caseChoice').value;
    const currentContent = tinyMCE.get('editor').getContent();

    isSaving = true;

   
    
    // Save changes via API call (unchanged from your original code)
    window.pywebview.api.save_changes(groupName, databaseName, tableName, indexValue, shortcut, currentContent, formatValue, label, caseChoice)
        .then(response => {
            // Directly update the format in the dataset
            window.currentRow.dataset.format = formatValue ? "1" : "0";
            isSaving = false;
        })
        .catch((error) => {
            console.error('Error:', error);
            isSaving = false;
        });

    reinitializeEditor(choice);
});

 
function reinitializeEditor(choice) {
    const visibleEditor = (document.getElementById('editor').style.display === 'none') ? '#editor-buffer' : '#editor';
    const hiddenEditor = (visibleEditor === '#editor') ? '#editor-buffer' : '#editor';
    const currentContent = tinymce.get(visibleEditor.substring(1)).getContent();
    tinymce.get(hiddenEditor.substring(1)).remove();

    function onEditorInit() {
        tinymce.get(hiddenEditor.substring(1)).setContent(currentContent);
        swapEditors(); // Swap the editors
    }

    initializeEditor(hiddenEditor, choice === "1", onEditorInit);
}


var saveTimeout = null;
var rowSelected = false;  // Flag para determinar se uma linha foi selecionada

var isSaving = false;  // Flag para verificar se uma operação de salvamento está em andamento

function getTinyMCEConfig(selector, isAdvanced) {
    var basicConfig = {
        height: '100%',
        icons: "thin",
        selector: selector,
        menubar: false,
        statusbar: false,
        plugins: ['paste'],
        toolbar: 'undo redo',
        paste_as_text: true,
        //-- On Change
        setup: function (editor) {
            editor.on('change', function () {
                // Save when the editor content changes
                if (!isEditorUpdate && window.currentRow) {
                    var shortcut = window.currentRow.dataset.shortcut;
                    var indexValue = window.currentRow.dataset.indexValue;
                    var groupName = window.currentRow.dataset.groupName;
                    var databaseName = window.currentRow.dataset.databaseName;
                    var tableName = window.currentRow.dataset.tableName;
                    var label = window.currentRow.dataset.label;
                    var formatValue = document.getElementById('escolha').value === "1";
                    var caseChoice = document.getElementById('caseChoice').value;

                    isSaving = true;
                    window.pywebview.api.save_changes(groupName, databaseName, tableName, indexValue, shortcut, editor.getContent(), formatValue, label, caseChoice)
                        .then(response => {
                            isSaving = false;
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                            isSaving = false;
                        });
                }
            });

            var saveTimeout;
            //-- On Key Up
            editor.on('keyup', function () {
                if (saveTimeout) {
                    clearTimeout(saveTimeout);
                }

                saveTimeout = setTimeout(function () {
                    if (!isEditorUpdate && window.currentRow) {
                        // Conteúdo mudou, salvar as alterações
                        var shortcut = window.currentRow.dataset.shortcut;
                        var indexValue = window.currentRow.dataset.indexValue;  // Added
                        var groupName = window.currentRow.dataset.groupName;
                        var databaseName = window.currentRow.dataset.databaseName;
                        var tableName = window.currentRow.dataset.tableName;  // Added
                        var label = window.currentRow.dataset.label;  // Added
                        var formatValue = document.getElementById('escolha').value === "1";
                        var caseChoice = document.getElementById('caseChoice').value;  // Added


                        isSaving = true;  // Set the flag before saving
                        // Updated the function call to match your Python function's updated signature
                        window.pywebview.api.save_changes(groupName, databaseName, tableName, indexValue, shortcut, editor.getContent(), formatValue, label, caseChoice)
                            .then(response => {
                                // Atualizar o dataset e o conteúdo visual da currentRow
                                var expansionCell = window.currentRow.cells[0].querySelector('.truncate');
                                if (expansionCell) {
                                    expansionCell.dataset.expansion = editor.getContent();
                                    expansionCell.textContent = decodeHtml(editor.getContent().replace(/<[^>]*>/g, ''));
                                }
                                isSaving = false;  // Reset the flag after saving is done
                            })
                            .catch((error) => {
                                console.error('Error:', error);
                                isSaving = false;  // Reset the flag in case of error
                            });
                    }
                }, 1000);
            });
        }
    };


         
    if (isAdvanced) {
        return Object.assign(basicConfig, {
            height: '100%',
            plugins:
            "a11ychecker advcode advlist advtable anchor autocorrect autosave editimage image link linkchecker lists media mediaembed pageembed powerpaste searchreplace table template tinymcespellchecker typography visualblocks wordcount",
            toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
            toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
            paste_as_text: false,
            
        });
    }

    return basicConfig;
}



function getBasicTinyMCEConfig() {
    return getTinyMCEConfig(false);
}

function getAdvancedTinyMCEConfig() {
    return getTinyMCEConfig(true);
}


function initializeEditor(selector, isAdvanced) {
    tinymce.init(getTinyMCEConfig(selector, isAdvanced));
}

function initializeEditorBasedOnDropdown() {
    var choice = document.getElementById('escolha').value;
    var isFormatted = choice === "1";

    // Initialize the main editor
    initializeEditor('#editor', isFormatted);

    // Initialize the buffer editor
    initializeEditor('#editor-buffer', isFormatted);

    // If the choice is for plain text, remove formatting
    if (!isFormatted) {
        var editor = tinyMCE.get('editor');
        if (editor) {
            var plainTextContent = editor.getContent({ format: 'text' });
            editor.setContent(plainTextContent); // Set plain text content
        }
    }
}



function swapEditors() {
    const editor1 = document.getElementById('editor');
    const editor2 = document.getElementById('editor-buffer');
    editor1.style.display = (editor1.style.display === 'none') ? '' : 'none';
    editor2.style.display = (editor2.style.display === 'none') ? '' : 'none';
}

function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}
