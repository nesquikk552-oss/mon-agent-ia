@echo off
cd /d "%~dp0"

echo Demarrage du serveur de voix...
start "Serveur Voix Christiane" cmd /k "cd clonage_voix && env_voix\Scripts\activate && python serveur_voix.py"

timeout /t 5 /nobreak >nul

echo Demarrage de Christiane...
call env\Scripts\activate
streamlit run interface.py

pause