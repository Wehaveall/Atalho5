function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

self.addEventListener('message', async function (e) {
    const totalRows = e.data;  // We're sending only the length of data
    let processedRows = 0;

    for (let index = 0; index < totalRows; index++) {
        processedRows++;

        // Introduce a 1ms delay every 200 rows
        if (processedRows % 200 === 0) {
            await sleep(1);
        }
        const progress = Math.round((processedRows / totalRows) * 100);
        // Post progress back to main thread
        self.postMessage(progress);
    }
}, false);