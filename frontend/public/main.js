const { app, BrowserWindow, screen: electronScreen } = require('electron')
const is = require('electron-is');

function createMainWindow () {
    const isDev = is.dev();
    let mainWindow = new BrowserWindow({
        width: electronScreen.getPrimaryDisplay().workArea.width,
        height: electronScreen.getPrimaryDisplay().workArea.height,
        show: false,
        backgroundColor: 'white',
        webPreferences: {
            nodeIntegration: true,
            devTools: isDev
        },
        title:"GenGame"
    });
    const startURL = isDev
        ? 'http://localhost:3000'
        : `file://${__dirname}/../build/index.html`;

    mainWindow.loadURL(startURL);

    mainWindow.once('ready-to-show', () => mainWindow.show());

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    mainWindow.webContents.on('new-window', (event, url) => {
        event.preventDefault();
        mainWindow.loadURL(url);
    });
}

app.whenReady().then(() => {
    createMainWindow();

    app.on('activate', () => {
        if (!BrowserWindow.getAllWindows().length) {
            createMainWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
