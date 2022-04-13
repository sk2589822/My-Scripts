const fs = require('fs');
const path = require('path');

(async function () {
  const folderPath = `F:\\EX\\Game`
  const iconPath = 'IconResource=C:\\Windows\\SYSTEM32\\SHELL32.dll'
  const oldIconNumber = 0
  const newIconNumber = 0

  const folders = fs.readdirSync(`${folderPath}`, { withFileTypes: true })

  for (const folder of folders) {
    if (folder.isDirectory()) {
      const subFolderPath = path.resolve(`${folderPath}`, folder.name);
      const files = fs.readdirSync(subFolderPath)

      for (const file of files) {
        if (file === 'desktop.ini') {
          const iniPath = path.resolve(subFolderPath, `desktop.ini`);
          console.log(iniPath);

          let ini = fs.readFileSync(iniPath, 'utf8')
          const regex = new regex(`^${iconPath},${oldIconNumber}$`, 'im')
          if (regex.test(ini)) {
            ini = ini.replace(regex, `${iconPath},${newIconNumber}`)
            console.log(ini);
            // https://github.com/nodejs/node/issues/41093
            fs.writeFileSync(iniPath, ini, { encoding: 'utf-8', flag: fs.constants.O_EXCL | fs.constants.O_WRONLY })
          }
        }
      }
    }
  }
})()




