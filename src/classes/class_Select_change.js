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
   
    //listerner for the Format Value Change and Case Choice
    customSelect.customElement.addEventListener('valueSelected', function (event) {
      const selectedValue = event.detail.value;

      if (isEditorUpdate || !window.currentRow) {
        return;
      }

      const shortcut = window.currentRow.dataset.shortcut;
      const groupName = window.currentRow.dataset.groupName; 
      const tableName = window.currentRow.dataset.tableName;
      const indexValue = window.currentRow.dataset.indexValue;
      const databaseName = window.currentRow.dataset.databaseName;
      const currentContent = tinyMCE.get('editor').getContent();
      const label = window.currentRow.dataset.label;
      let formatValue = window.currentRow.dataset.format === 'true'; // Get the existing format value
      let caseChoice = window.currentRow.dataset.caseChoice; // Get the existing case choice value

      if (selectElement.id === "escolha") {
        formatValue = selectedValue === "1";
        caseChoice = window.currentRow.dataset.caseChoice; // Get the existing value
        reinitializeEditor(selectedValue);

      } else if (selectElement.id === "caseChoice") {
        caseChoice = selectedValue;
        window.currentRow.dataset.caseChoice = caseChoice; // Store the new value
        // Removed the line that incorrectly resets formatValue
        // No need to change formatValue here
      }
      

      alert("Format Value being sent: " + formatValue + ", Type: " + typeof formatValue);

      // Set the flag to true because this change was made by the user
      isManualChange = true;

      if (isManualChange) { // Only save if changed manually
        isSaving = true;
        window.pywebview.api.save_changes(groupName, databaseName, tableName, indexValue, shortcut, currentContent, formatValue || null, label || null, caseChoice || null)
          .then(response => {
            if (formatValue !== undefined) {
              window.currentRow.dataset.format = formatValue ? 'true' : 'false';
            }
            if (caseChoice !== undefined) {
              window.currentRow.dataset.caseChoice = caseChoice; // Store the updated value
            }
            isSaving = false;
      
            // Reset the flag after making the changes
            isManualChange = false;
          })
          .catch((error) => {
            isSaving = false;
          });
      }
    });
  });
});
