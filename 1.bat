@echo off
echo Generare README.md complet (cu GitHub si Docker)...

:: 1. Sterge fisierul vechi
del README.md 2>nul

:: 2. Titlu si Descriere Generala
echo # 🚀 FR-MAP-CHAT-LLM-LSI: Chat de Echipa cu Agent LLM Sincronizat > README.md
echo. >> README.md
echo Proiectul implementeaza un sistem de chat multi-utilizator bazat pe socket-uri, echipat cu un Agent LLM (Large Language Model) activ in conversatie. Obiectivul principal este de a sincroniza mediul de lucru al AI-ului (rol, stare, istoric) intre toti clientii si de a oferi o solutie de comunicare stabila, moderna si transparenta. >> README.md
echo. >> README.md
echo Sistemul este proiectat pentru a rula intr-un mediu de productie pe un server Linux, utilizand **Docker** pentru containerizare si un pipeline automatizat de **CI/CD** legat de GitHub. >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 3. Tehnologii
echo ## 🛠️ Tehnologii Utilizate >> README.md
echo. >> README.md
echo ^| Componenta ^| Tehnologie ^| Scop ^| >> README.md
echo ^| :--- ^| :--- ^| :--- ^| >> README.md
echo ^| **Agent LLM** ^| Google Gemini (models/gemini-2.5-flash) ^| Analiza conversatiei, interventie bazata pe rol (Ex: Expert IT, PM, etc.). ^| >> README.md
echo ^| **Interfata Client** ^| Python (Tkinter + **ttkbootstrap**) ^| Interfata grafica moderna, Dark Mode, managementul configuratiei locale. ^| >> README.md
echo ^| **Backend Server** ^| Python (Socket), **Docker** ^| Gateway pentru clienti; sincronizare stare AI; izolare in container. ^| >> README.md
echo ^| **CI/CD** ^| Bash Scripting, Git, Crontab ^| Actualizare automata a codului de pe GitHub la fiecare 5 secunde. ^| >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 4. Structura Fisiere
echo ## 📂 Structura de Fisiere >> README.md
echo. >> README.md
echo ``` >> README.md
echo . >> README.md
echo ^|^| client/ >> README.md
echo ^|^| ^|^| client.py               ^|^| # Codul clientului (GUI si logica retea) >> README.md
echo ^|^| ^|^| install_dependencies.bat ^|^| # Instalare librarii necesare client (Windows) >> README.md
echo ^|^| ^|^| start_client_minimized.bat ^|^| # Rulare client minimizat >> README.md
echo ^|^| server/ >> README.md
echo ^|^| ^|^| server.py               ^|^| # Codul serverului (Socket + AI Logic) >> README.md
echo ^|^| ^|^| Dockerfile              ^|^| # Configuratia imaginii Docker >> README.md
echo ^|^| ^|^| docker-compose.yml      ^|^| # Orchestarea containerelor >> README.md
echo ^|^| DevOps/ >> README.md
echo ^|^| ^|^| auto_deploy.sh          ^|^| # Script verificare GitHub si update Docker >> README.md
echo ^|^| ^|^| restart.sh              ^|^| # Script manual/fortat de restart server >> README.md
echo ^|^| README.md                 ^|^| # Documentatia proiectului >> README.md
echo ``` >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 5. Integrare GitHub & Docker (NOU)
echo ## 🔄 Integrare CI/CD si Docker (Server-Side) >> README.md
echo. >> README.md
echo Proiectul ruleaza pe un server real Linux (`root@lnxserver`), asigurand disponibilitate continua. Arhitectura include un mecanism de **auto-deployment** care sincronizeaza serverul cu repository-ul GitHub. >> README.md
echo. >> README.md
echo ### 1. Auto-Deployment (`auto_deploy.sh`) >> README.md
echo Acest script este inima sistemului CI/CD. Ruleaza automat (via Crontab/Loop) si verifica la fiecare cateva secunde daca au aparut modificari (commit-uri noi) pe branch-ul `main`. >> README.md
echo. >> README.md
echo **Fluxul de executie:** >> README.md
echo 1.  Executa `git fetch` pentru a interoga GitHub. >> README.md
echo 2.  Compara hash-ul commit-ului local cu cel remote (`HEAD` vs `origin/main`). >> README.md
echo 3.  **Daca exista diferente:** >> README.md
echo     * Descarca noul cod (`git pull`). >> README.md
echo     * Reconstruieste containerele Docker (`docker-compose up -d --build`). >> README.md
echo     * Curata imaginile vechi pentru a economisi spatiu (`docker image prune`). >> README.md
echo. >> README.md
echo ### 2. Management Docker (`restart.sh`) >> README.md
echo Un script utilitar folosit pentru a forta repornirea mediului sau pentru mentenanta manuala. Acesta asigura ca folderul proiectului exista, apeleaza optional `auto_deploy.sh` si apoi reconstruieste si porneste containerele in modul *detached*. >> README.md
echo. >> README.md
echo ```bash >> README.md
echo # Exemplu rulare manuala pe server: >> README.md
echo ./restart.sh >> README.md
echo ``` >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 6. Rulare Client
echo ## 🚀 Rulare Client (Windows) >> README.md
echo. >> README.md
echo 1.  **Instalare Dependente:** >> README.md
echo     Executati `client/install_dependencies.bat` pentru a instala `ttkbootstrap` si `psutil`. >> README.md
echo. >> README.md
echo 2.  **Pornire Aplicatie:** >> README.md
echo     Executati `client/start_client_minimized.bat`. Aplicatia se va deschide, cerand numele de utilizator. >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 7. Functionalitati Detaliate
echo ## 🎯 Functionalitati Cheie >> README.md
echo. >> README.md
echo ### A. Agent AI Contextual >> README.md
echo * **Sincronizare:** Schimbarea rolului AI (ex: din "Expert IT" in "Avocat") de catre un utilizator actualizeaza instantaneu contextul pentru toata echipa. >> README.md
echo * **Resetare Memorie:** La schimbarea rolului, istoricul AI-ului este sters automat pentru a evita "halucinatiile" cauzate de contextul anterior. >> README.md
echo. >> README.md
echo ### B. Interfata Moderna (ttkbootstrap) >> README.md
echo * **Tematica:** Suport pentru teme multiple (Darkly, Cosmo, Superhero etc.) selectabile din UI. >> README.md
echo * **Emoticoane:** Panou dedicat pentru inserarea rapida a emoji-urilor. >> README.md
echo * **Logs:** Posibilitatea de a salva conversatia local intr-un fisier `.txt`. >> README.md
echo. >> README.md
echo ### C. Transparenta Tehnica >> README.md
echo La conectare, serverul preia informatiile hardware ale clientului (CPU, RAM, OS) si IP-ul public, afisandu-le discret in chat. Acest lucru ajuta la debugging rapid in echipa (ex: "Problema apare doar pe Windows 10 cu RAM putin"). >> README.md

echo.
echo Generare README.md finalizata cu succes!
pause