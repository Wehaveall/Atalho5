
var dropdownChanged = false;



window.addEventListener('load', function () {
    initializeEditorBasedOnDropdown();
    // attachTableClickHandler();
});

document.getElementById('escolha').addEventListener('change', function () {
    if (isEditorUpdate || !window.currentRow) {
        // Se a atualização do editor estiver em andamento ou nenhuma linha estiver selecionada, não faça nada
        return;
    }

    var choice = document.getElementById('escolha').value;
    var formatValue = choice === "1";

    var shortcut = window.currentRow.dataset.shortcut;
    var groupName = window.currentRow.dataset.groupName;
    var databaseName = window.currentRow.dataset.databaseName;
    var currentContent = tinyMCE.get('editor').getContent();

    isSaving = true;  // Set the flag before saving
    window.pywebview.api.save_changes(groupName, databaseName, shortcut, currentContent, formatValue)
        .then(response => {
            // Atualize o dataset da linha selecionada
            window.currentRow.dataset.format = formatValue ? 'true' : 'false';
            isSaving = false;  // Reset the flag after saving is done
        })
        .catch((error) => {
            console.error('Error:', error);
            isSaving = false;  // Reset the flag in case of error
        });
        reinitializeEditor(choice);
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

var isSaving = false;  // Flag para verificar se uma operação de salvamento está em andamento

function getTinyMCEConfig(isAdvanced, onEditorInit) {
    var basicConfig = {
        selector: '#editor',
        menubar: false,
        statusbar: false,
        plugins: ['paste'],
        toolbar: 'undo redo',
        paste_as_text: true,
        setup: function (editor) {
            editor.on('keyup', function () {
                if (!isEditorUpdate && window.currentRow) {
                    // Conteúdo mudou, salvar as alterações
                    var shortcut = window.currentRow.dataset.shortcut;
                    var groupName = window.currentRow.dataset.groupName;
                    var databaseName = window.currentRow.dataset.databaseName;
                    var formatValue = document.getElementById('escolha').value === "1";

                    isSaving = true;  // Set the flag before saving
                    window.pywebview.api.save_changes(groupName, databaseName, shortcut, editor.getContent(), formatValue)
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
