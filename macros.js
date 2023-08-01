document.addEventListener('DOMContentLoaded', function () {
    console.log('DOMContentLoaded event fired');

    var status = document.getElementById('status');
    var events = document.getElementById('eventos');

    var statusIntervalId = null;

    function startStatusUpdates() {
        statusIntervalId = setInterval(updateEvents, 100);  // Call updateEvents every 100ms
    }

    function stopStatusUpdates() {
        if (statusIntervalId) {
            clearInterval(statusIntervalId);
            statusIntervalId = null;
        }
    }

    function updateEvents() {
        window.pywebview.api.get_events().then(function (eventsList) {
            events.innerHTML = eventsList.join('<br>');
        });
    }

    var startButton = document.getElementById('startRecording');
    if (!startButton) {
        console.log('startButton not found');
        return;
    }

    startButton.addEventListener('click', function () {
        console.log('startButton clicked');
        status.innerHTML = "Gravação iniciada";
        window.pywebview.api.start_recording().then(startStatusUpdates);
    });

    var pauseButton = document.getElementById('pauseRecording');
    if (pauseButton) {
        pauseButton.addEventListener('click', function () {
            console.log('pauseButton clicked');
            status.innerHTML = "Gravação pausada";
            window.pywebview.api.pause_recording().then(stopStatusUpdates);
        });
    }

    var resumeButton = document.getElementById('resumeRecording');
    if (resumeButton) {
        resumeButton.addEventListener('click', function () {
            console.log('resumeButton clicked');
            status.innerHTML = "Gravação retomada";
            window.pywebview.api.resume_recording().then(startStatusUpdates);
        });
    }

    var stopButton = document.getElementById('stopRecording');
    if (stopButton) {
        stopButton.addEventListener('click', function () {
            console.log('stopButton clicked');
            status.innerHTML = "Gravação parada";
            window.pywebview.api.stop_recording().then(function () {
                stopStatusUpdates();
                updateEvents();
            });
        });
    }

    var saveButton = document.getElementById('saveMacroButton');
    if (saveButton) {
        saveButton.addEventListener('click', function () {
            var filename = document.getElementById('filename').value;
            if (filename) {
                console.log('saveButton clicked');
                window.pywebview.api.save_macro(filename).then(function (filepath) {
                    stopStatusUpdates();
                    updateEvents();
                    window.pywebview.api.clear_events();
                    status.innerHTML = "Gravação salva em: " + filepath;
                });
            } else {
                alert('Please enter a filename.');
            }
        });
    }
});
