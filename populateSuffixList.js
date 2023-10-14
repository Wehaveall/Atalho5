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
                    const pattern = item.pattern.match(/\)([a-zA-Z]+)\\b/)?.[1] || '';
                    const replaceText = item.replace.match(/[a-zA-Z]+/)?.[0] || '';

                    // Set the text to only show the specific parts of pattern and replace
                    newDiv.textContent = `Digite "${pattern}" para o sufixo "${replaceText}"`;

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
