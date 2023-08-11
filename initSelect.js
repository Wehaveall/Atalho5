import Select from "./select.js";

document.addEventListener("DOMContentLoaded", () => {
  const selectElements = document.querySelectorAll("[data-custom]");

  selectElements.forEach(selectElement => {
    new Select(selectElement);
  });
});
