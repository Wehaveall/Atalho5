window.addEventListener('load', function () {

    var startButton = document.getElementById('startRecording');
    var stopButton = document.getElementById('stopRecording');
    var pauseButton = document.getElementById('pauseRecording');
    var resumeButton = document.getElementById('resumeRecording');
    var saveButton = document.getElementById('saveMacroButton');

    // When the start button is clicked, send a message to Python to start recording
    startButton.addEventListener('click', function () {
        webview.api.start_recording(function (macro) {
            alert("foi");
            console.log("Received response from start_recording:", macro);
        });
    });






    // When the stop button is clicked, send a message to Python to stop recording
    stopButton.addEventListener('click', function () {
        webview.api.stop_recording().then(function (macro) {
            console.log("Received response from stop_recording:", macro);
        });
    });

    // When the pause button is clicked, send a message to Python to pause recording
    pauseButton.addEventListener('click', function () {
        webview.api.pause_recording().then(function (macro) {
            console.log("Received response from pause_recording:", macro);
        });
    });

    // When the resume button is clicked, send a message to Python to resume recording
    resumeButton.addEventListener('click', function () {
        webview.api.resume_recording().then(function (macro) {
            console.log("Received response from resume_recording:", macro);
        });
    });

    // When the save button is clicked, send a message to Python to save the macro
    saveButton.addEventListener('click', function () {
        var filename = document.getElementById('filename').value;
        webview.api.save_macro(filename).then(function (macro) {
            console.log("Received response from save_macro:", macro);
        });
    });
});
