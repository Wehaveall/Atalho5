

window.addEventListener('load', function () {
    // Select the startRecording button
    var startButton = document.getElementById('startRec');

    // Add event listener to the button
    if (startButton) {  // Add a check to ensure startButton is not null
        startButton.addEventListener('click', function () {
            alert('click');
            window.pywebview.api.hello()
                .then(function (response) {
                    alert(response);
                    console.log(response);
                })
                .catch(function (error) {
                    console.log('Error in get_database_names:', error);
                });
        });
    }
});
