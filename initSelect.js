import Select from "./select.js";

window.customSelects = {};

// Initialize flag for manual change detection
let isManualChange = false;

document.addEventListener("DOMContentLoaded", () => {
  const selectElements = document.querySelectorAll("[data-custom]");

  selectElements.forEach(selectElement => {
    const customSelect = new Select(selectElement);
    window.customSelects[selectElement.id] = customSelect;

    const customSelectContainer = customSelect.customElement; // Define customSelectContainer

    customSelectContainer.addEventListener('valueSelected', function (event) {
      const choice = event.detail.value;

      if (isEditorUpdate || !window.currentRow) {
        return;
      }

      const formatValue = choice === "1";
      const shortcut = window.currentRow.dataset.shortcut;
      const groupName = window.currentRow.dataset.groupName; 
      const tableName = window.currentRow.dataset.tableName;
      const databaseName = window.currentRow.dataset.databaseName;
      const currentContent = tinyMCE.get('editor').getContent();
      const label = window.currentRow.dataset.label

      // Set the flag to true because this change was made by the user
      isManualChange = true;

      if (isManualChange) { // Only save if changed manually
        isSaving = true;
        window.pywebview.api.save_changes(groupName, databaseName, tableName, shortcut, currentContent, formatValue, label)
          .then(response => {
            window.currentRow.dataset.format = formatValue ? 'true' : 'false';
            isSaving = false;

            // Reset the flag after making the changes
            isManualChange = false;

            // Assuming the response contains the database value:
            const dbValue = response.formatValue; // Replace with the actual value from the response
            const selectValue = dbValue ? "1" : "0";

            customSelect.selectValue(selectValue); // Update the custom select value
          })
          .catch((error) => {
            isSaving = false;
          });
      }

      reinitializeEditor(choice);
    });
  });
});
