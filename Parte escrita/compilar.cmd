@echo off
rem Compila a monografia: pdflatex, biber e mais duas passadas do pdflatex.
rem
rem   compilar          compila e atualiza o UFV-modelo-TCC.pdf
rem   compilar abrir    compila e abre o PDF no fim
rem
rem Precisa do MiKTeX (ou do TeX Live) instalado. Na primeira vez, o MiKTeX
rem baixa os pacotes do modelo e demora mais. Funciona de qualquer pasta.
rem O arquivo e so ASCII de proposito: o cmd do Windows estraga acentos.
setlocal
cd /d "%~dp0"
set "DOC=UFV-modelo-TCC"

rem Um terminal aberto antes da instalacao do MiKTeX nao enxerga o PATH novo;
rem por isso as pastas padrao do MiKTeX e do TeX Live tambem sao procuradas.
where pdflatex >nul 2>nul || call :procurar_tex
where pdflatex >nul 2>nul || goto sem_latex
where biber >nul 2>nul || goto sem_biber

echo [1 de 4] pdflatex: lendo o texto e anotando as citacoes...
echo          Na primeira vez, o MiKTeX baixa dezenas de pacotes e esta etapa pode
echo          levar varios minutos sem mostrar nada. Nao feche a janela nem aperte Ctrl+C.
pdflatex -interaction=nonstopmode -file-line-error "%DOC%.tex" >nul
if errorlevel 1 goto erro_latex
echo [2 de 4] biber: montando as referencias...
biber "%DOC%" >nul
if errorlevel 1 goto erro_biber
echo [3 de 4] pdflatex: encaixando as referencias...
pdflatex -interaction=nonstopmode -file-line-error "%DOC%.tex" >nul
if errorlevel 1 goto erro_latex
echo [4 de 4] pdflatex: acertando sumario e numeracao...
pdflatex -interaction=nonstopmode -file-line-error "%DOC%.tex" >nul
if errorlevel 1 goto erro_latex

echo.
echo Pronto: %DOC%.pdf atualizado em %CD%
if /i "%~1"=="abrir" start "" "%DOC%.pdf"
exit /b 0

:erro_latex
echo.
echo Erro na compilacao. Linhas com problema, tiradas do %DOC%.log:
findstr /r /c:"^!" /c:"\.tex:[0-9][0-9]*: " "%DOC%.log"
echo.
echo Se o PDF estiver aberto num leitor que trava o arquivo, como o Adobe Reader,
echo feche-o e rode de novo. Se o erro continuar, apague o %DOC%.aux e tente outra vez.
pause
exit /b 1

:erro_biber
echo.
echo Erro no biber. Detalhes no arquivo %DOC%.blg:
findstr /c:"ERROR" "%DOC%.blg"
pause
exit /b 2

:sem_latex
echo Erro: nao encontrei o pdflatex no PATH nem nestas pastas:
echo   %LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64
echo   %ProgramFiles%\MiKTeX\miktex\bin\x64
echo Se o MiKTeX acabou de ser instalado, feche o terminal e abra outro. No terminal
echo do VS Code, feche e abra o VS Code inteiro. Se nao instalou, baixe em miktex.org/download.
pause
exit /b 3

:sem_biber
echo Erro: nao encontrei o biber. No MiKTeX Console, aba Packages, instale o pacote biber-windows-x64.
pause
exit /b 3

:procurar_tex
for %%P in ("%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64" "%ProgramFiles%\MiKTeX\miktex\bin\x64") do (
    if exist "%%~P\pdflatex.exe" set "PATH=%%~P;%PATH%"
)
for /d %%P in ("%SystemDrive%\texlive\*") do (
    if exist "%%~P\bin\windows\pdflatex.exe" set "PATH=%%~P\bin\windows;%PATH%"
)
exit /b 0
