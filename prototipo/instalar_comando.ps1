# Instala o comando analisar para o seu usuario do Windows.
#
# Acrescenta a pasta deste script (a pasta prototipo) ao PATH do seu usuario.
# Depois, em qualquer terminal novo, basta entrar na pasta do projeto com cd
# e digitar:
#   analisar             analisa a pasta atual
#   analisar --falar     analisa e fala o relatorio pelo NVDA
#
# Uso, na pasta prototipo:
#   powershell -ExecutionPolicy Bypass -File .\instalar_comando.ps1
#   powershell -ExecutionPolicy Bypass -File .\instalar_comando.ps1 -Remover
#
# Nao precisa de administrador: muda so o PATH do seu usuario, nunca o do
# sistema, e rodar de novo nao duplica a entrada. -Remover desfaz.
#
# O arquivo e so ASCII de proposito: o Windows PowerShell 5.1 le .ps1 sem BOM
# na codepage ANSI e estragaria os acentos.
param([switch]$Remover)

$ErrorActionPreference = "Stop"
$pasta = $PSScriptRoot

if (-not (Test-Path -LiteralPath (Join-Path $pasta "analisar.cmd"))) {
    Write-Host ("Erro: nao achei o analisar.cmd em " + $pasta + ". Rode este script de dentro da pasta prototipo.")
    exit 1
}

# Compara as entradas do PATH pelo lugar para onde apontam: com variaveis como
# %USERPROFILE% expandidas, sem aspas e sem barra no fim.
function Normalizar([string]$entrada) {
    $texto = [Environment]::ExpandEnvironmentVariables($entrada).Trim().Trim('"')
    return $texto.TrimEnd('\')
}

# O PATH do usuario fica no registro, em HKEY_CURRENT_USER\Environment. Ele e
# lido sem expandir as variaveis e regravado com o mesmo tipo, para entradas
# como %USERPROFILE%\AppData\... continuarem escritas como estavam.
$chave = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey("Environment")
$semExpandir = [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames
$atual = [string]$chave.GetValue("Path", "", $semExpandir)
$tipo = [Microsoft.Win32.RegistryValueKind]::ExpandString
if (($chave.GetValueNames() -contains "Path") -and ($chave.GetValueKind("Path") -eq [Microsoft.Win32.RegistryValueKind]::String)) {
    $tipo = [Microsoft.Win32.RegistryValueKind]::String
}

$alvo = Normalizar $pasta
$entradas = @($atual -split ";" | Where-Object { $_.Trim() -ne "" })
$outras = @($entradas | Where-Object { (Normalizar $_) -ne $alvo })
$instalado = $outras.Count -lt $entradas.Count
$mudou = $false

if ($Remover) {
    if (-not $instalado) {
        Write-Host "O comando analisar nao estava instalado. Nada foi mudado."
    } else {
        if ($outras.Count -eq 0) {
            $chave.DeleteValue("Path", $false)
        } else {
            $chave.SetValue("Path", ($outras -join ";"), $tipo)
        }
        $mudou = $true
        Write-Host ("Pronto: a pasta " + $pasta + " saiu do PATH do seu usuario.")
        Write-Host "Os arquivos do prototipo continuam onde estavam."
    }
} else {
    if ($instalado) {
        Write-Host ("O comando analisar ja estava instalado: a pasta " + $pasta + " ja esta no PATH do seu usuario.")
    } else {
        $base = $atual.Trim().TrimEnd(";")
        if ($base -eq "") {
            $novo = $pasta
        } else {
            $novo = $base + ";" + $pasta
        }
        $chave.SetValue("Path", $novo, $tipo)
        $mudou = $true
        Write-Host ("Pronto: a pasta " + $pasta + " entrou no PATH do seu usuario.")
    }
}
$chave.Close()

if ($mudou) {
    # Avisa os programas abertos, como o Explorador, que o ambiente mudou: os
    # terminais abertos a partir de agora ja enxergam o PATH novo. Apagar pelo
    # .NET uma variavel de usuario que nao existe dispara esse aviso sem mudar
    # mais nada.
    [Environment]::SetEnvironmentVariable("ANALISADOR_AVISO_DE_PATH", $null, "User")
}

if (-not $Remover) {
    Write-Host ""
    Write-Host "Feche o terminal e abra um novo; no VS Code, feche e abra o VS Code."
    Write-Host "Depois, entre na pasta do projeto com cd e digite: analisar"
    Write-Host "Para ouvir o relatorio pelo NVDA, digite: analisar --falar"
    if (-not (Test-Path -LiteralPath (Join-Path $pasta ".venv\Scripts\python.exe"))) {
        Write-Host ""
        Write-Host "Aviso: o ambiente .venv ainda nao existe. Antes de usar o comando, rode:"
        Write-Host "powershell -ExecutionPolicy Bypass -File .\preparar_windows.ps1"
    }
}
