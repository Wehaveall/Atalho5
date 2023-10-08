// worker.js
self.addEventListener('message', function (e) {
    const totalRows = e.data;  // We're sending only the length of data
    let processedRows = 0;

    for (let index = 0; index < totalRows; index++) {
        processedRows++;
        const progress = (processedRows / totalRows) * 100;

        // Post progress back to main thread
        self.postMessage(progress);
    }
}, false);
