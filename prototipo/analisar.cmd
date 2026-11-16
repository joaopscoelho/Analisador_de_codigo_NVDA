@echo off
rem Atalho de uma palavra para o analisador (Windows).
rem
rem   analisar                 analisa a pasta atual
rem   analisar pasta\projeto   analisa outra pasta
rem   analisar --falar         analisa e fala o relatorio pelo NVDA
rem   analisar --menu          escolhe a pasta por um menu
rem
rem Usa o ambiente .venv desta pasta e acha o pacote sozinho, de qualquer
rem pasta em que for chamado: nao precisa ativar o venv nem definir PYTHONPATH.
rem Para chamar de qualquer pasta, rode uma vez o instalar_comando.ps1.
rem O arquivo e so ASCII de proposito, como o preparar_windows.ps1.
setlocal
set "RAIZ=%~dp0"
set "PYTHONPATH=%RAIZ%"
set "PYTHONIOENCODING=utf-8"
rem Sem isto, o Python poria a pasta atual, que e a do projeto analisado, na
rem frente das bibliotecas: um json.py do projeto rodaria no lugar do json.
set "PYTHONSAFEPATH=1"
if not exist "%RAIZ%.venv\Scripts\python.exe" goto sem_ambiente
"%RAIZ%.venv\Scripts\python.exe" -m analisador %*
exit /b %ERRORLEVEL%

:sem_ambiente
echo Erro: o ambiente .venv nao foi encontrado em %RAIZ%
echo Rode primeiro: powershell -ExecutionPolicy Bypass -File "%RAIZ%preparar_windows.ps1"
exit /b 5
