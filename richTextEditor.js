window.onload = function () {
    tinymce.init({
        selector: '#editor',

        plugins: ['code'

        ],
        statusbar: false,
        menubar: false,
        toolbar1: 'undo redo | blocks fontfamily fontsize',
        toolbar2: 'bold italic underline strikethrough | link image media table mergetags code | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
        // content_css: 'tinymce/skins/content/default/content.min.css'
    });
}