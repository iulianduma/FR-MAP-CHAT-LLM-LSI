#  FR-MAP-CHAT-LLM-LSI: Chat de Echipa cu Agent LLM Sincronizat 
 
Proiectul implementeaza un sistem de chat multi-utilizator bazat pe socket-uri, echipat cu un Agent LLM (Large Language Model) activ in conversatie. Obiectivul principal este de a sincroniza mediul de lucru al AI-ului (rol, stare, istoric) intre toti clientii si de a oferi o solutie de comunicare stabila, moderna si transparenta. 
 
Sistemul este proiectat pentru a rula intr-un mediu de productie pe un server Linux, utilizand **Docker** pentru containerizare si un pipeline automatizat de **CI/CD** legat de GitHub. 
 
--- 
 
##️ Tehnologii Utilizate 
 
| Componenta | Tehnologie | Scop | 
| :--- | :--- | :--- | 
| **Agent LLM** | Google Gemini (models/gemini-2.5-flash) | Analiza conversatiei, interventie bazata pe rol (Ex: Expert IT, PM, etc.). | 
| **Interfata Client** | Python (Tkinter + **ttkbootstrap**) | Interfata grafica moderna, Dark Mode, managementul configuratiei locale. | 
| **Backend Server** | Python (Socket), **Docker** | Gateway pentru clienti; sincronizare stare AI; izolare in container. | 
| **CI/CD** | Bash Scripting, Git, Crontab | Actualizare automata a codului de pe GitHub la fiecare 5 secunde. | 
 
--- 
 
## Structura de Fisiere 
 
``` 
. 
|| client/ 
|| || client.py               || # Codul clientului (GUI si logica retea) 
|| || install_dependencies.bat || # Instalare librarii necesare client (Windows) 
|| || start_client_minimized.bat || # Rulare client minimizat 
|| server/ 
|| || server.py               || # Codul serverului (Socket + AI Logic) 
|| || Dockerfile              || # Configuratia imaginii Docker 
|| || docker-compose.yml      || # Orchestarea containerelor 
|| DevOps/ 
|| || auto_deploy.sh          || # Script verificare GitHub si update Docker 
|| || restart.sh              || # Script manual/fortat de restart server 
|| README.md                 || # Documentatia proiectului 
``` 
 
--- 
 
##  Integrare CI/CD si Docker (Server-Side) 
 
Proiectul ruleaza pe un server real Linux (`root@lnxserver`), asigurand disponibilitate continua. Arhitectura include un mecanism de **auto-deployment** care sincronizeaza serverul cu repository-ul GitHub. 
 
### 1. Auto-Deployment (`auto_deploy.sh`) 
Acest script este inima sistemului CI/CD. Ruleaza automat (via Crontab/Loop) si verifica la fiecare cateva secunde daca au aparut modificari (commit-uri noi) pe branch-ul `main`. 
 
**Fluxul de executie:** 
1.  Executa `git fetch` pentru a interoga GitHub. 
2.  Compara hash-ul commit-ului local cu cel remote (`HEAD` vs `origin/main`). 
3.  **Daca exista diferente:** 
    * Descarca noul cod (`git pull`). 
    * Reconstruieste containerele Docker (`docker-compose up -d --build`). 
    * Curata imaginile vechi pentru a economisi spatiu (`docker image prune`). 
 
### 2. Management Docker (`restart.sh`) 
Un script utilitar folosit pentru a forta repornirea mediului sau pentru mentenanta manuala. Acesta asigura ca folderul proiectului exista, apeleaza optional `auto_deploy.sh` si apoi reconstruieste si porneste containerele in modul *detached*. 
 
```bash 
# Exemplu rulare manuala pe server: 
./restart.sh 
``` 
 
--- 
 
##  Rulare Client (Windows) 
 
1.  **Instalare Dependente:** 
    Executati `client/setup.bat` pentru a instala `ttkbootstrap` si `psutil`. 
 
2.  **Pornire Aplicatie:** 
    Executati `client/client.bat`. Aplicatia se va deschide, cerand numele de utilizator. 
 
--- 
 
##  Functionalitati Cheie 
 
### A. Agent AI Contextual 
* **Sincronizare:** Schimbarea rolului AI (ex: din "Expert IT" in "Avocat") de catre un utilizator actualizeaza instantaneu contextul pentru toata echipa. 
* **Resetare Memorie:** La schimbarea rolului, istoricul AI-ului este sters automat pentru a evita "halucinatiile" cauzate de contextul anterior. 
 
### B. Interfata Moderna (ttkbootstrap) 
* **Tematica:** Suport pentru teme multiple (Darkly, Cosmo, Superhero etc.) selectabile din UI. 
* **Emoticoane:** Panou dedicat pentru inserarea rapida a emoji-urilor. 
* **Logs:** Posibilitatea de a salva conversatia local intr-un fisier `.txt`. 
 
### C. Transparenta Tehnica 
La conectare, serverul preia informatiile hardware ale clientului (CPU, RAM, OS) si IP-ul public, afisandu-le discret in chat. Acest lucru ajuta la debugging rapid in echipa (ex: "Problema apare doar pe Windows 10 cu RAM putin"). 
