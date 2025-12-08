@echo off
ECHO # 💬 Proiect Chat Multi-Agent cu Intervenție AI > README.md
ECHO. >> README.md
ECHO Proiectul implementează un sistem de chat în timp real cu o componentă AI multi-agent activă, bazat pe o arhitectură Client-Server și rulat prin Docker. >> README.md
ECHO. >> README.md
ECHO ## 🌟 Arhitectură și Tehnologii >> README.md
ECHO. >> README.md
ECHO ^| Componentă ^| Tehnologie Principală ^| Responsabilitate ^| >> README.md
ECHO ^| :--- ^| :--- ^| :--- ^| >> README.md
ECHO ^| **Backend AI** ^| Google Gemini API ^| Logică de intervenție contextuală (filtrul `PASS`, limită de cuvinte, logica de pauză). ^| >> README.md
ECHO ^| **Server** ^| Python Sockets, Docker Compose ^| Gestiunea conexiunilor TCP, broadcast, stocarea istoricului de conversație (`last_authors`). ^| >> README.md
ECHO ^| **Frontend** ^| Python Tkinter (Standard) ^| Interfața grafică, sincronizarea stării (`Istoric Mesaje`, `Rol AI`) între clienți. ^| >> README.md
ECHO ^| **Styling** ^| Tkinter `tag_config` ^| Aplicarea dinamică a culorilor pastelate unice pentru fiecare utilizator. ^| >> README.md
ECHO. >> README.md
ECHO ## 📁 Structura Fişierelor >> README.md
ECHO. >> README.md
ECHO ```bash >> README.md
ECHO FR-MAP-CHAT-LLM-LSI/ >> README.md
ECHO ├── client/ >> README.md
ECHO │   ├── client.py           # Aplicația GUI (Interfața) >> README.md
ECHO │   └── run_client.bat      # Script de lansare Windows >> README.md
ECHO ├── server/ >> README.md
ECHO │   ├── server.py           # Logica serverului și handler-ul Gemini >> README.md
ECHO │   ├── docker-compose.yml  # Configurația serviciului Docker >> README.md
ECHO │   ├── .env                # Variabila GEMINI_API_KEY >> README.md
ECHO │   └── Dockerfile          # Instrucțiuni de build (imagine Python) >> README.md
ECHO └── generate_readme.bat     # Scriptul care generează acest fișier >> README.md
ECHO ``` >> README.md
ECHO. >> README.md
ECHO ## 🚀 Instalare și Rulare >> README.md
ECHO. >> README.md
ECHO ### 1. Configurare Server (Linux / Docker) >> README.md
ECHO. >> README.md
ECHO 1. **Navigare și Fișier `.env`:** Navigați în directorul `server/` și creați fișierul `.env` cu cheia API: >> README.md
ECHO    ```bash >> README.md
ECHO    cd server/ >> README.md
ECHO    nano .env >> README.md
ECHO    # Adăugați: GEMINI_API_KEY=AIzaSy...CHEIA_TA_AICI >> README.md
ECHO    ``` >> README.md
ECHO 2. **Instalare și Build:** Folosiți Docker Compose pentru a construi imaginea și a porni serviciul: >> README.md
ECHO    ```bash >> README.md
ECHO    # Construiește imaginea Python (pentru a include modificările din server.py) >> README.md
ECHO    docker-compose build >> README.md
ECHO. >> README.md
ECHO    # Pornește serverul (Port 5555 mapat) >> README.md
ECHO    docker-compose up -d >> README.md
ECHO. >> README.md
ECHO    # Verifică statusul și log-urile: >> README.md
ECHO    docker-compose logs -f >> README.md
ECHO    ``` >> README.md
ECHO. >> README.md
ECHO ### 2. Configurare Client (Windows / Local) >> README.md
ECHO. >> README.md
ECHO 1. **Instalare Dependințe:** Asigurați-vă că aveți Python 3 instalat. >> README.md
ECHO    ```bash >> README.md
ECHO    pip install google-generativeai >> README.md
ECHO    ``` >> README.md
ECHO 2. **Rulare:** Navigați în directorul `client/` și folosiți scriptul de lansare: >> README.md
ECHO    ```bash >> README.md
ECHO    cd client/ >> README.md
ECHO    run_client.bat >> README.md
ECHO    ``` >> README.md
ECHO. >> README.md
ECHO **README.md a fost generat cu succes!**