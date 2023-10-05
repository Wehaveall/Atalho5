function toggleDropdown(id) {
    const element = document.getElementById(id);
    if (element.classList.contains('show')) {
        element.classList.remove('show');
    } else {
        element.classList.add('show');
    }
}

function showContent(id) {
    // Hide all dropdowns
    const dropdowns = document.querySelectorAll('.dropdown-content');
    dropdowns.forEach((dropdown) => {
        dropdown.classList.remove('show');
    });

    // Show or hide the language section based on the clicked item
    const languageSection = document.getElementById('languageSection');
    if (id === 'language') {
        languageSection.style.display = 'block';
    } else {
        languageSection.style.display = 'none';
    }
}
