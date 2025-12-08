@echo off
setlocal

:: =======================================================
:: Verificare Instalare Python
:: =======================================================
echo.
echo Verificare instalare Python in variabila de mediu PATH...
python --version 2>nul
if errorlevel 9009 set errorlevel=1
if errorlevel 1 (
    echo.
    echo [ EROARE FATALA ]: Python nu a fost gasit in PATH.
    echo.
    echo Actiuni necesare:
    echo 1. Asigura-te ca Python 3 este instalat.
    echo 2. Asigura-te ca Python a fost adaugat la variabila de mediu PATH.
    echo Scriptul se inchide.
    echo.
    pause
    goto :EOF
)

:: Afiseaza versiunea gasita
echo SUCCES: Python gasit. Versiunea:
python --version

:: =======================================================
:: Rulare Aplicatie Client (Lansare Minimizata)
:: =======================================================
echo.
echo --------------------------------------------------
echo Se lanseaza client.py. Fereastra terminal va fi minimizata.
echo --------------------------------------------------
echo.

:: Folosim START /MIN pentru a lansa procesul minimizat in bara de activitati.
START /MIN "" python client.py

:: Scriptul se termina.
goto :EOF