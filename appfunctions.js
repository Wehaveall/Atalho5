let left_Panel_Collapsible_States = {};

var appState = {buttonStates: {}};

var activeCollapsibleButton = null;
var buttonStates = appState.buttonStates;
var allDbFiles = {};


var numberOfEnters = 2; // Você pode ajustar esse valor conforme necessário
//preciso que seja global, para ajustar a quantidade de enters!!



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


function decodeHtml(html) {
  var txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}



//----------------------------------------------------------------
//Clique do botão de configuração dos Grupos
function showDataSettingsPanel() {
  var dataSettingsPanel = document.getElementById('dataSettingsPanel');
  var middlePanel = document.getElementById('middlePanel');
  var rightPanel = document.getElementById('rightPanel');

  // Mostrar o painel de configurações de dados e ocultar os painéis do meio e da direita
  dataSettingsPanel.style.display = 'flex';
  middlePanel.style.display = 'none';
  rightPanel.style.display = 'none';
}

function hideDataSettingsPanel() {
  var dataSettingsPanel = document.getElementById('dataSettingsPanel');
  var middlePanel = document.getElementById('middlePanel');
  var rightPanel = document.getElementById('rightPanel');

  // Ocultar o painel de configurações de dados e mostrar os painéis do meio e da direita
  dataSettingsPanel.style.display = 'none';
  middlePanel.style.display = 'flex';
  rightPanel.style.display = 'flex';
}

// Adicionar um ouvinte de evento para clicar em qualquer child (por exemplo, em um elemento da tabela)



//------------------------------------------------------------------

function saveCheckBoxStates() {
  // Call Python function to save checkBoxStates to JSON file
  window.pywebview.api.save_checkBox_states(checkBoxStates);
}






