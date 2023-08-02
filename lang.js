// Declare your function in the global scope

window.addEventListener('load', function () {
    // Listen for the webviewready event
    window.addEventListener('webviewready', function () {
        window.pywebview.api.load_language_setting()
            .then(languageCode => {
                // Change the language according to the loaded setting
                changeLanguage(languageCode);
            })
            .catch((error) => console.error('Error in load_language_setting:', error));
    });
});


//aqui era winonload - ok
//aqui dá erro no EDGETOOLS






function changeLanguage(languageCode) {
    console.log(`Change Language Function called. Changing language to: ${languageCode}`);
    window.pywebview.api.change_language(languageCode)
        .then(updateLanguage)
        .catch((error) => console.log('Error in change_language:', error));
}

function updateLanguage() {

    window.pywebview.api.load_translations()
        .then((translations) => {
            console.log(`Loaded translations: ${JSON.stringify(translations)}`);
            // Updating buttons with the translations
            document.getElementById('principal').textContent = translations['Tab1'];
            document.getElementById('config').textContent = translations['Tab2'];
            document.getElementById('rascunho').textContent = translations['Tab3'];
            document.getElementById('macros').textContent = translations['Tab4'];
            document.getElementById('ajuda').textContent = translations['Tab5'];
            document.getElementById('language_choice').textContent = translations['language_choice'];
        })
        .catch((error) => console.log('Error in load_translations:', error));
}

document.addEventListener('DOMContentLoaded', function () {
    window.addEventListener('pywebviewready', function () {

        window.pywebview.api.load_language_setting()
            .then(languageCode => {
                // Change the language according to the loaded setting
                changeLanguage(languageCode);
            })
            .catch((error) => console.error('Error in load_language_setting:', error));


    });

    // Event listeners for flag clicks
    ['en', 'es', 'de', 'it', 'pt-br'].forEach(languageCode => {
        const flagElement = document.getElementById(languageCode);
        if (flagElement) {
            flagElement.addEventListener('click', function () {
                changeLanguage(languageCode);
            });
        }
    });
});

