const fs = require('fs');
const cheerio = require('cheerio');
const path = require('path');
const ProgressBar = require('progress');
//const iconv = require('iconv-lite');

const loadHTMLFile = (filepath) => {
    try {
      //  const buffer = fs.readFileSync(filepath);
      //  const html = iconv.decode(buffer, 'windows-1252');
        return fs.readFileSync(filepath, 'latin1');
    } catch (err) {
        console.error(`Error reading file from disk: ${err}`);
    }
};

const appendScript = (html, scriptContent) => {
    const $ = cheerio.load(html);
    const script = $('<script></script>');
    script.text(scriptContent);
    $('body').append(script);

    return $.html();
};

const writeToFile = (filepath, data) => {

   

      
    fs.writeFile(filepath, data, 'latin1', (err) => {
        if (err) {
            console.error(`Failed to write to file: ${err}`);
        } else {
            console.log(`File is saved as ${filepath}`);
           
        }
    });
};

const directoryPath = 'G:/'; // replace with your directory path
const scriptContent = `     
// Pegar o texto dos parágrafos - Primeiro Passo
var elementos = document.getElementsByTagName('p');
    const newArray = Array.from(elementos)
    
    newArray.forEach(function(element){

        if (element.innerText.startsWith('Art. ')) {
            element.innerText = element.innerText.replace('Art. ' ,'* Art. ');
        }
  
        
// Substituir os "o" por "º"    - Segundo passo     
var artnum = 1

while (artnum <= 9)
{
    if (element.innerText.startsWith('* Art. '+ artnum +  ' o')) {
            element.innerText = element.innerText.replace('* Art. '+ artnum + ' o','* Art. ' + artnum + 'º');
        }

       // console.log (artnum)
artnum++
}


    })
`; // replace with your script content

fs.readdir(directoryPath, (err, files) => {
    if (err) {
        console.error(`Error getting directory information: ${err}`);
    } else {
        

        files.forEach((file) => {

   // Filter out non-HTML files
   const htmlFiles = files.filter(file => path.extname(file) === '.html');

        
   // Initialize a new progress bar
   const bar = new ProgressBar(':bar :percent', { total: htmlFiles.length });

            if (path.extname(file) === '.html') {

                setTimeout(() => {
                    console.log('This message is displayed after 2 seconds');
                }, 2000);
                
                const filepath = path.join(directoryPath, file);
                const html = loadHTMLFile(filepath);
                const updatedHTML = appendScript(html, scriptContent);
                writeToFile(filepath, updatedHTML);
                
                // Increment the progress bar
                bar.tick()
               
              

                
            }
        });
    }
});
