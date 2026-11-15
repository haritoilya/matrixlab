# Downloads PDFs and the DINPro font from the old site builder storage.
# Run from the site folder:
#   powershell -ExecutionPolicy Bypass -File scripts\fetch-assets.ps1
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$root = Split-Path -Parent $PSScriptRoot
$S = 'https://90f1661d-2ff4-4f29-b07c-0e47453ca691.selstorage.ru/site684476%2F'
$items = [ordered]@{
  'assets\fonts\DINPro-CondensedBold.eot'   = 'https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.eot'
  'assets\fonts\DINPro-CondensedBold.ttf'   = 'https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.ttf'
  'assets\fonts\DINPro-CondensedBold.woff'  = 'https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.woff'
  'assets\fonts\DINPro-CondensedBold.woff2' = 'https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.woff2'
  'files\buklet-partner.pdf'                = $S + '%D0%91%D1%83%D0%BA%D0%BB%D0%B5%D1%82%5F%D0%9F%D0%B0%D1%80%D1%82%D0%BD%D0%B5%D1%80%2Epdf'
  'files\elastin-klin-issled-statya-1.pdf'  = $S + '%D0%AD%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BD%5F%D0%9A%D0%BB%D0%B8%D0%BD%5F%D0%98%D1%81%D1%81%D0%BB%D0%B5%D0%B4%5F%D0%A1%D1%82%D0%B0%D1%82%D1%8C%D1%8F%5F1%2Epdf'
  'files\elastin-klin-issled-statya-2.pdf'  = $S + '%D0%AD%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BD%5F%D0%9A%D0%BB%D0%B8%D0%BD%5F%D0%98%D1%81%D1%81%D0%BB%D0%B5%D0%B4%5F%D0%A1%D1%82%D0%B0%D1%82%D1%8C%D1%8F%5F2%2Epdf'
  'files\sertifikat-2-stranicy-20221027.pdf' = $S + '%D0%A1%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%202%20%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B%5F20221027%2Epdf'
  'files\sertifikat-sootvetstviya-dobrovolnyj-bad.pdf' = $S + '%D0%A1%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%5F%D1%81%D0%BE%D0%BE%D1%82%D0%B2%D0%B5%D1%82%D1%81%D1%82%D0%B2%D0%B8%D1%8F%5F%D0%B4%D0%BE%D0%B1%D1%80%D0%BE%D0%B2%D0%BE%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9%5F%D0%91%D0%90%2Epdf'
}
$ok = 0
foreach ($k in $items.Keys) {
  $dest = Join-Path $root $k
  New-Item -ItemType Directory -Force (Split-Path -Parent $dest) | Out-Null
  try {
    Invoke-WebRequest -Uri $items[$k] -OutFile $dest -UseBasicParsing
    Write-Host ('OK     ' + $k + '  (' + (Get-Item $dest).Length + ' bytes)')
    $ok++
  } catch {
    Write-Host ('ERROR  ' + $k + '  ' + $_.Exception.Message) -ForegroundColor Red
  }
}
Write-Host ''
Write-Host ('Done: ' + $ok + ' of ' + $items.Count)
