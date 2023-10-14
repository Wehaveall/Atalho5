function toggleMenu(submenuId) {
    var submenu = document.getElementById(submenuId);
    var arrow = submenu.parentElement.querySelector('.arrow');
    if (submenu.classList.contains('open')) {
        submenu.classList.remove('open');
        arrow.innerHTML = '&#9654;'; // Right arrow
    } else {
        submenu.classList.add('open');
        arrow.innerHTML = '&#9660;'; // Down arrow
    }
}

function showContent(contentId) {
    const lang_general = document.querySelector('.right-column-tab4-lan-gen');
    const lang_specific = document.querySelector('.right-column-tab4-lan-spec');

    if (contentId === 'language_general') {
        lang_general.style.display = 'block';
    } else {
        lang_general.style.display = 'none';
    }

    if (contentId === 'language_advanced') {
        lang_specific.style.display = 'block';
    } else {
        lang_specific.style.display = 'none';
    }


}