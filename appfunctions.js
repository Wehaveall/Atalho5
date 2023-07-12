





// RESIZING FUNCTION


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


///////////////////////////////////////////////////////////// LEFT PANEL

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





function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}



//Stop event propagation
document.getElementById("content").addEventListener("click", function (event) {
  event.stopPropagation();
}, false);

var collapsibles = document.getElementsByClassName("content");
for (var i = 0; i < collapsibles.length; i++) {
  collapsibles[i].addEventListener("click", function (event) {
    event.stopPropagation();
  }, false);
}










//////////////////////////////////////////////////////////////////Create Collapsible




async function createCollapsible(directory, file) {
  console.log("Creating collapsible for directory: " + directory + " and file: " + file);
  var leftPanel = document.getElementById('leftPanel');

  // Create the button for the collapsible
  var collapsibleButton = document.createElement('button');
  collapsibleButton.className = 'collapsible';
  collapsibleButton.innerHTML = directory;
  leftPanel.appendChild(collapsibleButton);

  // Create the content for the collapsible
  var collapsibleContent = document.createElement('div');
  collapsibleContent.className = 'content';
  collapsibleContent.innerHTML = '<p>' + file + '</p>';
  leftPanel.appendChild(collapsibleContent);

  // Load state from Python API
  var storedState = await window.pywebview.api.loadState(directory);
  if (storedState === "block") {
    collapsibleContent.style.display = "block";
    collapsibleButton.classList.add('active');
  } else {
    collapsibleContent.style.display = "none";
  }

  // Add the click event to the collapsible button
  collapsibleButton.addEventListener('click', async function () {
    this.classList.toggle('active');
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
      await window.pywebview.api.saveState(directory, "none");
    } else {
      content.style.display = "block";
      await window.pywebview.api.saveState(directory, "block");
    }
  });
}










