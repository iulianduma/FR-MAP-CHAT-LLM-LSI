@echo off
echo Pornire clientul chat in fundal (minimizat)...

:: Folosim comanda 'start' cu optiunea /min pentru a rula clientul minimizat.
:: 'pythonw.exe' este folosit in loc de 'python.exe' pentru a ascunde fereastra de consola (CMD) a scriptului.

start /min pythonw client.py

exit /b 0