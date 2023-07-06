



function maximizeOrRestore() {

    var button = document.getElementById("maxRestore");  // get the button
    var icon = button.getElementsByTagName('img')[0];  // get the img element in the button
  
    // check the current icon and change it
    if (icon.src.includes("maxBtn_white")) {
     
      icon.src = "/src/images/restoreBtn_white.png";  // change to restore icon
    } else {
     
      icon.src = "/src/images/maxBtn_white.png";  // change back to maximize icon
    }
    

    pywebview.api.maximize_or_restore_window();  // Let Python handle the maximizing/restoring

    
  }
  