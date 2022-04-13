const fs = require('fs')
const path = require('path')

class AssFormatter {
  constructor(folderPath) {
    this._folderPath = folderPath
    this._outputPath = `${folderPath}\\FormattedAss`
    this._files = []

    this.createOutputFolder()
  }

  createOutputFolder() {
    if (fs.existsSync(this._outputPath)) {
      return
    }

    fs.mkdirSync(this._outputPath)
  }

  readFiles() {
    this._files = fs.readdirSync(this._folderPath)
  }

  format() {
    this._files
      .filter(fileName => /\.ass$/.test(fileName))
      .forEach(fileName => {
        if (!/\.ass$/.test(fileName)) {
          return
        }

        this.outputFormattedAssFile(fileName)
        this.renameVideoFile(fileName)
      })
  }

  getFormattedAss(file) {
    const defaults = [
      'Default',
      '魔穗体',
      'maho',
      'Maho',
      'Taka\-Default',
      'Sub\-CN',
      'Sub\-CH',
    ]
    defaults.forEach(str => {
      const regex = new RegExp(`^Style: ?${str} ?,.*$`, 'm')
      file = file.replace(regex, '')
    })

    if (file.match(/^Style:/)) {
      file = file.replace(/^Style: /m, 'Style: Default,Microsoft YaHei,38,&H00FFFFFF,&HF0000000,&H00800080,&HF0000000,-1,0,0,0,100,100,0,0,1,1,0,2,30,30,10,134\nStyle: ')
    } else {
      file = file.replace(/(^Format: Name, Fontname.*?$)/m, '$1\n\nStyle: Default,Microsoft YaHei,38,&H00FFFFFF,&HF0000000,&H00800080,&HF0000000,-1,0,0,0,100,100,0,0,1,1,0,2,30,30,10,134')
    }

    file = file.replace(/^PlayResX: ?\d+$/m, 'PlayResX: 1280')
    file = file.replace(/^PlayResY: ?\d+$/m, 'PlayResY: 720')
    file = file.replace(/^ScaledBorderAndShadow: ?yes$/m, 'ScaledBorderAndShadow: no')
    file = file.replace(/^Style: Taka-Default -High,方正粗圆_GBK,38,&H00FFFFFF,&H00FFFFFF,&H008140FF,&H96000000/m, 'Style: Default,Microsoft YaHei,38,&H00FFFFFF,&HF0000000,&H00800080,&HF0000000')

    return file
  }

  outputFormattedAssFile(fileName) {
    const file = fs.readFileSync(`${this._folderPath}\\${fileName}`, 'utf8')
    const FormattedAss = this.getFormattedAss(file)
    fs.writeFileSync(`${this._outputPath}\\${fileName}`, FormattedAss, 'utf8')

    console.log(`[Format] ${this._folderPath}\\${fileName}`)
  }

  renameVideoFile(fileName) {
    const fileBaseName = path.basename(fileName, '.ass')
    const videoFileName = this._files.find(videoFileName =>
      videoFileName !== fileName &&
      videoFileName.includes(fileBaseName)
    )

    if (videoFileName) {
      const videoExtension = path.extname(videoFileName)
      const videoFileBaseName = path.basename(videoFileName, videoExtension)
      if (videoFileBaseName && videoExtension) {
        fs.rename(
          `${this._folderPath}\\${videoFileName}`,
          `${this._folderPath}\\${fileBaseName}${videoExtension}`,
          () => {}
        )

        console.log(`[Rename] ${this._folderPath}\\${videoFileName}  ->  ${this._folderPath}\\${fileBaseName}${videoExtension}`)
      }
    }
  }
}

function inputPath() {
  return new Promise(resolve => {
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    })

    readline.question("Input path\n", resolve)
  })
}

(async function () {
  const folderPath = await inputPath()

  const assFormatter = new AssFormatter(folderPath)
  assFormatter.readFiles(folderPath)
  assFormatter.format()
  process.exit()
})()
