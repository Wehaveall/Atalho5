// Declare your function in the global scope
window.changeLanguage = function (languageCode) {
    console.log(`Change Language Function called. Changing language to: ${languageCode}`);
    if (window.pywebview) {
        window.pywebview.api.change_language(languageCode)
            .then(updateLanguage)
            .catch((error) => console.log('Error in change_language:', error));
    }
}

window.onload = function () {
    function updateLanguage() {
        console.log('Update Language function called.');
        if (window.pywebview) {
            window.pywebview.api.load_translations()
                .then((translations) => {
                    console.log(`Loaded translations: ${translations}`);
                    // Updating buttons with the translations
                    document.getElementById('principal').textContent = translations['Tab1'];
                    document.getElementById('config').textContent = translations['Tab2'];
                    document.getElementById('rascunho').textContent = translations['Tab3'];
                    document.getElementById('ajuda').textContent = translations['Tab4'];
                })
                .catch((error) => console.log('Error in load_translations:', error));
        }
    }

    if (window.pywebview) {
        window.pywebview.api.load_language_setting().then(languageCode => {
            // Assuming setFlags is a function to set flags according to language
            setFlags(languageCode);
            // Change the language according to the loaded setting
            window.changeLanguage(languageCode);
        });
    } else {
        console.error("pywebview object is not available.");
    }
}
