@echo off
echo Generare README.md detaliat...

:: 1. Sterge fisierul vechi (ignora eroarea daca nu exista)
del README.md 2>nul

:: 2. Foloseste > pentru a scrie prima linie (creeaza fisierul)
echo # 🚀 FR-MAP-CHAT-LLM-LSI: Chat de Echipa cu Agent LLM Sincronizat > README.md
echo. >> README.md
echo Proiectul implementeaza un sistem de chat multi-utilizator bazat pe socket-uri, echipat cu un Agent LLM (Large Language Model) activ in conversatie. Obiectivul principal este de a sincroniza mediul de lucru al AI-ului (rol, stare, istoric) intre toti clientii si de a oferi o solutie de comunicare stabila, moderna si transparenta. >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 3. Scrie sectiunea Tehnologii
echo ## 🛠️ Tehnologii Utilizate >> README.md
echo. >> README.md
echo ^| Componenta ^| Tehnologie ^| Scop ^| >> README.md
echo ^| :--- ^| :--- ^| :--- ^| >> README.md
echo ^| **Agent LLM** ^| Google Gemini (models/gemini-2.5-flash) ^| Analiza conversatiei, interventie bazata pe rol (Ex: Expert IT, PM, etc.). ^| >> README.md
echo ^| **Interfata Client** ^| Python (Tkinter + **ttkbootstrap**) ^| Interfata grafica moderna, Dark Mode, managementul configuratiei locale. ^| >> README.md
echo ^| **Backend Server** ^| Python (Socket Programming) ^| Gateway pentru clienti si API-ul Gemini; sincronizare stare AI si istoric. ^| >> README.MD
echo ^| **Colectare Info** ^| `psutil`, `platform` ^| Colectarea informatiilor hardware (CPU, RAM, OS) ale clientilor la conectare. ^| >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 4. Scrie sectiunea Structura de Fisiere
echo ## 📂 Structura de Fisiere >> README.md
echo. >> README.md
echo ``` >> README.md
echo . >> README.md
echo ^|^| client >> README.md
echo ^|^| ^|^| client.py               ^|^| # Codul clientului (Interfata grafica si logica de retea) >> README.md
echo ^|^| ^|^| install_dependencies.bat ^|^| # Script pentru instalarea dependintelor (Client) >> README.md
echo ^|^| ^|^| start_client_minimized.bat ^|^| # Script pentru rularea clientului (Fara fereastra CMD) >> README.md
echo ^|^| server >> README.md
echo ^|^| ^|^| server.py               ^|^| # Codul serverului (Gateway API Gemini, Socket Server, Logica AI) >> README.md
echo ^|^| README.md                 ^|^| # Acest fisier >> README.md
echo ^|^| ... >> README.md
echo ``` >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 5. Scrie sectiunea Cerinte
echo ## ⚙️ Cerinte >> README.md
echo. >> README.md
echo 1.  **Python 3.8+** instalat si adaugat in PATH. >> README.md
echo 2.  **Cheie API Gemini:** Variabila de mediu `GEMINI_API_KEY` trebuie setata pe masina care ruleaza `server.py`. >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 6. Scrie sectiunea Rulare si Comenzi
echo ## 🚀 Rulare si Comenzi >> README.md
echo. >> README.md
echo ### 1. Instalarea Dependentelor (Client) >> README.md
echo. >> README.md
echo Deschideti un terminal (CMD/PowerShell) in directorul `client/` si rulati: >> README.md
echo. >> README.md
echo ```bash >> README.md
echo .\install_dependencies.bat >> README.md
echo ``` >> README.md
echo. >> README.md
echo Acest script va instala automat `ttkbootstrap`, `psutil` si `google-generativeai` (desi ultima este necesara doar pe server, se recomanda instalarea peste tot). >> README.md
echo. >> README.md
echo ### 2. Pornirea Serverului >> README.md
echo. >> README.md
echo Asigurati-va ca aveti setata variabila `GEMINI_API_KEY`! >> README.md
echo Deschideti un terminal in directorul `server/` si rulati: >> README.md
echo. >> README.md
echo ```bash >> README.md
echo python server.py >> README.md
echo ``` >> README.md
echo. >> README.md
echo ### 3. Pornirea Clientului >> README.md
echo. >> README.md
echo Rulati scriptul pentru a porni clientul in modul minimizat (fara fereastra de consola): >> README.md
echo. >> README.md
echo ```bash >> README.md
echo .\start_client_minimized.bat >> README.md
echo ``` >> README.md
echo. >> README.md
echo --- >> README.md
echo. >> README.md

:: 7. Scrie sectiunea Descrierea Detaliata
echo ## 🎯 Descrierea Detaliata a Proiectului >> README.md
echo. >> README.md
echo ### A. Sincronizarea Starii AI >> README.md
echo. >> README.md
echo Serverul mentine o singura stare globala pentru Agentul LLM (rol, limita de istoric, stare ON/OFF). Toate modificarile facute de **orice** client (ex: schimbarea din "Expert IT" in "Avocat") sunt transmise catre server, care actualizeaza setarile globale si notifica imediat toti ceilalti clienti. Acest lucru asigura ca toti utilizatorii vad aceeasi interventie din partea AI-ului si au aceleasi optiuni de configurare. >> README.md
echo. >> README.md
echo ### B. Resetarea Contextului >> README.md
echo. >> README.md
echo In cazul in care se schimba personalitatea AI-ului (Dropdown "Rol AI"), serverul executa automat o resetare a `conversation_history`. Acest lucru previne ca noul rol (ex: "Avocat") sa fie influentat de subiectele discutate anterior de rolul precedent (ex: "Expert IT"). >> README.md
echo. >> README.md
echo ### C. Interfata Utilizator (ttkbootstrap) >> README.md
echo. >> README.md
echo Interfata grafica a fost modernizata folosind **ttkbootstrap** (tema `darkly`), oferind o estetica moderna si lizibila: >> README.md
echo * **Indentare Inversata:** Mesajele umane (utilizatori) sunt indentate cu 40px pentru a le separa vizual de raspunsurile AI, care folosesc alinierea de baza (fara indentare). >> README.md
echo * **Status Bar Extins:** Bara de stare afiseaza permanent informatii critice despre clientul local (OS, CPU, RAM, GPU) si starea globala a AI-ului (Rol, Model). >> README.md
echo * **Buton AI ON/OFF:** Permite controlul instantaneu asupra Agentului LLM, afectand toti clientii simultan. >> README.md
echo. >> README.md
echo ### D. Transparenta Hardware >> README.md
echo. >> README.md
echo La conectare, fiecare client trimite automat serverului informatiile sale hardware locale (obtinute prin `psutil` si `platform`). Serverul adauga adresa IP a conexiunii si propaga aceste detalii catre toti utilizatorii, imbunatatind transparenta si contextul tehnic in cadrul echipei. >> README.md

echo.
echo Generare README.md detaliat finalizata.
pause