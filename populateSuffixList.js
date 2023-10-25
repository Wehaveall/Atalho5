function populateSuffixList() {
    fetch('suffix.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const suffixListDiv = document.getElementById('suffix-list');

            for (const lang in data) {
                const langDiv = document.createElement('div');

                // Add vertical space before each language section
                langDiv.style.marginTop = '20px';

                // Add left margin for each language title
                langDiv.style.marginLeft = '15px';  // New line to add left margin

                // Translate language codes to full names and remove bold
                let displayName;
                switch (lang) {
                    case 'pt-BR': displayName = 'Português - Brasil'; break;
                    case 'en': displayName = 'Inglês'; break;
                    case 'de': displayName = 'Alemão'; break;
                    case 'it': displayName = 'Italiano'; break;
                    case 'fr': displayName = 'Francês'; break;
                    case 'es': displayName = 'Espanhol'; break;
                    default: displayName = lang;
                }
                langDiv.innerHTML = `<span>Idioma: ${displayName}</span>`;
                suffixListDiv.appendChild(langDiv);

                data[lang].forEach((item, index) => {
                    const newDiv = document.createElement('div');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `${lang}-checkbox-${index}`;
                    checkbox.checked = item.replace.endsWith('enabled');

                    const patternStart = item.pattern.startsWith("^") ? item.pattern.slice(1, item.pattern.indexOf("\\b")).replace(/[()]/g, '') : item.pattern.match(/\)([a-zA-Zç]+)\\b/)?.[1] || '';
                    const replaceText = item.replace.match(/[a-zA-Zà-úç]+/)?.[0] || '';
                    let replacementType = item.pattern.startsWith("^") ? 'acento' : 'sufixo';

                    if (patternStart === 'aa') {
                        replacementType += ' crase';
                    }

                    newDiv.textContent = `Digite "${patternStart}" para o ${replacementType} "${replaceText}"`;

                    checkbox.addEventListener('change', function () {
                        pywebview.api.update_suffix_json_api(lang, item.pattern, this.checked);
                    });

                    const wrapperDiv = document.createElement('div');
                    wrapperDiv.style.display = 'flex';
                    wrapperDiv.style.alignItems = 'center';

                    // Add left margin for each language item
                    wrapperDiv.style.marginLeft = '15px';

                    wrapperDiv.appendChild(checkbox);
                    wrapperDiv.appendChild(newDiv);
                    langDiv.appendChild(wrapperDiv);
                });
            }
        })
        .catch(error => {
            alert('Error fetching JSON:', error);
        });
}
