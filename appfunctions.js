
document.addEventListener('DOMContentLoaded', (event) => {
  var table = document.getElementById('myTable');

  table.onclick = function (event) {
    var target = event.target;
    while (target && target.nodeName !== "TR") {
      target = target.parentNode;
    }
    if (!target) { return; }

    var selected = table.querySelector('.selected');
    if (selected) {
      selected.classList.remove('selected');
    }

    target.classList.add('selected');
  }
});





function maximizeOrRestore() {

  var button = document.getElementById("maxRestore");  // get the button
  var icon = button.getElementsByTagName('img')[0];  // get the img element in the button
  // check the current icon and change it
  if (icon.src.includes("maxBtn_white")) {
    icon.src = "/src/images/restoreBtn_white.png";  // change to restore icon
  } else {
    icon.src = "/src/images/maxBtn_white.png";  // change back to maximize icon
  }
  pywebview.api.maximize_or_restore_window();  // Let Python handle the maximizing/restoring
}
