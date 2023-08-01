

window.addEventListener('load', function () {
    tinymce.init({
        selector: '#editor',
        plugins: ['code'],
        statusbar: false,
        forced_root_block: "",
        menubar: false,
        toolbar1: 'undo redo | fontfamily fontsize|bold italic underline strikethrough',
        toolbar2: 'link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
    });
});
