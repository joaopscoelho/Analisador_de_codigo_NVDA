@echo off
rem Atalho de uma palavra para o analisador (Windows).
rem
rem   analisar                 abre o menu de pastas
rem   analisar pasta\projeto   analisa direto
rem   analisar --explicar      menu e explicacao do modelo
rem
rem Usa o ambiente .venv desta pasta e acha o pacote sozinho, de qualquer
rem pasta em que for chamado: nao precisa ativar o venv nem definir PYTHONPATH.
rem O arquivo e so ASCII de proposito, como o preparar_windows.ps1.
setlocal
set "RAIZ=%~dp0"
set "PYTHONPATH=%RAIZ%"
set "PYTHONIOENCODING=utf-8"
if not exist "%RAIZ%.venv\Scripts\python.exe" goto sem_ambiente
"%RAIZ%.venv\Scripts\python.exe" -m analisador %*
exit /b %ERRORLEVEL%

:sem_ambiente
echo Erro: o ambiente .venv nao foi encontrado em %RAIZ%
echo Rode primeiro: powershell -ExecutionPolicy Bypass -File "%RAIZ%preparar_windows.ps1"
exit /b 5
