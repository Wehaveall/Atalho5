

var buttonStates = {};
var allDbFiles = {};

// Wait until the document is fully loaded
document.addEventListener('DOMContentLoaded', function () {
  // Ensure pywebview API is ready
  window.addEventListener('pywebviewready', function () {
    if (!window.pywebview || !window.pywebview.api) {
      console.error('pywebview API is not available');
      return;
    }

    // Load all states once at the start of the program
    window.pywebview.api.load_all_states().then(function (states) {
      console.log('load_all_states called');
      buttonStates = states;

      // Get all directories and database files
      window.pywebview.api.get_all_db_files().then(function (allDbFiles) {
        console.log('get_all_db_files called');
        // Now that the states have been loaded, create the collapsibles
        for (let directory in allDbFiles) {
          var db_files = allDbFiles[directory];
          createCollapsible(directory, db_files);
        }
      });
    });
  });

  // ... Rest of your code ...
});








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


window.onload = function () {
  // Load all states once at the start of the program
  window.pywebview.api.load_all_states()
    .then(states => {
      buttonStates = states;
      // Now that the states have been loaded, create the collapsibles
      for (let directory in allDbFiles) {
        createCollapsible(directory, allDbFiles[directory]);
      }
    });
};

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




function createCollapsible(directory, db_files) {
  console.log('createCollapsible called for directory:', directory);
  var leftPanel = document.getElementById('leftPanel');

  // Check if the button and the content div already exist
  var collapsibleButton = document.getElementById(directory);
  var contentDiv = document.getElementById(directory + '-content');

  // If the button doesn't exist, create it
  if (!collapsibleButton) {
    collapsibleButton = document.createElement('button');
    collapsibleButton.id = directory;
    collapsibleButton.className = 'collapsible';

    // Set the color of the collapsible button text to dark gray
    collapsibleButton.style.color = "#333";

    // Set the background color of the button to light gray
    collapsibleButton.style.backgroundColor = "#ccc";

    // Add an event listener to the button
    collapsibleButton.addEventListener('click', function () {
      this.classList.toggle('active');
      if (contentDiv.style.display === "block") {
        contentDiv.style.display = "none";
        buttonStates[directory] = 'none';
        this.innerHTML = "▶ " + directory;
      } else {
        contentDiv.style.display = "block";
        buttonStates[directory] = 'block';
        this.innerHTML = "▼ " + directory;
      }
      window.pywebview.api.save_all_states(buttonStates);  // Save the states whenever a button is clicked
    });

    // Append the button to the left panel
    leftPanel.appendChild(collapsibleButton);
  }

  // If the content div doesn't exist, create it
  if (!contentDiv) {
    contentDiv = document.createElement('div');
    contentDiv.id = directory + '-content';
    contentDiv.className = 'content';

    // Add CSS rules to ensure the div behaves as a block-level element
    contentDiv.style.display = "none";
    contentDiv.style.width = "100%";

    // Append the content div to the left panel
    leftPanel.appendChild(contentDiv);
  }

  // Get the state of the button from the buttonStates global variable and set the initial arrow direction
  var state = buttonStates[directory] || 'none';
  if (state === 'block') {
    collapsibleButton.innerHTML = "▼ " + directory;
    contentDiv.style.display = "block";
  } else {
    collapsibleButton.innerHTML = "▶ " + directory;
  }

  // Clear the content div before appending new database file names
  contentDiv.innerHTML = '';

  db_files.forEach(function (databaseFile) {
    var db_file_elem = document.createElement('p');
    var filenameWithoutExtension = databaseFile.replace('.db', '');
    db_file_elem.textContent = filenameWithoutExtension;

    // Add left padding to align with the title
    db_file_elem.style.paddingLeft = "30px";

    db_file_elem.addEventListener('click', function () {
      window.pywebview.api.get_tables(directory, databaseFile)
        .then(function (tableNames) {
          tableNames.forEach(function (tableName) {
            window.pywebview.api.get_data(directory, databaseFile, tableName)
              .then(data => populateTable(data))
              .catch(error => console.error('Error:', error));
          });
        })
        .catch(function (error) {
          console.log('Error in get_tables:', error);
        });
    });

    // Append the p element to the content div
    contentDiv.appendChild(db_file_elem);
  });
}








//----------------------------------------------------------------POPULATE DATA----------------------------------------------------------------



function populateTable(data) {
  console.log("populateTable called with data:", data);
  var table = document.getElementById('myTable');

  // Remove any existing rows (except for the header)
  while (table.rows.length > 1) {
    table.deleteRow(1);
  }

  // Add new rows
  for (var i = 0; i < data.length; i++) {
    var row = table.insertRow(-1); // Insert a new row at the end

    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);

    cell1.innerHTML = data[i]['shortcut']; // Shortcut
    cell2.innerHTML = data[i]['expansion']; // Expansion
    cell3.innerHTML = data[i]['label']; // Label
  }
}









window.onbeforeunload = function () {
  // Save all states before the window closes
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.save_all_states(buttonStates);
  }
  // Signal to Python that the window is closing
};