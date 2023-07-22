tinymce.init({
    selector: '#rightPanel',  // select the right panel for the editor
    plugins: [
        'advlist autolink link image lists charmap print preview hr anchor pagebreak',
        'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
        'save table contextmenu directionality emoticons template paste textcolor'
    ],
    toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | print preview media fullpage | forecolor backcolor emoticons',
    menu: {
        file: { title: 'File', items: 'newdocument' },
        edit: { title: 'Edit', items: 'undo redo | cut copy paste pastetext | selectall' },
        insert: { title: 'Insert', items: 'link media | template hr' },
        view: { title: 'View', items: 'visualaid' },
        format: { title: 'Format', items: 'bold italic underline strikethrough superscript subscript | formats | removeformat' },
        table: { title: 'Table', items: 'inserttable' },
        tools: { title: 'Tools', items: 'spellchecker code' }
    },
    content_css: 'tinymce/skins/content/default/content.min.css' // include CSS file for content
});
