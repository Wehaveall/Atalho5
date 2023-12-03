// class_Select-Change.js
// Este arquivo cuida especificamente da mudança nos dropdowns de escolha de formatação 
// e diferenciação entre maiúsculas e minúsculas.

import Select from "./class_Select.js";

window.customSelects = {};

// Initialize flag for manual change detection
let isManualChange = false;
document.addEventListener("DOMContentLoaded", () => {
  const selectElements = document.querySelectorAll("[data-custom]");

  selectElements.forEach(selectElement => {
    const customSelect = new Select(selectElement);
    window.customSelects[selectElement.id] = customSelect;

    customSelect.customElement.addEventListener('valueSelected', function (event) {
      const selectedValue = event.detail.value;

      if (isEditorUpdate || !window.currentRow) {
        return;
      }

      const shortcut = window.currentRow.dataset.shortcut;
      const groupName = window.currentRow.dataset.groupName;
      const databaseName = window.currentRow.dataset.databaseName;
      const tableName = window.currentRow.dataset.tableName;
      const indexValue = window.currentRow.dataset.indexValue;
      const label = window.currentRow.dataset.label;
      let formatValue;
      let caseChoice;

      if (selectElement.id === "escolha") {
        formatValue = selectedValue === "1";
        caseChoice = window.currentRow.dataset.caseChoice;

        var editor = tinyMCE.get('editor');
        if (formatValue === false) {
          // Display as plain text for editing
          var plainTextContent = editor.getBody().textContent || editor.getBody().innerText;
          editor.setContent(plainTextContent, { format: 'text' });
        } else {
          // Refetch and display the original formatted content
          refetchAndDisplayFormattedContent(groupName, databaseName, tableName, indexValue);
        }

        reinitializeEditor(selectedValue);
      }
      
    
      
     
      
      else if (selectElement.id === "caseChoice") {
        caseChoice = selectedValue;
        window.currentRow.dataset.caseChoice = caseChoice;
      }

      isManualChange = true;

      if (isManualChange) {
        var currentContent = editor.getContent({ format: 'html' });

        window.pywebview.api.get_data(groupName, databaseName, tableName)
          .then(data => {
            const latestDatabaseContent = data.find(row => row.id.toString() === indexValue).expansion;

            if (currentContent !== latestDatabaseContent) {
              isSaving = true;
              window.pywebview.api.save_changes(groupName, databaseName, tableName, indexValue, shortcut, currentContent, formatValue || null, label || null, caseChoice || null)
                .then(response => {
                  window.currentRow.dataset.format = formatValue ? 'true' : 'false';
                  if (caseChoice !== undefined) {
                    window.currentRow.dataset.caseChoice = caseChoice;
                  }
                })
                .catch((error) => {
                  console.error('Error:', error);
                })
                .finally(() => {
                  isSaving = false;
                  isManualChange = false;
                });
            }
          })
          .catch(error => {
            console.error("Error fetching recent data:", error);
          });
      }
    });
  });
});

function refetchAndDisplayFormattedContent(groupName, databaseName, tableName, indexValue) {
  window.pywebview.api.get_data(groupName, databaseName, tableName)
    .then(data => {
      const rowData = data.find(row => row.id.toString() === indexValue);
      if (rowData) {
        const editor = tinyMCE.get('editor');
        editor.setContent(rowData.expansion);  // Set the original formatted content
      } else {
        alert('No data found for the selected row with id: ' + indexValue);
      }
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}
