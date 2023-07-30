
var activeCollapsibleButton = null;  /// For the rounded border

var buttonStates = {};
var allDbFiles = {};


const cache = new Map();

function getCachedData(directory, databaseFile, tableName) {
  let key = directory + '|' + databaseFile + '|' + tableName;
  return cache.get(key);
}

function setCachedData(directory, databaseFile, tableName, data) {
  let key = directory + '|' + databaseFile + '|' + tableName;
  cache.set(key, data);
}








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
  console.log("openTab called with tabName: ", tabName); // Add this line

  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block"; // change this to "flex" if you want to use Flexbox layout
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


////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
///CREATE COLLAPSIBLE

let databaseChildSelected = false;

function createCollapsible(directory, db_files) {
  console.log('createCollapsible called for directory:', directory);

  var leftPanel = document.getElementById('leftPanel');
  var docFrag = document.createDocumentFragment();


  // Create a parent div for the collapsible and its content
  var collapsibleParent = document.createElement('div');

  // Check if the button and the content div already exist

  // Check if the button and the content div already exist
  var collapsibleButton = document.getElementById(directory);
  var contentDiv = document.getElementById(directory + '-content');

  // If the button doesn't exist, create it
  if (!collapsibleButton) {
    collapsibleButton = document.createElement('button');
    collapsibleButton.id = directory;
    collapsibleButton.className = 'collapsible';

    // Create span for the arrow
    var arrowSpan = document.createElement('span');
    arrowSpan.className = 'arrow-right';
    arrowSpan.innerHTML = "▶ ";

    // Create span for the directory name
    var directorySpan = document.createElement('span');
    directorySpan.textContent = directory;

    // Append the spans to the button
    collapsibleButton.appendChild(arrowSpan);
    collapsibleButton.appendChild(directorySpan);

    collapsibleButton.style.fontFamily = "'Work Sans', sans-serif";

    // Set the color of the collapsible button text to dark gray
    collapsibleButton.style.color = "#333";

    // Set the background color of the button to light gray
    collapsibleButton.style.backgroundColor = "#f1f1f1";

    // Use Flexbox to vertically center the arrow and the directory name
    collapsibleButton.style.display = 'flex';
    collapsibleButton.style.alignItems = 'center';

    // Add a transparent border to the button
    collapsibleButton.style.border = '2px solid transparent';
    collapsibleButton.style.borderRadius = '5px';

    // Add an event listener to the button
    collapsibleButton.addEventListener('click', function () {
      // If there's an active button and it's not the current button, make its border transparent
      if (activeCollapsibleButton && activeCollapsibleButton !== this) {
        activeCollapsibleButton.style.borderColor = 'transparent';
      }

      // Toggle this button's active state
      this.classList.toggle('active');

      var arrowSpan = this.children[0];  // get the arrow span

      if (contentDiv.style.display === "block") {
        contentDiv.style.display = "none";
        buttonStates[directory] = 'none';
        arrowSpan.innerHTML = "▶ ";
        var groupManage = document.getElementById('groupManage');
        groupManage.style.display = 'none';

        // When collapsing the group, deselect any selected database
        // When collapsing the group or expanding, deselect any selected database in any group
        let allChildElements = document.getElementsByClassName('child-elem');
        for (let i = 0; i < allChildElements.length; i++) {
          allChildElements[i].classList.remove('focused');
        }
        databaseChildSelected = false;

        // Hide the table and table headers when a group is collapsed
        document.getElementById('myTable').style.display = 'none';
        document.getElementById("header").style.display = "none";

      } else {
        contentDiv.style.display = "block";
        buttonStates[directory] = 'block';
        arrowSpan.innerHTML = "▼ ";

        // When expanding the group, deselect any selected child
        let allChildElements = contentDiv.getElementsByClassName('child-elem');
        for (let i = 0; i < allChildElements.length; i++) {
          allChildElements[i].classList.remove('focused');
        }
      }

      // Change the border color to orange
      this.style.borderColor = '#f5b57f';

      // Set this button as the active button
      activeCollapsibleButton = this;

      window.pywebview.api.save_all_states(buttonStates);  // Save the states whenever a button is clicked
    });

    // Append the button to the new parent div
    collapsibleParent.appendChild(collapsibleButton);
  }

  // If the content div doesn't exist, create it
  // If the content div doesn't exist, create it
  if (!contentDiv) {
    contentDiv = document.createElement('div');
    contentDiv.id = directory + '-content';
    contentDiv.className = 'content';

    // Add CSS rules to ensure the div behaves as a block-level element
    contentDiv.style.width = "100%";

    // Set the display state of the content div based on the saved state
    if (buttonStates[directory] === 'block') {
      contentDiv.style.display = "block";
      arrowSpan.innerHTML = "▼ ";
    } else {
      contentDiv.style.display = "none";
      arrowSpan.innerHTML = "▶ ";
    }

    // Append the content div to the new parent div
    collapsibleParent.appendChild(contentDiv);
  }

  // Clear the content div before appending new database file names
  contentDiv.innerHTML = '';


  db_files.forEach(function (databaseFile) {
    var db_file_elem = document.createElement('p');
    var filenameWithoutExtension = databaseFile.replace('.db', '');
    db_file_elem.textContent = filenameWithoutExtension;

    // Add a class to child elements
    db_file_elem.className = 'child-elem';

    // Add left padding to align with the title
    db_file_elem.style.paddingLeft = "30px";
    db_file_elem.style.fontFamily = "'Work Sans', sans-serif";
    db_file_elem.style.fontSize = "14px";
    db_file_elem.style.marginTop = "10px";

    db_file_elem.addEventListener('click', function () {
      console.log("Database clicked!");
      // Remove 'focused' class from all children across all sections
      let allChildElements = document.getElementsByClassName('child-elem');
      for (let i = 0; i < allChildElements.length; i++) {
        allChildElements[i].classList.remove('focused');
      }

      // Deselect the active collapsible button
      if (activeCollapsibleButton) {
        activeCollapsibleButton.classList.remove('active');
        activeCollapsibleButton.style.borderColor = 'transparent';
        activeCollapsibleButton = null;
      }

      // Add 'focused' class to the clicked child
      this.classList.add('focused');

      databaseChildSelected = true;

      // Get reference to the header element
      var headerElem = document.getElementById('header');

      //Group Manager State
      var groupManage = document.getElementById('groupManage');
      groupManage.style.display = 'flex';

      // Get reference to the name of database
      var selectedDbNameElem = document.getElementById('selectedDbName');
      selectedDbNameElem.textContent = filenameWithoutExtension;

      // Split the full path into components to get the groupName and databaseName
      var groupName = directory;  // directory is passed into createCollapsible function
      var databaseName = databaseFile.replace('.db', '');  // remove the .db extension


      window.pywebview.api.get_tables(directory, databaseFile)
        .then(function (tableNames) {
          tableNames.forEach(function (tableName) {
            let data = getCachedData(directory, databaseFile, tableName);
            if (data) {
              if (databaseChildSelected) {
                document.getElementById('myTable').style.display = 'table';
                headerElem.style.display = 'table';
                headerElem.classList.add('showing');
                populateTable(data);
              } else {
                document.getElementById('myTable').innerHTML = "";
                document.getElementById('myTable').style.display = 'none';
                headerElem.style.display = 'none';
                headerElem.classList.remove('showing');
              }
            } else {






              window.pywebview.api.get_data(groupName, databaseName, tableName)
                .then(data => {
                  console.log(data);  // This will print the returned data to the JavaScript console
                  setCachedData(directory, databaseFile, tableName, data);
                  if (databaseChildSelected) {
                    document.getElementById('myTable').style.display = 'table';
                    headerElem.style.display = 'table';
                    headerElem.classList.add('showing');
                    populateTable(data);
                  } else {
                    document.getElementById('myTable').innerHTML = "";
                    document.getElementById('myTable').style.display = 'none';
                    headerElem.style.display = 'none';
                    headerElem.classList.remove('showing');
                  }
                })
                .catch(error => console.error('Error:', error));
            }
          });
        })
        .catch(function (error) {
          console.log('Error in get_tables:', error);
        });
    });


    // Append the p element to the content div
    //contentDiv.appendChild(db_file_elem);
    contentDiv.appendChild(db_file_elem);
  });




  // Append the main DocumentFragment to the left panel
  leftPanel.appendChild(collapsibleParent);

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

    var cell1 = row.insertCell(0); // Expansion or Label if Expansion is empty
    var cell2 = row.insertCell(1); // Shortcut

    var expansion = data[i]['expansion'];
    var label = data[i]['label'];
    var shortcut = data[i]['shortcut'];

    // Store full texts as data attributes
    row.dataset.expansion = expansion;
    row.dataset.shortcut = shortcut;

    if (expansion === "") {
      cell1.innerHTML = truncateText(label, 20);
    } else {
      cell1.innerHTML = truncateText(expansion, 20);
    }

    cell2.innerHTML = truncateText(shortcut, 20);
    cell2.style.textAlign = "right"; // aligns the content to the right










    // Add click event to the row
    // Inside your row.onclick event


    row.onclick = function () {
      var selected = document.getElementsByClassName("selected");
      if (selected[0]) selected[0].className = '';
      this.className = 'selected';

      // Get the full "expansion" and "shortcut" texts from the data attributes
      var expansion = this.dataset.expansion;
      var shortcut = this.dataset.shortcut;

      // Format the expansion
      var formattedExpansion = formatArticle(expansion);

      // Load the formatted "expansion" content into the TinyMCE editor
      tinyMCE.get('editor').setContent(formattedExpansion);

      // Load the full "shortcut" content into the input field
      document.getElementById('shortcutInput').value = shortcut;
    };
  }
}



// Adicione esta função em algum lugar do seu código JavaScript
//Inserir quebra de linha nos delimitadores
function formatArticle(article) {
  return article.replace(/\*/g, "<br/>")
    .replace(/#/g, "<br/>")
    .replace(/%/g, "<br/>")
    .replace(/@/g, "<br/>")
    .replace(/\$/g, "<br/>");
}










// Truncate text if it's longer than the specified length
function truncateText(text, maxLength) {
  return text.length > maxLength ? text.substr(0, maxLength - 1) + '...' : text;
}











window.onbeforeunload = function () {
  // Save all states before the window closes
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.save_all_states(buttonStates);
  }
  // Signal to Python that the window is closing
};