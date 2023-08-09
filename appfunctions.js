
var appState = {
  buttonStates: {}
};

var activeCollapsibleButton = null;
var buttonStates = appState.buttonStates;
var allDbFiles = {};



var numberOfEnters = 2; // Você pode ajustar esse valor conforme necessário
//preciso que seja global, para ajustar a quantidade de enters!!



/////////////////////////////////////////////////////////////////////CACHE////////////////////////////////

// Nesta implementação:

// O cache é armazenado em dataCache.
// Cada entrada de cache tem um timestamp indicando quando foi armazenada.
// Ao obter uma entrada do cache com getFromCache(), verificamos se o TTL expirou.
//  Se sim, excluímos a entrada e retornamos null.
// fetchData() primeiro verifica o cache. Se os dados estiverem no cache e ainda forem válidos,
//  ele retorna imediatamente. Caso contrário, busca os dados e os armazena no cache.
// Quando você atualizar os dados em algum lugar no seu aplicativo,
//  você deve chamar dataCache.delete(cacheKey) para invalidar a entrada de cache relevante.


// Dada a forma como o seu cache está estruturado e como você recupera dados do cache, 
// o que está acontecendo é que, quando você salva as alterações com save_changes,
//  está invalidando mais do que o necessário. O que você precisa fazer é simplesmente
//   invalidar a chave do cache que corresponde aos dados que foram alterados.

// Veja, a chave do cache é composta por groupName|databaseName|tableName. 
// Quando você modifica dados em uma tabela específica, você não está alterando
//  o nome do grupo, nome do banco de dados ou nome da tabela.
//   O que está mudando são os valores dentro dessa tabela. 
//   Portanto, a chave do cache não precisa incluir os valores de expansion, 
//   shortcut ou format, porque esses valores não fazem parte da chave do cache.

// A função invalidateCacheEntry que você tem agora é quase correta, 
// mas tem um pequeno erro: está referenciando cache em vez de dataCache. Vamos corrigir isso:

// javascript
// Copy code
// function invalidateCacheEntry(...args) {
//   const cacheKey = args.join('|');
//   if (dataCache.has(cacheKey)) {
//     dataCache.delete(cacheKey);
//   }
// }
// Agora, na sua função save_changes, você só precisa chamar invalidateCacheEntry
//  com os três argumentos: groupName, databaseName, e tableName.

// python
// Copy code
// self.window.evaluate_js(
//   'invalidateCacheEntry("{groupName}", "{databaseName}", "{tableName}")'.format(
//     groupName=groupName,
//     databaseName=databaseName,
//     tableName=tableName
//   )
// )
// O que isso faz é simplesmente remover a entrada do cache para essa tabela específica.
//  Da próxima vez que você tentar recuperar dados dessa tabela usando a função fetchData, 
//  o cache não terá esses dados e a função buscará no banco de dados e recolocará os dados atualizados no cache.

// Em resumo, a chave é entender que a chave do cache é baseada em identificadores 
// que descrevem "onde" os dados estão (ou seja, em qual grupo, banco de dados, tabela),
//  e não "o que" os dados são (ou seja, os valores de expansion, shortcut, etc.). 
//  Ao modificar os dados, você simplesmente invalida a entrada do cache
//   para essa localização e os dados são buscados novamente na próxima vez que você os solicitar.





const CACHE_TTL = 60000; // 60 segundos de tempo de vida
const dataCache = new Map();  //datacache é o nome da variável para o cache

// Função para obter dados do cache
function getFromCache(key) {
  const cacheEntry = dataCache.get(key);
  if (!cacheEntry) return null;
  if (Date.now() - cacheEntry.timestamp > CACHE_TTL) {
    // A entrada do cache expirou
    dataCache.delete(key);
    return null;
  }
  return cacheEntry.data;
}

// Função para definir dados no cache
function setToCache(key, data) {
  dataCache.set(key, {
    data: data,
    timestamp: Date.now()
  });
}

// Refatorado para usar o cache
function fetchData(groupName, databaseName, tableName) {
  const cacheKey = `${groupName}|${databaseName}|${tableName}`;
  const cachedData = getFromCache(cacheKey);
  if (cachedData) {
    return Promise.resolve(cachedData);
  }
  return window.pywebview.api.get_data(groupName, databaseName, tableName)
    .then(data => {
      setToCache(cacheKey, data);
      return data;
    });
}

function invalidateCacheEntry(...args) {
  const cacheKey = args.join('|');
  if (dataCache.has(cacheKey)) {
    dataCache.delete(cacheKey);
  }
}



//Funções

function decodeHtml(html) {
  var txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}


