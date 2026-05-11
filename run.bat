@echo off
setlocal

echo Vertex Asset — dashboard fundos (Streamlit)
echo.

cd /d "%~dp0"
if errorlevel 1 (
  echo ERRO: diretorio do projeto inacessivel.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Criando .venv...
  python -m venv .venv
  if errorlevel 1 (
    echo ERRO: falha ao criar venv.
    pause
    exit /b 1
  )
)

echo Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERRO: pip install falhou.
  pause
  exit /b 1
)

set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
set "RCAP_DEMO=1"

echo.
echo Streamlit (RCAP_DEMO=1, dados em demo_data^)
echo.
".venv\Scripts\python.exe" -m streamlit run app.py

pause
endlocal
