@echo off
setlocal

:: =======================================================
:: Verificare Instalare Python
:: =======================================================
echo.
echo Verificare instalare Python in variabila de mediu PATH...
python --version 2>nul
if errorlevel 100 set errorlevel=1
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
:: Verificare Librarii
:: =======================================================
echo.
echo Verificare librarii necesare...
echo [ Info ]: Client.py foloseste doar librarii standard (Tkinter, Socket, Threading).
echo [ Info ]: Daca Python functioneaza, librariile sunt disponibile.
echo.

:: =======================================================
:: Rulare Aplicatie
:: =======================================================
echo --------------------------------------------------
echo Totul este in regula. Se ruleaza aplicatia client.py
echo --------------------------------------------------
echo.

:: Rulam client.py din directorul curent.
:: Daca aplicatia se inchide cu succes, scriptul continua.
python client.py

echo.
echo Aplicatia client s-a inchis.
