$delayMs = 10   # 產生出來的開檔指令每張之間的間隔

$procs = Get-Process MassiGra -ErrorAction SilentlyContinue | Sort-Object StartTime

$exe = $procs | Select-Object -First 1 -ExpandProperty Path
if (-not $exe) { $exe = 'D:\My Document\My Tools\MassiGra\MassiGra.exe' }

$paths = $procs |
    ForEach-Object { $_.MainWindowTitle -replace '\s*\(\d+/\d+\).*$', '' } |
    Where-Object { $_ }

if (-not $paths) {
    Write-Host "MassiGra 目前沒有開著任何圖。" -ForegroundColor Yellow
} else {
    $paths | ForEach-Object { Write-Host $_ }

    $lines = @()
    $lines += "`$exe = '" + $exe.Replace("'", "''") + "'"
    $lines += '$files = @('
    $lines += $paths | ForEach-Object { "    '" + $_.Replace("'", "''") + "'" }
    $lines += ')'
    $lines += "`$files | ForEach-Object { & `$exe `$_; Start-Sleep -Milliseconds $delayMs }"

    ($lines -join "`r`n") | Set-Clipboard
    Write-Host ""
    Write-Host "共 $($paths.Count) 張，開檔指令已複製到剪貼簿。" -ForegroundColor Green
}

Write-Host ""
Read-Host "按 Enter 關閉"
