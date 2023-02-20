Add-Type -AssemblyName Microsoft.VisualBasic

while ($true) {
    $inputPath = Read-Host "Please enter path"
    if ($inputPath -eq '') {
        break
    }

    $namePattern = Read-Host "Please enter pattern of filesnames"
    if ([string]::IsNullOrWhiteSpace($namePattern)) {
        $namePattern = "*"
    }

    $paths = $inputPath.Split(",")
    
    foreach ($path in $paths) {
        if (!$path) {
            continue
        }
		
        Set-Location -LiteralPath $path.Trim()

        # move matched files to to /Orignal
        $originFolder = "./Orignal"
        if (-Not (Test-Path -Path $originFolder)) {
            New-Item -Path . -Name "Orignal" -ItemType "directory"
            Move-Item -Path .\$namePattern.* -Include "*.jpg", "*.jpeg", "*.png" -Destination "Orignal"
        }

        # run magick
        $magickExePath = "C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"
        $arguments = "-monitor", "./Orignal/*", "-resize", "x2160>", "-set", "filename:name", "%t", "./%[filename:name]-resized.jpg"

        try {
            &$magickExePath $arguments
        }
        catch {
            break
        }
		
        [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory("$path/Orignal" , "OnlyErrorDialogs", "SendToRecycleBin")
    }
    
    Write-Host "Done!"
}

