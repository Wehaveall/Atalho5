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
  var leftPanel = document.getElementById('leftPanel');

  var collapsibleButton = document.createElement('button');
  collapsibleButton.className = 'collapsible';
  collapsibleButton.innerHTML = directory;

  var contentDiv = document.createElement('div');
  contentDiv.className = 'content';

  db_files.forEach(function (databaseFile) {
    var db_file_elem = document.createElement('p');
    db_file_elem.textContent = databaseFile;
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
    contentDiv.appendChild(db_file_elem);
  });

  collapsibleButton.addEventListener('click', function () {
    this.classList.toggle('active');
    if (contentDiv.style.display === "block") {
      contentDiv.style.display = "none";
      window.pywebview.api.save_state(directory, 'none');
    } else {
      contentDiv.style.display = "block";
      window.pywebview.api.save_state(directory, 'block');
    }
  });

  leftPanel.appendChild(collapsibleButton);
  leftPanel.appendChild(contentDiv);

  window.pywebview.api.load_state(directory)
    .then(state => {
      if (state === 'block') {
        contentDiv.style.display = 'block';
        collapsibleButton.classList.add('active');
      } else {
        contentDiv.style.display = 'none';
      }
    });
}

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

