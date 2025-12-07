# 💬 Chat AI Multi-Agent (Docker + Gemini) 
 
Acest proiect folosește Docker pentru a rula un server Python care gestionează conexiunile de tip chat și interacțiunile cu modelul Gemini de la Google. Aplicația client rulează local (Windows/Linux) folosind Tkinter. 
 
## Configurare Server (Linux/lnxserver) 
 
1. **Clonare Repozitoriu:** 
   ```bash 
   # Navighează la directorul dorit 
   git clone [URL-ul repo-ului tău] lsi/server 
   cd lsi/server 
   ``` 
 
2. **Fișierul .env:** 
   Creează fișierul .env în acest director și adaugă cheia ta API Gemini: 
   ```bash 
   nano .env 
   # Adaugă linia: 
   # GEMINI_API_KEY=AIzaSy...CHEIA_TA_AICI 
   ``` 
 
3. **Instalare și Pornire Docker Compose:** 
   ```bash 
   # Reconstruiește imaginea Docker (pentru a include server.py actualizat) 
   docker-compose build 
 
   # Pornește serverul în fundal 
   docker-compose up -d 
 
   # Verifică log-urile pentru a confirma că modelul a fost selectat 
   docker-compose logs -f 
   ``` 
 
## Configurare Client (Windows/Local) 
 
1. **Instalare Dependințe:** 
   Asigură-te că ai instalat Python 3 și librăriile necesare: 
   ```bash 
   pip install google-generativeai # Dacă vrei să rulezi serverul local 
   # Tkinter este inclus în instalarea standard Python pe Windows/macOS. 
   ``` 
 
2. **Rulare Client:** 
   Rulează fișierul client.py direct: 
   ```bash 
   python client.py 
   ``` 
   *Notă: Modifică variabila HOST din client.py la **192.168.1.254** pentru testare locală sau **iulianddd.ddns.net** pentru acces extern.* 
 
## Troubleshooting Comun 
 
* **EROARE: Variabila de mediu GEMINI_API_KEY nu este setata!** 
    * Verifică dacă fișierul .env există și are formatul corect (GEMINI_API_KEY=...). 
    * Asigură-te că env_file: .env este în docker-compose.yml. 
* **Nu mă pot conecta la server!** 
    * Verifică dacă portul **5555** este Forwardat în router către IP-ul serverului Docker (192.168.1.254). 
    * Verifică statusul containerului cu docker ps. 
 
