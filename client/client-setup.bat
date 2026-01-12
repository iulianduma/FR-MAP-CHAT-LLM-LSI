@echo off
echo =======================================================
echo == Instalare Dependente Client Chat (Windows)        ==
echo =======================================================
echo.

:: Verifica daca Python este in PATH.
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo EROARE: Python nu a fost gasit in PATH.
    echo Asigura-te ca Python 3.x este instalat si ca optiunea "Add Python to PATH" a fost bifata la instalare.
    pause
    exit /b 1
)

echo Instalare/Verificare librarii necesare...

:: ttkbootstrap (pentru interfata moderna)
pip install ttkbootstrap
if %errorlevel% neq 0 (
    echo EROARE la instalarea ttkbootstrap. Verifica conexiunea la internet sau permisiunile.
    pause
    exit /b 1
)

:: psutil (pentru informatii despre sistem: RAM/CPU)
pip install psutil
if %errorlevel% neq 0 (
    echo EROARE la instalarea psutil.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo == Instalare reusita! Poti rula clientul.            ==
echo =======================================================
pause