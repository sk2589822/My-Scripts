Add-Type -AssemblyName Microsoft.VisualBasic

while ($true) {
  $inputPath = Read-Host "Path of directory: "
  if ($inputPath -eq '') {
    break
  }

  $namePattern = Read-Host "Pattern of filesnames: "
  if ([string]::IsNullOrWhiteSpace($namePattern)) {
    $namePattern = "*"
  }

  $isRecursive = Read-Host "Recursive?(y/N)"

  if ($isRecursive -eq 'y' -or $isRecursive -eq 'Y' -or $isRecursive -eq '1') {
    $paths = @(ls $inputPath)
  } else {
    $paths = New-Object System.Collections.ArrayList
    foreach ($path in $inputPath.Split(",")) {
      $paths.Add($path.Trim())
    }
    $paths = $paths.toArray()
  }
  
  foreach ($path in $paths) {
    if (!$path) {
      continue
    }

    if (-not (get-item $path).PSIsContainer) {
      $path = [System.IO.Path]::GetDirectoryName($path)
    }

    Set-Location -LiteralPath $path

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

