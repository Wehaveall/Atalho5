
var dropdownChanged = false;



window.addEventListener('load', function () {
    initializeEditorBasedOnDropdown();
    // attachTableClickHandler();
});

document.getElementById('escolha').addEventListener('change', function () {
    dropdownChanged = true;
    var choice = document.getElementById('escolha').value;
    reinitializeEditor(choice);

    // If there's no currently selected row, just return
    if (!window.currentRow) return;

    var shortcut = window.currentRow.dataset.shortcut;
    var groupName = window.currentRow.dataset.groupName;
    var databaseName = window.currentRow.dataset.databaseName;
    var formatValue = choice === "1";

    // Only save the formatValue to the database
    window.pywebview.api.save_changes(groupName, databaseName, shortcut, null, formatValue)
        .then(response => {
            console.log("Format value saved successfully.");
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});




function reinitializeEditor(choice) {
    var currentContent = tinymce.get('editor').getContent();

    // Ocultar o elemento do editor durante a transição
    document.querySelector('#editor').style.display = 'none';

    tinymce.get('editor').remove();

    function onEditorInit() {
        console.log("Editor initialized.");  // Log para verificar a inicialização

        setTimeout(function () {
            tinymce.get('editor').setContent(currentContent);
            // Exibir o editor novamente
            document.querySelector('#editor').style.display = '';
        }, 100);  // 100ms delay
    }

    if (choice === "0") {
        tinymce.init(getTinyMCEConfig(false, onEditorInit));
    } else if (choice === "1") {
        tinymce.init(getTinyMCEConfig(true, onEditorInit));
    }
}


var saveTimeout = null;
var rowSelected = false;  // Flag para determinar se uma linha foi selecionada

function getTinyMCEConfig(isAdvanced, onEditorInit) {
    var basicConfig = {
        selector: '#editor',
        menubar: false,
        statusbar: false,
        plugins: ['paste'],
        toolbar: 'undo redo',
        paste_as_text: true,
        setup: function (editor) {
            editor.on('keyup change', function () {
                clearTimeout(saveTimeout);  // Limpar o timer anterior

                saveTimeout = setTimeout(function () {
                    if (!window.currentRow) return;

                    // Se o dropdown foi alterado, não atualize o TinyMCE e redefina a flag
                    if (dropdownChanged) {
                        dropdownChanged = false;
                        return;
                    }

                    var shortcut = window.currentRow.dataset.shortcut;
                    var groupName = window.currentRow.dataset.groupName;
                    var databaseName = window.currentRow.dataset.databaseName;
                    var formatValue = document.getElementById('escolha').value === "1";
                    var editorContent = editor.getContent();

                    window.pywebview.api.save_changes(groupName, databaseName, shortcut, editorContent, formatValue)
                        .then(response => {
                            // Atualizar o dataset e o conteúdo visual da currentRow
                            if (window.currentRow) {
                                var expansionCell = window.currentRow.cells[0].querySelector('.truncate');  // Assume que a célula expansion é a primeira
                                if (expansionCell) {
                                    expansionCell.dataset.expansion = editorContent;
                                    expansionCell.textContent = decodeHtml(editorContent.replace(/<[^>]*>/g, ''));
                                }
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                }, 1200);
            });
        }
    };

    if (isAdvanced) {
        return Object.assign(basicConfig, {
            height: '100%',
            plugins: ['code'],
            toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
            toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat'
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

function initializeEditorBasedOnDropdown() {
    var choice = document.getElementById('escolha').value;
    if (choice === "0") {
        tinymce.init(getBasicTinyMCEConfig());
    } else if (choice === "1") {
        tinymce.init(getAdvancedTinyMCEConfig());
    }
}

function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}
