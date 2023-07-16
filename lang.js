// Declare your function in the global scope
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
            document.getElementById('ajuda').textContent = translations['Tab4'];
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
                // Assuming setFlags is a function to set flags according to language
                setFlags(languageCode);
            })
            .catch((error) => console.error('Error in load_language_setting:', error));



        //old wrong text

        //    One thing to note, however, is that you've got the changeLanguage
        //     function invoked after the setFlags function in the
        //      window.pywebview.api.load_language_setting() promise. 
        //      This might be an issue if setFlags is a function that should 
        //      be run after the language has been changed. 
        //      If that's the case, you might want to switch the order:

        // window.pywebview.api.load_language_setting()
        //     .then(languageCode => {
        //         // Assuming setFlags is a function to set flags according to language
        //         setFlags(languageCode);
        //         // Change the language according to the loaded setting
        //         changeLanguage(languageCode);
        //     })
        //     .catch((error) => console.error('Error in load_language_setting:', error));
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

