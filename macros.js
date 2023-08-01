document.addEventListener('DOMContentLoaded', function () {
    console.log('DOMContentLoaded event fired');


    var startButton = document.getElementById('startRecording');
    if (!startButton) {
        console.log('startButton not found');
        return;
    }

    startButton.addEventListener('click', function () {
        console.log('startButton clicked');
        alert('Record');
        window.pywebview.api.teste("oi");
    });

});
