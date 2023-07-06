const axios = require('axios');
const fs = require('fs');




async function downloadFile(url, path) {
   
    /*      PORQUE O PROGRAMA NÃO BAIXAVA O ARQUIVO: O erro ECONNRESET normalmente significa que a conexão TCP foi abruptamente encerrada pelo servidor ou por algum software intermediário.
     Isso pode ser causado por várias razões, como um servidor que encerra a conexão prematuramente ou um ambiente intermediário
      (como um proxy ou firewall) que interrompe a conexão.

    O site http://www.planalto.gov.br/ pode estar restringindo ou limitando conexões de certos clientes ou simplesmente não permitindo conexões
    de programas de raspagem de dados.
    
    Uma maneira de contornar isso é configurar o axios para enviar um User-Agent de um navegador popular. 
    Isso pode enganar o servidor para pensar que a solicitação é de um navegador da web regular, em vez de um programa de raspagem de dados.
    Aqui está como você pode modificar sua função para fazer isso:
    
    Ver também: https://masteringjs.io/tutorials/axios/user-agent       user-agent dentro do headers, dentro do axios(biblioteca)*/

    



    const response = await axios({
        method: 'GET',
        url: url,
        responseType: 'stream',
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    });

    const writer = fs.createWriteStream(path);

    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
    });
}

const url = 'http://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm' // substitua pela URL do arquivo que deseja baixar
const path = 'G:/cpenal.html'; // substitua pela localização onde deseja salvar o arquivo

downloadFile(url, path)
    .then(() => console.log(`Arquivo baixado com sucesso na localização: ${path}`))
    .catch(error => console.error(`Erro ao baixar arquivo: ${error}`));