function formatArticle(article) {
  let replacement = "<br/>".repeat(numberOfEnters); // Repete a tag <br/> de acordo com o valor de numberOfEnters
  return article.replace(/[\*\#%@\$]/g, replacement);
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


      //--------------------------------------------------Aqui entra o cache----------------------------------------

      window.pywebview.api.get_tables(directory, databaseFile)
        .then(function (tableNames) {
          tableNames.forEach(function (tableName) {
            //aqui entra o cache
            fetchData(groupName, databaseName, tableName)
              .then(data => {
                console.log(data);
                if (databaseChildSelected) {
                  document.getElementById('myTable').style.display = 'table';
                  headerElem.style.display = 'table';
                  headerElem.classList.add('showing');
                  populateTable(data, groupName, databaseName, tableName);
                } else {
                  document.getElementById('myTable').innerHTML = "";
                  document.getElementById('myTable').style.display = 'none';
                  headerElem.style.display = 'none';
                  headerElem.classList.remove('showing');
                }
              })
              .catch(error => console.error('Error:', error));
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

  // Reference to the table
  var table = document.getElementById('myTable');

  // Clear existing rows (except for the header)
  while (table.rows.length > 1) {
    table.deleteRow(1);
  }

  // Iterate over data and add new rows
  data.forEach(item => {
    // Extract the values from the item
    const { expansion, label, shortcut, format } = item;

    // Create a new row and cells
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);

    // Convert the HTML expansion to plain text
    var plainExpansion = decodeHtml(expansion.replace(/<[^>]*>/g, ''));

    // Store the values as data attributes for the row
    Object.assign(row.dataset, {
      expansion,
      shortcut,
      format,
      tableName,
      groupName,
      databaseName
    });

    // Populate the cells with content
    cell1.appendChild(createCellContent('truncate', expansion === "" ? label : plainExpansion));
    cell2.appendChild(createCellContent('truncate', shortcut, 'right'));

    // Add the row click event
    row.addEventListener('click', handleRowClick);
  });
}

// Helper function to create cell content
function createCellContent(className, textContent, textAlign = 'left') {
  var div = document.createElement('div');
  div.className = className;
  div.textContent = textContent;
  div.style.textAlign = textAlign;
  return div;
}

// Row click handler
// Row click handler
var rowSelected = false;  // Adicione esta variável de flag fora de qualquer função, no escopo global
var isRowClick = false;  // Adicionado no início do seu script
var preventSave = false;
var isEditorUpdate = false;
var isSaving = false;

function handleRowClick() {
  // Se uma operação de salvamento estiver em andamento, retorne imediatamente
  if (isSaving) return;

  // Deselect the previously selected row, if any
  if (window.currentRow && window.currentRow !== this) {
    window.currentRow.className = '';  // Deselect the previous row
  }

  // Highlight the current row
  this.className = 'selected';
  window.currentRow = this;

  // Extract the relevant data from the clicked row
  const { groupName, databaseName, tableName, shortcut, format } = this.dataset;

  // Fetch the most recent data from the cache or database
  window.pywebview.api.get_data(groupName, databaseName, tableName)
    .then(data => {
      const rowData = data.find(item => item.shortcut === shortcut);

      isEditorUpdate = true;  // Set before updating the editor
      if (rowData) {
        // Primeiro, decodificar as entidades HTML
        let decodedExpansion = decodeHtml(rowData.expansion);
        // Em seguida, formatar o artigo usando sua função
        let formattedExpansion = formatArticle(decodedExpansion);

        tinyMCE.get('editor').setContent(formattedExpansion);

        // Update dropdown based on the format value
        var escolhaDropdown = document.getElementById('escolha');
        escolhaDropdown.value = rowData.format ? '1' : '0';

        // Reinitialize the editor based on the dropdown value
        reinitializeEditor(escolhaDropdown.value);
      } else {
        tinyMCE.get('editor').setContent('');
      }
      isEditorUpdate = false;  // Reset after updating the editor
    })
    .catch(error => console.error("Error fetching recent data:", error));

  document.getElementById('shortcutInput').value = this.dataset.shortcut;
}




//--------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------

function initializePyWebView() {
  if (!window.pywebview || !window.pywebview.api) {
    console.error('pywebview API is not available');
    return;
  }

  window.pywebview.api.load_all_states()
    .then(states => {
      appState.buttonStates = states;
      return window.pywebview.api.get_all_db_files();
    })
    .then(allDbFiles => {
      for (let directory in allDbFiles) {
        let db_files = allDbFiles[directory];
        createCollapsible(directory, db_files);
      }
    })
    .catch(console.error);
}

document.addEventListener('DOMContentLoaded', function () {
  window.addEventListener('pywebviewready', function () {
    if (window.pywebview && window.pywebview.api) {
      console.log("pywebview API is ready");
      initializePyWebView();
    } else {
      console.error("Failed to load pywebview API");
    }
  });

  document.getElementById("content").addEventListener("click", function (event) {
    event.stopPropagation();
  }, false);

  let collapsibles = document.getElementsByClassName("content");
  for (let i = 0; i < collapsibles.length; i++) {
    collapsibles[i].addEventListener("click", function (event) {
      event.stopPropagation();
    }, false);
  }
});

window.onbeforeunload = function () {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.save_all_states(appState.buttonStates);
  }
};
