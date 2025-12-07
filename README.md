Iată versiunea completă a fișierului README.md, actualizată cu toate funcționalitățile (AI local, Docker, CI/CD), dar formatată într-un stil academic/profesional, fără emoticoane sau iconițe, așa cum ai cerut.

Copiaza conținutul de mai jos în fișierul README.md din repository-ul tău.

Markdown

# AI-Enhanced Team Chat (Proiect LSI)

O platformă de comunicare în timp real, bazată pe arhitectură Client-Server (TCP Sockets), care integrează un Agent Inteligent local pentru asistență tehnică și moderare a discuției. Proiectul este containerizat folosind Docker și utilizează modelul Llama 3 (via Ollama) pentru generarea răspunsurilor, asigurând confidențialitatea datelor.

## Arhitectura Sistemului

Sistemul este compus din trei entități principale interconectate:

1.  **Clientul (Python/Tkinter):** Interfața grafică utilizată de membrii echipei. Se conectează la server prin TCP.
2.  **Serverul (Python/Docker):** Gestionează conexiunile, difuzează mesajele (broadcasting) și integrează logica AI.
3.  **Modulul AI (Ollama):** Un serviciu care rulează modelul Llama 3 local și comunică cu serverul prin HTTP.

### Diagrama de Flux

```mermaid
graph TD
    Client["Client Desktop"] -->|TCP Socket :5555| Server["Container Server Python"]
    Server -->|HTTP Request| Ollama["Container Ollama (Llama 3)"]
    Ollama -->|AI Response| Server
    Server -->|Broadcast| Client
    Script["Script Auto-Deploy"] -->|Git Pull| GitHub["Repository GitHub (Main)"]
Structura Proiectului
client/

client.py - Aplicația client cu interfață grafică.

server/

server.py - Codul sursă al serverului (include clasa LLMParticipant).

Dockerfile - Configurația pentru construirea imaginii Docker a serverului.

docker-compose.yml - Orchestrarea serviciilor (Server + Ollama).

auto_deploy.sh - Script pentru actualizarea automată a serverului din GitHub.

requirements.txt - Lista dependențelor Python necesare.

.env.example - Model pentru variabilele de mediu.

Cerinte de Sistem
Server: Ubuntu (sau altă distribuție Linux) cu Docker și Docker Compose instalate. Minim 8GB RAM recomandat pentru rularea modelului AI.

Client: Orice sistem de operare (Windows, Linux, macOS) cu Python 3.9+ instalat.

Ghid de Instalare si Configurare
1. Configurare Server (Productie)
Urmați acești pași pe serverul unde va rula aplicația:

Creați fișierul .env în rădăcina proiectului și adăugați următoarele configurații:

Ini, TOML

HOST=0.0.0.0
PORT=5555
OLLAMA_HOST=http://ollama:11434/v1
Porniți serviciile folosind Docker Compose:

Bash

docker-compose -f server/docker-compose.yml up -d --build
Descărcați modelul AI (această comandă se execută o singură dată):

Bash

docker exec -it ollama_backend ollama pull llama3
2. Configurare Client (Local)
Pentru a rula aplicația de chat pe stația de lucru locală:

Clonați repository-ul.

Deschideți fișierul client/client.py.

Modificați variabila IP_SERVER:

Utilizați iulianddd.ddns.net (sau IP-ul serverului) pentru conectare remote.

Utilizați 127.0.0.1 doar pentru testare locală.

Rulați clientul:

Bash

python client/client.py
Functionarea Agentului AI
Serverul include o clasă specializată LLMParticipant care gestionează interacțiunea cu modelul de limbaj.

Comportament:

Raspuns la comanda: Dacă un mesaj conține cuvântul "AI" sau "@AI", agentul va analiza ultimele mesaje din context și va răspunde.

Monitorizare liniste: Un thread separat verifică timpul scurs de la ultimul mesaj. Dacă trec 60 de secunde fără activitate, AI-ul va genera automat o întrebare tehnică sau un subiect de discuție pentru a stimula conversația.

Fluxul de Lucru (Git Workflow)
Pentru menținerea stabilității mediului de producție, se impun următoarele reguli:

Branch-ul Main: Este protejat. Codul din main este cel care rulează activ pe server.

Dezvoltare: Orice modificare se face pe un branch separat (ex: feature-nume-functionalitate).

Deployment: Actualizarea serverului se face automat (prin scriptul auto_deploy.sh) sau manual după ce modificările au fost integrate în main prin Pull Request.

Comenzi Utile
Vizualizare log-uri server: docker logs -f python_chat_server

Vizualizare log-uri AI: docker logs -f ollama_backend

Actualizare manuală server: ./auto_deploy.sh

Oprire servicii: docker-compose down