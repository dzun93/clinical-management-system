@echo off

set "PROYECTO=C:\Proyectos\sistema_gestion_clinica"
set "PYTHON=%PROYECTO%\venv\Scripts\python.exe"
set "LOGS=%PROYECTO%\logs"

if not exist "%LOGS%" mkdir "%LOGS%"

cd /d "%PROYECTO%"

echo. >> "%LOGS%\respaldos.log"
echo ================================================== >> "%LOGS%\respaldos.log"
echo Inicio del respaldo: %date% %time% >> "%LOGS%\respaldos.log"
echo ================================================== >> "%LOGS%\respaldos.log"

"%PYTHON%" manage.py ejecutar_respaldo_automatico >> "%LOGS%\respaldos.log" 2>&1

if errorlevel 1 (
    echo RESULTADO: ERROR >> "%LOGS%\respaldos.log"
) else (
    echo RESULTADO: EXITOSO >> "%LOGS%\respaldos.log"
)

echo Fin del proceso: %date% %time% >> "%LOGS%\respaldos.log"
echo ================================================== >> "%LOGS%\respaldos.log"