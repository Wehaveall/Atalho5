
var dropdownChanged = false;

window.addEventListener('load', function () {
    initializeEditorBasedOnDropdown();
    // attachTableClickHandler();
});


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
    var config = {
        height: '100%',
        icons: "thin",
        selector: selector,
        menubar: false,
        statusbar: false,
        plugins: ['paste'],
        toolbar: 'undo redo',
        paste_as_text: true,

        setup: function (editor) {
            if (isAdvanced) {
                editor.on('ExecCommand', function (e) {
                    if (!isEditorUpdate && window.currentRow) {
                        saveEditorContent(editor);
                    }
                });
            }

            editor.on('keyup', function () {
                if (!isEditorUpdate && window.currentRow) {
                    saveEditorContent(editor);
                }
            });
        }
    };

    if (isAdvanced) {
        Object.assign(config, {
            plugins: "a11ychecker advcode advlist advtable anchor autocorrect autosave editimage image link linkchecker lists media mediaembed pageembed powerpaste searchreplace table template tinymcespellchecker typography visualblocks wordcount",
            toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
            toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
            paste_as_text: false,
        });
    }

    return config;
}


//Save editor content into the database
function saveEditorContent(editor) {
    if (isSaving) {
        return;
    }

    const currentContent = editor.getContent();
    const groupName = window.currentRow.dataset.groupName;
    const databaseName = window.currentRow.dataset.databaseName;
    const tableName = window.currentRow.dataset.tableName;
    const indexValue = window.currentRow.dataset.indexValue;
    const shortcut = window.currentRow.dataset.shortcut;
    const label = window.currentRow.dataset.label;
    const formatValue = document.getElementById('escolha').value === "1";
    const caseChoice = document.getElementById('caseChoice').value;

    isSaving = true;

    window.pywebview.api.save_changes(groupName, databaseName, tableName, indexValue, shortcut, currentContent, formatValue, label, caseChoice)
        .then(response => {
            isSaving = false;
        })
        .catch((error) => {
            console.error('Error:', error);
            isSaving = false;
        });
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
    initializeEditor('#editor', choice === "1");
    initializeEditor('#editor-buffer', choice === "1");
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
