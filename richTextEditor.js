function initTinyMCE() {
    // Check if tinymce is loaded
    if (window.tinymce) {
        tinymce.init({
            selector: '#editor',
            height: '100%',
            plugins: ['code'],
            statusbar: false,
            forced_root_block: false,
            menubar: false,
            toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
            toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
        });
    } else {
        // If tinymce is not loaded yet, retry after 100ms
        setTimeout(initTinyMCE, 100);
    }
}

// Call initTinyMCE when the page loads
window.addEventListener('load', function () {
    initTinyMCE();
});
