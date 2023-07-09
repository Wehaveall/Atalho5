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

    // Calculate distances to all four borders
    const distTop = Math.abs(mouseY - rect.top);
    const distBottom = Math.abs(mouseY - rect.bottom);
    const distLeft = Math.abs(mouseX - rect.left);
    const distRight = Math.abs(mouseX - rect.right);

    // Determine the smallest distance
    const minDist = Math.min(distTop, distBottom, distLeft, distRight);

    if (minDist <= margin) {
      if (minDist === distLeft || minDist === distRight) {
        // Closer to left or right border
        document.body.style.cursor = 'w-resize';
      } else {
        // Closer to top or bottom border
        document.body.style.cursor = 'n-resize';
      }
      if (isMouseDown && !isResizing) {
        pywebview.api.start_resizing();
        isResizing = true;
      }
    } else {
      document.body.style.cursor = 'default';
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
