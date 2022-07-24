$path = Read-Host "Please enter path"
$namePattern = Read-Host "Please enter pattern of of filesnames"

Set-Location -LiteralPath $path

# move all files to to /Orignal
New-Item -Path . -Name "Orignal" -ItemType "directory"
Move-Item -Path .\*.* -Destination "Orignal"

# run magick
$magickExePath = "C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"
$arguments = "-monitor", "./Orignal/$namePattern", "-resize", "x2160>", "-set", "filename:name", "%t", "$path/%[filename:name]-resized.jpg"

&$magickExePath $arguments

Write-Host "Done!"
[Console]::ReadKey()