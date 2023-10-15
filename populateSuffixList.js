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
                    const newDiv = document.createElement('div');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `${lang}-checkbox-${index}`;
                    checkbox.checked = item.replace.endsWith('enabled');  // Added line to set checked status

                    const patternStart = item.pattern.startsWith("^") ? item.pattern.slice(1, item.pattern.indexOf("\\b")).replace(/[()]/g, '') : item.pattern.match(/\)([a-zA-Zç]+)\\b/)?.[1] || '';
                    const replaceText = item.replace.match(/[a-zA-Zà-úç]+/)?.[0] || '';
                    let replacementType = item.pattern.startsWith("^") ? 'acento' : 'sufixo';

                    if (patternStart === 'aa') {
                        replacementType += ' crase';
                    }

                    newDiv.textContent = `Digite "${patternStart}" para o ${replacementType} "${replaceText}"`;

                    checkbox.addEventListener('change', function () {
                       
                        //Chama Função da API para recarregar os sufixos e acentos após cada clique no checkbox:

                        //  def update_suffix_json_api(self, lang, pattern, is_enabled):
                        //    update_suffix_json(lang, pattern, is_enabled)
                        //  # Refresh the in -memory suffix patterns(if needed)
                        //     self.suffix_patterns = load_suffix_data()
                        pywebview.api.update_suffix_json_api(lang, item.pattern, this.checked);
                        //pywebview.api.update_suffix_pattern(item.pattern, item.replace.split(",")[0], this.checked);
                    });

                    const wrapperDiv = document.createElement('div');
                    wrapperDiv.style.display = 'flex';
                    wrapperDiv.style.alignItems = 'center';

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
