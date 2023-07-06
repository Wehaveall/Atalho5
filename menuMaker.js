const {app, Menu} = require('electron')

const isMac = process.platform === 'darwin'

const template = [
    ...(isMac ?[{
        label: app.name,
        submenu: [
            {role: 'about'},
            {role:'separator'},
            {role:'quit'},
    
        ]
    }] : []),

    {
        label: "File",
        submenu: [{
                    label: 'Open',
                    click: async() => {
                        doOpenFile()
                    }
                }
            ]


    },
]

module.exports.mainMenu = Menu.buildFromTemplate(template);