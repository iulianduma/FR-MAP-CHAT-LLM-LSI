#  FR-MAP-CHAT-LLM-LSI: Chat de Echipa cu Agent LLM Sincronizat 
 
Proiectul implementeaza un sistem de chat multi-utilizator bazat pe socket-uri, echipat cu un Agent LLM (Large Language Model) activ in conversatie. Obiectivul principal este de a sincroniza mediul de lucru al AI-ului (rol, stare, istoric) intre toti clientii si de a oferi o solutie de comunicare stabila, moderna si transparenta. 
 
--- 
 
## ️ Tehnologii Utilizate 
 
| Componenta | Tehnologie | Scop | 
| :--- | :--- | :--- | 
| **Agent LLM** | Google Gemini (models/gemini-2.5-flash) | Analiza conversatiei, interventie bazata pe rol (Ex: Expert IT, PM, etc.). | 
| **Interfata Client** | Python (Tkinter + **ttkbootstrap**) | Interfata grafica moderna, Dark Mode, managementul configuratiei locale. | 
| **Backend Server** | Python (Socket Programming) | Gateway pentru clienti si API-ul Gemini; sincronizare stare AI si istoric. | 
| **Colectare Info** | `psutil`, `platform` | Colectarea informatiilor hardware (CPU, RAM, OS) ale clientilor la conectare. | 
 
--- 
 
##  Structura de Fisiere 
 
``` 
. 
|| client 
|| || client.py               || # Codul clientului (Interfata grafica si logica de retea) 
|| || install_dependencies.bat || # Script pentru instalarea dependintelor (Client) 
|| || start_client_minimized.bat || # Script pentru rularea clientului (Fara fereastra CMD) 
|| server 
|| || server.py               || # Codul serverului (Gateway API Gemini, Socket Server, Logica AI) 
|| README.md                 || # Acest fisier 
|| ... 
``` 
 
--- 
 
## ️ Cerinte 
 
1.  **Python 3.8+** instalat si adaugat in PATH. 
2.  **Cheie API Gemini:** Variabila de mediu `GEMINI_API_KEY` trebuie setata pe masina care ruleaza `server.py`. 
 
--- 
 
##  Rulare si Comenzi 
 
### 1. Instalarea Dependentelor (Client) 
 
Deschideti un terminal (CMD/PowerShell) in directorul `client/` si rulati: 
 
```bash 
.\install_dependencies.bat 
``` 
 
Acest script va instala automat `ttkbootstrap`, `psutil` si `google-generativeai` (desi ultima este necesara doar pe server, se recomanda instalarea peste tot). 
 
### 2. Pornirea Serverului 
 
Asigurati-va ca aveti setata variabila `GEMINI_API_KEY`! 
Deschideti un terminal in directorul `server/` si rulati: 
 
```bash 
python server.py 
``` 
 
### 3. Pornirea Clientului 
 
Rulati scriptul pentru a porni clientul in modul minimizat (fara fereastra de consola): 
 
```bash 
.\start_client_minimized.bat 
``` 
 
--- 
 
##  Descrierea Detaliata a Proiectului 
 
### A. Sincronizarea Starii AI 
 
Serverul mentine o singura stare globala pentru Agentul LLM (rol, limita de istoric, stare ON/OFF). Toate modificarile facute de **orice** client (ex: schimbarea din "Expert IT" in "Avocat") sunt transmise catre server, care actualizeaza setarile globale si notifica imediat toti ceilalti clienti. Acest lucru asigura ca toti utilizatorii vad aceeasi interventie din partea AI-ului si au aceleasi optiuni de configurare. 
 
### B. Resetarea Contextului 
 
In cazul in care se schimba personalitatea AI-ului (Dropdown "Rol AI"), serverul executa automat o resetare a `conversation_history`. Acest lucru previne ca noul rol (ex: "Avocat") sa fie influentat de subiectele discutate anterior de rolul precedent (ex: "Expert IT"). 
 
### C. Interfata Utilizator (ttkbootstrap) 
 
Interfata grafica a fost modernizata folosind **ttkbootstrap** (tema `darkly`), oferind o estetica moderna si lizibila: 
* **Indentare Inversata:** Mesajele umane (utilizatori) sunt indentate cu 40px pentru a le separa vizual de raspunsurile AI, care folosesc alinierea de baza (fara indentare). 
* **Status Bar Extins:** Bara de stare afiseaza permanent informatii critice despre clientul local (OS, CPU, RAM, GPU) si starea globala a AI-ului (Rol, Model). 
* **Buton AI ON/OFF:** Permite controlul instantaneu asupra Agentului LLM, afectand toti clientii simultan. 
 
### D. Transparenta Hardware 
 
La conectare, fiecare client trimite automat serverului informatiile sale hardware locale (obtinute prin `psutil` si `platform`). Serverul adauga adresa IP a conexiunii si propaga aceste detalii catre toti utilizatorii, imbunatatind transparenta si contextul tehnic in cadrul echipei. 
