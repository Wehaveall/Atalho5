
var activeCollapsibleButton = null;  /// For the rounded border
var buttonStates = {};
var allDbFiles = {};
const cache = new Map();


//Funções

function getCachedData(directory, databaseFile, tableName) {
  let key = directory + '|' + databaseFile + '|' + tableName;
  return cache.get(key);
}

function setCachedData(directory, databaseFile, tableName, data) {
  let key = directory + '|' + databaseFile + '|' + tableName;
  cache.set(key, data);
}

function decodeHtml(html) {
  var txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}


function formatArticle(article) {
  return article.replace(/[\*\#%@\$]/g, "<br/>");
}




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

                    //Where I call PopulateTable
                    populateTable(data, groupName, databaseName, tableName);
                  }

                  else {
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




//----------------------------------------------------------------POPULATE TABLE----------------------------------------------------------------


// Aqui tive que adicionar a função os parametros groupName, databaseName e tableName
//pois, a função da API save_changes chama a função get_database_path que requer estes parâmetros:

//I need groupName and databaseName because, inside my save_changes function, im my api,  :
//def save_changes(self, groupName, databaseName, tableName, shortcut, newContent):

////Yes, we can simplify the process and find a way to ensure that groupName and databaseName are available when needed. Here's a plan of action:

//Storing groupName and databaseName in populateTable:
//Instead of extracting the values of groupName and databaseName each time inside the loop, you can pass them as arguments to the populateTable function.
// This ensures that the function always has access to the required values. 
//This is especially useful since populateTable is already being called with data specific to a particular database.

//So, modify the function definition to:
//function populateTable(data, groupName, databaseName){}}

// Por fim, dentro de createCollapsible, eu chamo a pupulateTable já modificada, com os novos parâmetros



function populateTable(data, groupName, databaseName, tableName) {
  console.log("populateTable called with data:", data);
  var table = document.getElementById('myTable');

  // Remove any existing rows (except for the header)
  while (table.rows.length > 1) {
    table.deleteRow(1);
  }

  // Add new rows
  data.forEach(item => {
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);

    var expansion = item['expansion'];
    var label = item['label'];
    var shortcut = item['shortcut'];
    var format = item['format'];

    // Convert the HTML expansion to plain text
    var plainExpansion = decodeHtml(expansion.replace(/<[^>]*>/g, ''));

    // Store full texts as data attributes
    row.dataset.expansion = expansion;
    row.dataset.shortcut = shortcut;
    row.dataset.format = format;
    row.dataset.tableName = tableName;
    row.dataset.groupName = groupName;
    row.dataset.databaseName = databaseName;

    var cell1Div = document.createElement('div');
    cell1Div.className = 'truncate';
    cell1Div.textContent = expansion === "" ? label : plainExpansion;

    cell1.appendChild(cell1Div);

    var cell2Div = document.createElement('div');
    cell2Div.className = 'truncate';
    cell2Div.style.textAlign = 'right';
    cell2Div.innerText = shortcut;

    cell2.appendChild(cell2Div);

    // Row click event
    // Row click event
    row.onclick = function () {
      if (window.currentRow) {
        window.currentRow.className = '';
      }
      this.className = 'selected';
      window.currentRow = this;

      var expansion = this.dataset.expansion;
      var format = this.dataset.format;

      var formattedExpansion = formatArticle(expansion);
      console.log('Format: ' + format);

      // Update the TinyMCE editor content to reflect the clicked row
      tinyMCE.get('editor').setContent(formattedExpansion);
      document.getElementById('shortcutInput').value = this.dataset.shortcut;

      // Update dropdown value
      var escolhaDropdown = document.getElementById('escolha');
      escolhaDropdown.value = format === 'true' ? '1' : '0';

      // Dispatch the change event using your provided instantiation style
      var event = new Event('change', {
        'bubbles': true,
        'cancelable': true
      });
      escolhaDropdown.dispatchEvent(event);
    };
  });
}




function initializePyWebView() {
  if (!window.pywebview || !window.pywebview.api) {
    console.error('pywebview API is not available');
    return;
  }

  window.pywebview.api.load_all_states()
    .then(states => {
      buttonStates = states;
      return window.pywebview.api.get_all_db_files();
    })
    .then(allDbFiles => {
      for (let directory in allDbFiles) {
        var db_files = allDbFiles[directory];
        createCollapsible(directory, db_files);
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}



//------------------------------------------------Lastly, the event handling and page initialization:



document.addEventListener('DOMContentLoaded', function () {
  window.addEventListener('pywebviewready', initializePyWebView);
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


window.onbeforeunload = function () {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.save_all_states(buttonStates);
  }
};