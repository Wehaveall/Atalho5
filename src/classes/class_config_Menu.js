function toggleMenu(submenuId) {
    var submenu = document.getElementById(submenuId);
    var arrow = submenu.parentElement.querySelector('.arrow');
    if (submenu.classList.contains('open')) {
        submenu.classList.remove('open');
        arrow.innerHTML = '&#9654;'; // Right arrow
    } else {
        submenu.classList.add('open');
        arrow.innerHTML = '&#9660;'; // Down arrow
    }
}

function showContent(contentId) {
    const lang_general = document.querySelector('.right-column-tab4-lan-gen');
    const lang_specific = document.querySelector('.right-column-tab4-lan-spec');

    if (contentId === 'language_general') {
        lang_general.style.display = 'block';
    } else {
        lang_general.style.display = 'none';
    }

    if (contentId === 'language_advanced') {
        lang_specific.style.display = 'block';
    } else {
        lang_specific.style.display = 'none';
    }


    // Your existing logic for other content
}










document.addEventListener('DOMContentLoaded', () => {
    // Mock-up of the data you might receive from Python
    const suffixData = {
        "en": [
            { pattern: "([a-zA-Z])ab\\b", replacement: "\\1able", enabled: false },
        ],
        "pt-BR": [
            { pattern: "([a-zA-Z])mn\\b", replacement: "\\1mento", enabled: true },
        ],
    };

    // Function to populate suffixes for a given language
    const populateSuffixes = (language, suffixList) => {
        const languageSection = document.createElement('div');
        languageSection.className = 'language-section';

        const languageTitle = document.createElement('h3');
        languageTitle.textContent = `Language: ${language}`;

        const suffixContainer = document.createElement('div');
        suffixContainer.className = 'suffix-container';

        suffixData[language].forEach((item, index) => {
            const suffixEntry = document.createElement('div');
            suffixEntry.className = 'suffix-entry';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = item.enabled;
            checkbox.id = `${language}-checkbox-${index}`;
            checkbox.className = 'default-checkbox';  // Add this line

            const label = document.createElement('label');
            label.htmlFor = `${language}-checkbox-${index}`;
            label.textContent = `${item.pattern} = ${item.replacement}`;

            suffixEntry.appendChild(checkbox);
            suffixEntry.appendChild(label);
            suffixContainer.appendChild(suffixEntry);
        });

        languageSection.appendChild(languageTitle);  // Added this line
        languageSection.appendChild(suffixContainer);
        suffixList.appendChild(languageSection);
    };

    // Populate the suffix list dynamically
    const suffixList = document.getElementById('suffix-list');
    Object.keys(suffixData).forEach(language => {
        populateSuffixes(language, suffixList);
    });

    // Save button event
    document.getElementById('save-config').addEventListener('click', () => {
        // Collect updated data and send it to Python
        // ...
    });
});








