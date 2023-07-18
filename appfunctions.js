

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

// document.addEventListener('DOMContentLoaded', (event) => {
//   var coll = document.getElementsByClassName("collapsible");
//   var i;

//   for (i = 0; i < coll.length; i++) {
//     coll[i].addEventListener("click", function () {
//       this.classList.toggle("active");
//       var content = this.nextElementSibling;
//       var arrow = this.getElementsByClassName('arrow')[0];
//       if (content.style.maxHeight) {
//         content.style.maxHeight = null;
//         arrow.innerHTML = " ► ";
//       } else {
//         content.style.maxHeight = content.scrollHeight + "px";
//         arrow.innerHTML = " ▼ ";
//       }

//       // Get the database name from the data-database attribute
//       var databaseName = this.getAttribute('data-database');

//       // Call populateTable with the database name
//       populateTable(databaseName);
//     });
//   }
// });





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
document.addEventListener('DOMContentLoaded', (event) => {
  document.getElementById("content").addEventListener("click", function (event) {
    event.stopPropagation();
  }, false);

  var collapsibles = document.getElementsByClassName("content");
  for (var i = 0; i < collapsibles.length; i++) {
    collapsibles[i].addEventListener("click", function (event) {
      event.stopPropagation();
    }, false);
  }
});











//////////////////////////////////////////////////////////////////Create Collapsible




async function createCollapsible(directory, file) {
  console.log("Creating collapsible for directory: " + directory + " and file: " + file);
  var leftPanel = document.getElementById('leftPanel');

  // Create the button for the collapsible
  var collapsibleButton = document.createElement('button');
  collapsibleButton.className = 'collapsible';
  collapsibleButton.innerHTML = directory;

  // Add a click event listener to the button
  collapsibleButton.addEventListener('click', function () {
    // Toggle active class
    this.classList.toggle('active');
    // Expand/collapse content
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
      // Save state to Python API
      window.pywebview.api.save_state(directory, 'none');
    } else {
      content.style.display = "block";
      // Save state to Python API
      window.pywebview.api.save_state(directory, 'block');
    }
  });

  leftPanel.appendChild(collapsibleButton);

  // Create the content for the collapsible
  var collapsibleContent = document.createElement('div');
  collapsibleContent.className = 'content';

  // For each file in the directory, create a new paragraph element
  var fileElement = document.createElement('p');
  fileElement.innerHTML = file;

  // Add a click event listener to the fileElement
  fileElement.addEventListener('click', function () {
    // When the fileElement is clicked, get data from the corresponding database and populate the table
    window.pywebview.api.get_data(directory, file)
      .then(data => {
        console.log(data); // Log the data
        populateTable(data);
      })
      .catch(error => console.error('Error:', error));
  });

  // Add the fileElement to the collapsibleContent
  collapsibleContent.appendChild(fileElement);

  leftPanel.appendChild(collapsibleContent);

  // Load state from Python API
  window.pywebview.api.load_state(directory)
    .then(state => {
      if (state === 'block') {
        collapsibleContent.style.display = 'block';
        collapsibleButton.classList.add('active');
      } else {
        collapsibleContent.style.display = 'none';
      }
    });
}













