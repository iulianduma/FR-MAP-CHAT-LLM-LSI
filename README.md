#  Proiect Chat Multi-Agent cu Intervenție AI 
 
Proiectul implementează un sistem de chat în timp real cu o componentă AI multi-agent activă, bazat pe o arhitectură Client-Server și rulat prin Docker. 
 
##  Arhitectură și Tehnologii 
 
| Componentă | Tehnologie Principală | Responsabilitate | 
| :--- | :--- | :--- | 
| **Backend AI** | Google Gemini API | Logică de intervenție contextuală (filtrul `PASS`, limită de cuvinte, logica de pauză). | 
| **Server** | Python Sockets, Docker Compose | Gestiunea conexiunilor TCP, broadcast, stocarea istoricului de conversație (`last_authors`). | 
| **Frontend** | Python Tkinter (Standard) | Interfața grafică, sincronizarea stării (`Istoric Mesaje`, `Rol AI`) între clienți. | 
| **Styling** | Tkinter `tag_config` | Aplicarea dinamică a culorilor pastelate unice pentru fiecare utilizator. | 
 
##  Structura Fişierelor 
 
```bash 
FR-MAP-CHAT-LLM-LSI/ 
├── client/ 
│   ├── client.py           # Aplicația GUI (Interfața) 
│   └── run_client.bat      # Script de lansare Windows 
├── server/ 
│   ├── server.py           # Logica serverului și handler-ul Gemini 
│   ├── docker-compose.yml  # Configurația serviciului Docker 
│   ├── .env                # Variabila GEMINI_API_KEY 
│   └── Dockerfile          # Instrucțiuni de build (imagine Python) 
└── generate_readme.bat     # Scriptul care generează acest fișier 
``` 
 
##  Instalare și Rulare 
 
### 1. Configurare Server (Linux / Docker) 
 
1. **Navigare și Fișier `.env`:** Navigați în directorul `server/` și creați fișierul `.env` cu cheia API: 
   ```bash 
   cd server/ 
   nano .env 
   # Adăugați: GEMINI_API_KEY=AIzaSy...CHEIA_TA_AICI 
   ``` 
2. **Instalare și Build:** Folosiți Docker Compose pentru a construi imaginea și a porni serviciul: 
   ```bash 
   # Construiește imaginea Python (pentru a include modificările din server.py) 
   docker-compose build 
 
   # Pornește serverul (Port 5555 mapat) 
   docker-compose up -d 
 
   # Verifică statusul și log-urile: 
   docker-compose logs -f 
   ``` 
 
### 2. Configurare Client (Windows / Local) 
 
1. **Instalare Dependințe:** Asigurați-vă că aveți Python 3 instalat. 
   ```bash 
   pip install google-generativeai 
   ``` 
2. **Rulare:** Navigați în directorul `client/` și folosiți scriptul de lansare: 
   ```bash 
   cd client/ 
   client.bat 
   ``` 
 
