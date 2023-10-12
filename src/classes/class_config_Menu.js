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
    const rightColumn = document.querySelector('.right-column-tab4');

    if (contentId === 'language_general') {
        rightColumn.style.display = 'block';
    } else {
        rightColumn.style.display = 'none';
    }

    // Your existing logic for other content
}
