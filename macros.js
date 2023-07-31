window.onload = function () {
    // Select the startRecording button
    var startButton = document.getElementById('startRecording');

    // Add event listener to the button
    startButton.addEventListener('click', function () {
        window.pywebview.api.start_recording().then(function (response) {
            alert(response);
            console.log(response);
        });
    });
};