document.addEventListener('DOMContentLoaded', function () {
  let isMouseDown = false;
  let isResizing = false;

  document.addEventListener('mousedown', function () {
    isMouseDown = true;
  });

  document.addEventListener('mouseup', function () {
    isMouseDown = false;
    if (isResizing) {
      pywebview.api.stop_resizing();
      isResizing = false;
    }
    document.body.style.cursor = 'default';
  });

  const contentWrapper = document.querySelector('#content-wrapper');
  const margin = 10; // Adjust the margin as needed

  contentWrapper.addEventListener('mousemove', function (e) {
    const rect = contentWrapper.getBoundingClientRect();
    const mouseX = e.clientX;
    const mouseY = e.clientY;

    if (
      mouseX <= rect.left + margin ||
      mouseX >= rect.right - margin ||
      mouseY <= rect.top + margin ||
      mouseY >= rect.bottom - margin
    ) {
      document.body.style.cursor = 'nwse-resize';
      if (isMouseDown && !isResizing) {
        pywebview.api.start_resizing();
        isResizing = true;
      }
    } else {
      document.body.style.cursor = 'default';
      if (isResizing) {
        pywebview.api.stop_resizing();
        isResizing = false;
      }
    }
  });
});

// Rest of your code...


/////////////////////////////////////////////////////// LEFT PANEL

document.addEventListener('DOMContentLoaded', (event) => {
  var coll = document.getElementsByClassName("collapsible");
  var i;

  for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
      this.classList.toggle("active");
      var content = this.nextElementSibling;
      var arrow = this.getElementsByClassName('arrow')[0];
      if (content.style.maxHeight) {
        content.style.maxHeight = null;
        arrow.innerHTML = " ► ";
      } else {
        content.style.maxHeight = content.scrollHeight + "px";
        arrow.innerHTML = " ▼ ";
      }
    });
  }
});
