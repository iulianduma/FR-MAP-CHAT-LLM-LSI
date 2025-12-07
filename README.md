# FR-MAP-CHAT-LLM-LSI / AI-Enhanced Team Chat (LSI Project)

> O platformă de comunicare în timp real, asistată de un Agent AI local, construită pe arhitectură TCP Socket și Docker.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![AI](https://img.shields.io/badge/AI-Ollama%20(Llama3)-orange)
![Status](https://img.shields.io/badge/Status-Active%20Development-green)

## Despre Proiect

Acest proiect nu este doar un simplu chat. Este un experiment de integrare a unui **LLM (Large Language Model)** într-un flux de conversație TCP clasic. 

Sistemul include un "participant" virtual (**AI-Lead**) care:
1.  **Monitorează discuția:** Oferă sfaturi tehnice la cerere.
2.  **Previne liniștea:** Dacă nimeni nu scrie timp de X secunde, AI-ul generează automat un subiect de discuție relevant.
3.  **Rulează Local:** Folosește `Ollama` și modelul `Llama 3`, asigurând confidențialitatea datelor (niciun mesaj nu părăsește serverul).

##  Arhitectură

Sistemul este împărțit în containere Docker pentru izolare și scalabilitate:

```mermaid
graph TD
    Client["Client Desktop (Tkinter)"] -->|TCP Socket :5555| Server["Python Server Container"]
    Server -->|HTTP Request| Ollama["Ollama Container (Llama 3)"]
    Ollama -->|AI Response| Server
    Server -->|Broadcast| Client
    Cron["Auto-Deploy Script"] -->|Git Pull| GitHub["GitHub Repo (Main)"]
	
##  Structura Proiectului

FR-MAP-CHAT-LLM-LSI/
├── client/
│   └── client.py          # Interfața Grafică (rulează la utilizator)
├── server/
│   ├── Dockerfile         # Configurare imagine Python
│   ├── docker-compose.yml # Orchestare (Server + Ollama)
│   └── server.py          # Logică TCP + Integrare AI
├── auto_deploy.sh         # Script de actualizare automată (CI/CD)
├── .env.example           # Model variabile de mediu
└── README.md              # Documentație




##  Ghid de Instalare

1. Pentru Developeri (Clientul)
Dacă vrei doar să te conectezi la chat:

Clonează proiectul:

Bash

git clone [https://github.com/iulianduma/FR-MAP-CHAT-LLM-LSI.git](https://github.com/iulianduma/FR-MAP-CHAT-LLM-LSI.git)
cd FR-MAP-CHAT-LLM-LSI/client
Configurează: Deschide client.py și editează linia IP_SERVER:

iulianduma.ddns.net (pentru conectare la serverul echipei)

127.0.0.1 (dacă testezi serverul local)

Rulează:

Bash

python client.py
2. Pentru Server (Administrator)
Pașii necesari pe serverul Ubuntu de producție:

Configurare Mediu: Creează un fișier .env bazat pe exemplul oferit:

Ini, TOML

HOST=0.0.0.0
PORT=5555
OLLAMA_HOST=http://ollama:11434
Pornire Servicii:

Bash

docker-compose up -d --build
Inițializare AI (Doar prima dată): Trebuie descărcat modelul Llama 3 în containerul Ollama:

Bash

docker exec -it ollama_backend ollama pull llama3
  
  Cum funcționează AI-ul?
Clasa LLMParticipant din server acționează ca un wrapper peste API-ul Ollama.

Trigger de Răspuns: Dacă menționezi "AI" sau "ajutor", botul va prelua contextul (ultimele 10 mesaje) și va răspunde.

Trigger de Liniște: Un thread separat (silence_watchdog) numără secundele de la ultimul mesaj. Dacă depășește limita (ex: 60 sec), cere LLM-ului o întrebare de "spargere a gheții".

 Reguli de Contribuție (Git Workflow)
Pentru a nu strica versiunea de producție (care se actualizează automat), respectați regulile:

 NU lucra pe main. Branch-ul main este protejat și rulează live pe server.

Creează un branch pentru orice modificare:

Bash

git checkout -b feature-numele-tau
Testează local codul.

Fă Push și deschide un Pull Request pe GitHub.

După aprobare și Merge, serverul își va face update singur în ~5 minute.

️ Comenzi Utile (Server)
Vezi logurile serverului: docker logs -f python_chat_server

Vezi logurile AI: docker logs -f ollama_backend

Restart forțat: docker-compose restart

Update manual: ./auto_deploy.sh

Proiect realizat pentru Laboratorul de Sisteme Inteligente.