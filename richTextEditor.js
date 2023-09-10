
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


// Assuming the custom select is applied to the 'escolha' element
 const customSelectElement = document.querySelector('.custom-select-container');

 customSelectElement.addEventListener('valueSelected', function (event) {

    const choice = event.detail.value; // Get the selected value from the event detail

    if (isEditorUpdate || !window.currentRow) {
//         // Se a atualização do editor estiver em andamento ou nenhuma linha estiver selecionada, não faça nada
         return;
    }

    const formatValue = choice === "1";
    const shortcut = window.currentRow.dataset.shortcut;
    const groupName = window.currentRow.dataset.groupName;
    const databaseName = window.currentRow.dataset.databaseName;
    const currentContent = tinyMCE.get('editor').getContent();

     isSaving = true;  // Set the flag before saving
     window.pywebview.api.save_changes(groupName, databaseName, shortcut, currentContent, formatValue)
         .then(response => {
             // Update the dataset of the selected row directly with the choice
           window.currentRow.dataset.format = choice;
             isSaving = false;  // Reset the flag after saving is done
         })
         .catch((error) => {
             console.error('Error:', error);
             isSaving = false;  // Reset the flag in case of error
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

function getTinyMCEConfig(selector, isAdvanced, onEditorInit) {
    var basicConfig = {
        //Altura 10%% para maximizar
        height: '100%', // Defina a altura para 100%
        //Altura 100%
        icons: "thin",
        selector: selector,
        menubar: false,
        statusbar: false,
        plugins: ['paste'],
        toolbar: 'undo redo',
        paste_as_text: true,




        setup: function (editor) {
            var saveTimeout;  // Para armazenar o temporizador

            editor.on('keyup', function () {
                if (saveTimeout) {
                    clearTimeout(saveTimeout);  // Limpar o temporizador anterior
                }

                saveTimeout = setTimeout(function () {
                    if (!isEditorUpdate && window.currentRow) {
                        // Conteúdo mudou, salvar as alterações
                        var shortcut = window.currentRow.dataset.shortcut;
                        var groupName = window.currentRow.dataset.groupName;
                        var tableName = window.currentRow.dataset.tableName;
                        var databaseName = window.currentRow.dataset.databaseName;
                        var label = window.currentRow.dataset.label
                        var formatValue = document.getElementById('escolha').value === "1";
                        var caseChoice = document.getElementById('caseChoice').value;

                        isSaving = true;  // Set the flag before saving
                        window.pywebview.api.save_changes(groupName, databaseName, tableName, shortcut, editor.getContent(), formatValue, label, caseChoice)
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
                }, 1000);  // Aguardar 1 segundo antes de salvar
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