//Formata o expansion das tabelas jurídicas
//-----------------------------------------------------------------
function formatExpansion(expansion, tableName) {
  if (tableName === 'aTable') {
    // Remove os caracteres especiais "#" "%" "&" "*"
    expansion = expansion.replace(/[#%&@*]/g, '');

    // Nova linha: Remove os delimitadores "++"
    expansion = expansion.replace(/\+\+/g, '');
  }
  // Você pode adicionar mais lógica de formatação aqui, se necessário
  return expansion; // Retorna a expansão formatada
}



// Apenas no caso de aTable!!!!!

function convertHtmlToPlainText(html) {
  var tempDiv = document.createElement("div");
  tempDiv.innerHTML = html;
  return tempDiv.textContent || tempDiv.innerText || "";
}



//----------------------------------------------------------------
//Formata  o texto dentro do tinyMCE editor
//----------------------------------------------------------------



function formatArticle(article, tableName) {
  // Apenas no caso de aTable!!!!!
  if (tableName === 'aTable') {
    // Convert HTML to plain text
    article = convertHtmlToPlainText(article);

    var numberOfEnters = 2; // Adjust this value as needed
    var lineBreaks = '<br/>'.repeat(numberOfEnters); // Repeat the line break the desired number of times

    // Trim whitespace from the start and end of the article
    article = article.trim();

    // Initialize a counter for occurrences of "++"
    let plusCounter = 0;

    // Replace "++" not preceded by "*" with line breaks, except for the first occurrence
    article = article.replace(/\+\+/g, (match, offset, fullString) => {
      if (offset > 0 && fullString[offset - 1] === '*') return match;
      plusCounter++;
      return plusCounter > 1 ? lineBreaks : '';
    });

    // Replace "Art. " with "<br/>Art. " if "Art." is not the first string in the article
    article = article.replace(/(^|\s)(Art\. )/g, (match, p1, p2) => {
      return p1 ? lineBreaks + p2 : p2;
    });

    // Replace "@", "#", and "$" with the desired number of line breaks
    article = article.replace(/[@#$%]/g, lineBreaks);

    // If the article now starts with a line break, remove it
    if (article.startsWith('<br/>')) {
      article = article.substring(5);
    }

    return article;
  }
  return article; // If tableName is not 'aTable', return the unchanged article
}


//----------------------------------------------------------------
//----------------------------------------------------------------

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;

  tabcontent = document.querySelectorAll(".tabcontent, .tabcontent_2, .tabcontent_3, .tabcontent_4, .tabcontent_5" ); 

  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  if (tabName === 'Tab4') {
    document.getElementById(tabName).style.display = "flex";
  } else {
    document.getElementById(tabName).style.display = "block";
  }

  evt.currentTarget.className += " active";
}



////////////////////////////////////////////////////////////////Esconder tela de caregamento
function hideLoadingScreen() {
  document.getElementById("loadingScreen").style.display = "none";
}


function salvar_Label(event) {
  pywebview.api.update_description(event.target.value);
}



////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
function createCollapsible(directory, db_files) {
  const leftPanel = document.getElementById('leftPanel');

  // Remove existing collapsibleParent if it exists
  const existingCollapsible = document.getElementById(directory + '-parent');
  if (existingCollapsible) {
    existingCollapsible.remove();
  }

  // Create a parent div for the collapsible and its content
  const collapsibleParent = document.createElement('div');
  collapsibleParent.id = directory + '-parent';
  collapsibleParent.style.width = '90%';

  // Create the button
  const collapsibleButton = document.createElement('button');
  collapsibleButton.id = directory;
  collapsibleButton.className = 'collapsible';
  collapsibleButton.innerHTML = `▶ ${directory}`;
  collapsibleButton.addEventListener('click', toggleCollapsible);

  // Create the content div

  const contentDiv = document.createElement('div');
  contentDiv.id = directory + '-content';
  contentDiv.className = 'left-panel-content'; // Added this class for animation

  // Create database files list with checkboxes
  db_files.forEach((databaseFile) => {
    const filenameWithoutExtension = databaseFile.replace('.db', '');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'db-file-checkbox';

    const dbFileElem = document.createElement('div');
    dbFileElem.className = 'child-elem';
    dbFileElem.textContent = filenameWithoutExtension;

    // Add click event listener here
    const tableName = "someTableName";  // replace with the actual table name
    dbFileElem.addEventListener('click', handleDbFileElemClick(directory, filenameWithoutExtension, databaseFile, tableName));

    const wrapper = document.createElement('div');
    wrapper.className = 'wrapper';
    wrapper.appendChild(checkbox);
    wrapper.appendChild(dbFileElem);

    contentDiv.appendChild(wrapper);
  });

  // Append elements
  collapsibleParent.appendChild(collapsibleButton);
  collapsibleParent.appendChild(contentDiv);
  leftPanel.appendChild(collapsibleParent);
}



// This function will be used as the event listener for dbFileElem click events
function handleDbFileElemClick(directory, filenameWithoutExtension, databaseFile, tableName) {
  return async function () {  // Make the function async
 
    hideDataSettingsPanel();
    document.getElementById('rightPanel').style.display = 'none';
    document.getElementById('middlePanel').style.display = 'flex';
 

    //Reset Progress Bar Value here
    // Reset the progress bar to 0 here TOOOOOOO
    const progressBar = document.getElementById('progress-bar');
    progressBar.value = 0;
    document.getElementById('progress-container').style.display = 'block';


    // Hide the table initially
    document.getElementById('myTable').style.visibility = 'hidden';
    document.getElementById('tableContainer').style.overflow = 'hidden';
 
    // Remove 'child-focused' class from all children
    let allChildElements = document.getElementsByClassName('child-elem');
    for (let i = 0; i < allChildElements.length; i++) {
      allChildElements[i].classList.remove('child-focused');
    }

    // Add 'child-focused' class to the clicked element
    this.classList.add('child-focused');


    //Group Manager State
    var groupManage = document.getElementById('groupManage');
    groupManage.style.display = 'flex';

    // Get reference to the name of database
    var selectedDbNameElem = document.getElementById('selectedDbName');
    selectedDbNameElem.textContent = filenameWithoutExtension;

    // Get the table names dynamically
    try {
      const tableNames = await window.pywebview.api.get_tables(directory, databaseFile);
      // Assuming you want to use the first table name returned
      const tableName = tableNames[0] || "defaultTableName";  // replace defaultTableName with a sensible default
      // Populate middle panel with respective database data
      const data = await fetchData(directory, filenameWithoutExtension, tableName);
      // Now, populate the table
      populateTable(data, directory, filenameWithoutExtension, tableName);
    } catch (error) {
      console.error('Error in get_tables:', error);
    }
  }
}



/////////////////////////////////////////////////////////////////    LOAD COLLAPSIBLE STATES   /////////////////////////////////
// Function to initialize the states of collapsibles based on saved states
function initializeCollapsibleStates(savedStates) {
  for (const [collapsibleId, state] of Object.entries(savedStates)) {
    const collapsibleElement = document.getElementById(collapsibleId);
    const content = collapsibleElement.nextElementSibling;

    if (state === 'block') {
      collapsibleElement.classList.add('active');
      content.style.maxHeight = content.scrollHeight + 'px';
      collapsibleElement.innerHTML = `▼ ${collapsibleElement.id}`;
    } else {
      collapsibleElement.classList.remove('active');
      content.style.maxHeight = null;
      collapsibleElement.innerHTML = `▶ ${collapsibleElement.id}`;
    }
  }
}


///////////////////////////////////////////////////////////////////  TOGGLE COLLAPSIBLE    ////////////////////////////////////////////////////////
// Function to toggle collapsible content
// Keep track of the last clicked collapsible
let lastClickedCollapsible = null;

function toggleCollapsible() {

  const content = this.nextElementSibling;

  // Remove 'focused' class from the last clicked collapsible
  if (lastClickedCollapsible) {
    lastClickedCollapsible.classList.remove('focused');
  }

  // Add 'focused' class to the currently clicked collapsible
  this.classList.add('focused');

  // Update the last clicked collapsible
  lastClickedCollapsible = this;

  // Initialize state as 'none'
  let newState = 'none';

  // Toggle active class
  this.classList.toggle('active');

  // Existing collapsible toggle logic
  if (content.style.maxHeight) {
    content.style.maxHeight = null;
    this.innerHTML = `▶ ${this.id}`;
  } else {
    content.style.maxHeight = content.scrollHeight + 'px';
    this.innerHTML = `▼ ${this.id}`;
    newState = 'block';  // Update state to 'block'
  }

  // Capture current state
  const collapsibleId = this.id;  // Assuming the id is set on the clicked element

  left_Panel_Collapsible_States[collapsibleId] = newState;

  pywebview.api.save_all_states(left_Panel_Collapsible_States).then(response => {
    if (response.status === 'success') {
      console.log('State updated successfully.');
    } else {
      console.log('Failed to update state:', response.message);
    }
  });

  // Hide the middle and right panels
  document.getElementById('middlePanel').style.display = 'none';
  document.getElementById('rightPanel').style.display = 'none';
}




///////////////////////////////////////////////////////////////////////////////////////////////////

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}



//////////////////////////////////////////////////////////////////    /POPULATE   /////////////////////////////////


async function populateTable(data, groupName, databaseName, tableName) {
  
  //Reset Progress Bar Value here
  const progressBar = document.getElementById('progress-bar');
  progressBar.value = 0;


  // Reference to the table
  var table = document.getElementById('myTable');
  // Clear existing rows (except for the header)
  
  // Create a new Worker
  const worker = new Worker('worker.js');
 
  while (table.rows.length > 1) {
    table.deleteRow(1);
  }


  // Listen for messages from the Worker (for progress updates)
  worker.addEventListener('message', function (e) {
    const progress = e.data;
    
    
    requestAnimationFrame(() => {
      progressBar.value = progress;  // Update the progress bar within requestAnimationFrame
    });

 // Make the table visible when progress reaches 100%
    if (progress >= 100) {
      table.style.visibility = 'visible';
      // Hide progress bar when table is populated
      document.getElementById('progress-container').style.display = 'none';
      document.getElementById('tableContainer').style.overflow = 'auto';
    
    }
    
    else {  
    // Show progress bar
      document.getElementById('progress-container').style.display = 'block';
    }

  }, false);

  // Start the Worker
  worker.postMessage(data.length);  // Send only the length of data to worker




  // Iterate over data and add new rows
  for (let index = 0; index < data.length; index++) {
    const item = data[index];
 
    var rowClass = index % 2 === 0 ? 'tr-even' : 'tr-odd';
    // Extract the values from the item
    const { expansion, label, shortcut, format, case: caseChoice } = item;

    // Create a new row and cells
    var row = table.insertRow(-1);
    row.className = rowClass; // Apply the class to the row
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    row.dataset.index = index;  // <-- Add this line

    // Convert the HTML expansion to plain text
    var plainExpansion = decodeHtml(expansion.replace(/<[^>]*>/g, ''));

    // Store the values as data attributes for the row
    Object.assign(row.dataset, {
      expansion,
      shortcut,
      format,
      label,
      tableName,
      groupName,
      databaseName,
      caseChoice
    });

    // Formata a expansão das tabelas Jurídicas (tableName "aTable")
    var formattedExpansion = formatExpansion(plainExpansion, tableName);

    // Populate the cells with content
    cell1.appendChild(createCellContent('truncate', expansion === "" ? label : formattedExpansion));
    cell2.appendChild(createCellContent('truncate', shortcut, 'right'));

    // Add the row click event
    row.addEventListener('click', handleRowClick);
   
  };
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
var rowSelected = false;  // Adicione esta variável de flag fora de qualquer função, no escopo global
var isRowClick = false;  // Adicionado no início do seu script
var preventSave = false;
var isEditorUpdate = false;
var isSaving = false;


//----------------------------------------------------------------
//----------------------------------------------------------------
//----------------------------------------------------------------
var jsOperationCompleted = false; // Global variable

async function copyHtmlToClipboard(html) {
  const item = new ClipboardItem({
    "text/html": new Blob([html], {type: "text/html"})
  });
  await navigator.clipboard.write([item]);
  jsOperationCompleted = true;  // Set the global variable to true
}



function handleRowClick() {
  // Se uma operação de salvamento estiver em andamento, retorne imediatamente
  if (isSaving) return;

// Show the #rightPanel without modifying the width of #middlePanel
document.getElementById('rightPanel').style.display = 'flex';

  // Deselect the previously selected row, if any
  if (window.currentRow && window.currentRow !== this) {
    window.currentRow.className = '';  // Deselect the previous row
  }

  // Highlight the current row
  this.className = 'selected';
  window.currentRow = this;

  // Extract the relevant data from the clicked row
  const { groupName, databaseName, tableName, shortcut, label, format, caseChoice } = this.dataset;


  const index = this.dataset.index;  // <-- Add this line to get the index

  
  // Fetch the most recent data from the cache or database
  window.pywebview.api.get_data(groupName, databaseName, tableName)
    .then(data => {
      const rowData = data[index];  // Use the index to get the specific row

      isEditorUpdate = true;  // Set before updating the editor
      if (rowData) {
        // Primeiro, decodificar as entidades HTML
        let decodedExpansion = decodeHtml(rowData.expansion);
        // Em seguida, formatar o artigo usando sua função
        let formattedExpansion = formatArticle(decodedExpansion, tableName);

        tinyMCE.get('editor').setContent(formattedExpansion);



        // Set the "atalho" value inside the #shortcutName div
        const shortcutNameDiv = document.getElementById('shortcutName');
        shortcutNameDiv.innerHTML = `Atalho: ${shortcut}`;

        const { label } = this.dataset;
        document.getElementById('label').value = label;


        // Update dropdown based on the format value
        const selectValue = rowData.format ? '1' : '0';

        // Update the custom select for caseChoice
        const caseChoiceSelectId = 'caseChoice';
        const customCaseChoiceSelect = window.customSelects[caseChoiceSelectId];
        if (customCaseChoiceSelect) {
          customCaseChoiceSelect.selectValue(caseChoice);
        } else {
          alert('Error: customSelect is not found for ID ' + caseChoiceSelectId);
        }


        // Assuming the select element has an ID, and customSelects is accessible here:
        const selectId = 'escolha'; // Replace with the actual ID
        const customSelect = window.customSelects[selectId];
        if (customSelect) {
          customSelect.selectValue(selectValue);
        } else {
          alert('Error: customSelect is not found for ID ' + selectId);
        }
        // Reinitialize the editor based on the dropdown value
        reinitializeEditor(selectValue);
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

function saveLabelValue(newValue) {
  var shortcut = window.currentRow.dataset.shortcut;
  var groupName = window.currentRow.dataset.groupName;
  var tableName = window.currentRow.dataset.tableName;
  var databaseName = window.currentRow.dataset.databaseName;
  var formatValue = document.getElementById('escolha').value === "1";
  var caseChoice = document.getElementById('caseChoice').value;

  window.pywebview.api.save_changes(groupName, databaseName, tableName, shortcut, null, formatValue, newValue, caseChoice)
    .then(response => {
      console.log('Label value saved:', response);
      // Atualize o valor do data-label na linha selecionada
      window.currentRow.dataset.label = newValue;

      // Invalidar a entrada de cache após salvar
      invalidateCacheEntry(groupName, databaseName, tableName);
    })
    .catch(error => {
      console.error('Error saving label value:', error);
    });
}


/////////////////////////////////////////////////////////////////////////////////////////////////


document.addEventListener("DOMContentLoaded", function () {
  const themeToggle = document.getElementById("darkmode-toggle");
  const body = document.body;

  themeToggle.addEventListener("click", function () {
    if (body.classList.contains("dark-theme")) {
      body.classList.remove("dark-theme");
      body.classList.add("light-theme");

    } else {
      body.classList.remove("light-theme");
      body.classList.add("dark-theme");
    }
  });
});












/////////////////////////////////////////////////////////////////////////////////////////////////////

function initializePyWebView() {
  if (!window.pywebview || !window.pywebview.api) {
    console.error('pywebview API is not available');
    return;
  }

  // Load checkbox states
  window.pywebview.api.load_checkBox_states()
    .then(states => {
      checkBoxStates = states;
      // Initialize checkboxes based on these states
    });

  // Load all states including button states for collapsibles
  window.pywebview.api.load_all_states()
    .then(states => {
      appState.buttonStates = states;
      left_Panel_Collapsible_States = states;  // Initialize the left panel states
      return window.pywebview.api.get_all_db_files();
    })
    .then(allDbFiles => {
      for (let directory in allDbFiles) {
        let db_files = allDbFiles[directory];
        createCollapsible(directory, db_files);
      }
      initializeCollapsibleStates(left_Panel_Collapsible_States);  // Initialize collapsibles based on saved states
    })
    .catch(console.error);
}
document.addEventListener('DOMContentLoaded', function () {
  window.addEventListener('pywebviewready', function () {
    if (window.pywebview && window.pywebview.api) {
      console.log("pywebview API is ready");
      initializePyWebView();


      pywebview.api.get_initial_states().then(response => {
        initializeCollapsibleStates(response);
    });

      // Adicione este código em um lugar onde o DOM esteja carregado

      // Pegue o elemento input pelo nome
      var labelInput = document.getElementById('label');

      // Adicione um event listener para detectar mudanças no valor do input
      labelInput.addEventListener('input', function () {
        // Chame a função para salvar os dados
        saveLabelValue(this.value);
      });



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


window.addEventListener("load", function () {
  hideLoadingScreen();

});



window.onbeforeunload = function () {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.save_all_states(appState.buttonStates);
  }
};
