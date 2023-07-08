document.addEventListener('DOMContentLoaded', function () {
  let isMouseDown = false;
  let isResizing = false;

  // Function to check if the target element is a table row
  function isTableRow(element) {
    return element && element.nodeName === 'TR';
  }

  // Add click event listener to the table to handle row selection
  var table = document.getElementById('myTable');
  table.onclick = function (event) {
    var target = event.target;
    while (target && !isTableRow(target)) {
      target = target.parentNode;
    }
    if (!target) { return; }

    var selected = table.querySelector('.selected');
    if (selected) {
      selected.classList.remove('selected');
    }

    target.classList.add('selected');
  };

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

  const borders = document.querySelectorAll('.border');
  borders.forEach(border => {
    border.addEventListener('mousemove', function (e) {
      if (isMouseDown) {
        const rect = border.getBoundingClientRect();
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        const margin = 5; // Adjust the margin as needed

        if (
          mouseX <= rect.left + margin ||
          mouseX >= rect.right - margin ||
          mouseY <= rect.top + margin ||
          mouseY >= rect.bottom - margin
        ) {
          document.body.style.cursor = 'nwse-resize';
          if (!isResizing) {
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
      }
    });
  });
});



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

