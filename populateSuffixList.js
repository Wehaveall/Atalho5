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
                langDiv.innerHTML = `<h4>Language: ${lang}</h4>`;
                suffixListDiv.appendChild(langDiv);

                data[lang].forEach((item, index) => {
                    // Create new divs and elements
                    const newDiv = document.createElement('div');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `${lang}-checkbox-${index}`;

                    // Correctly extract the specific parts of pattern and replace
                    const patternStart = item.pattern.startsWith("^") ? item.pattern.slice(1, item.pattern.indexOf("\\b")).replace(/[()]/g, '') : item.pattern.match(/\)([a-zA-Zç]+)\\b/)?.[1] || '';
                    const replaceText = item.replace.match(/[a-zA-Zà-úç]+/)?.[0] || '';

                    // Determine the type of replacement: 'sufixo' or 'acento'
                    let replacementType = item.pattern.startsWith("^") ? 'acento' : 'sufixo';

                    // Special case for "crase"
                    if (patternStart === 'aa') {
                        replacementType += ' crase';
                    }

                    // Set the text to show the specific parts of pattern and replace
                    newDiv.textContent = `Digite "${patternStart}" para o ${replacementType} "${replaceText}"`;



                    // Add an event listener to update the JSON file when clicked
                    checkbox.addEventListener('change', function () {
                        pywebview.api.update_suffix_json(lang, item.pattern, this.checked);
                        pywebview.api.update_suffix_pattern(item.pattern, item.replace.split(",")[0], this.checked);

                    });



                    // Create a wrapper div and use flexbox to align items horizontally
                    const wrapperDiv = document.createElement('div');
                    wrapperDiv.style.display = 'flex';
                    wrapperDiv.style.alignItems = 'center';

                    // Append the checkbox and the text div to the wrapper
                    wrapperDiv.appendChild(checkbox);
                    wrapperDiv.appendChild(newDiv);

                    // Append the wrapper div to the language div
                    langDiv.appendChild(wrapperDiv);
                });
            }
        })
        .catch(error => {
            alert('Error fetching JSON:', error);
        });
}
