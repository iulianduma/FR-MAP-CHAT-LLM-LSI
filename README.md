# FR-MAP-CHAT-LLM-LSI 💬 Python Socket Chat

O aplicație de chat în timp real, multithreaded, construită pe arhitectura Client-Server folosind socket-uri TCP pure. Proiectul este containerizat cu Docker pentru o desfășurare ușoară pe serverul de producție (Ubuntu).

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Status](https://img.shields.io/badge/Status-Active-green)

## 🏗️ Arhitectură

Aplicația este împărțită în două componente principale:
1.  **Serverul:** Gestionează conexiunile și redistribuie mesajele (Broadcasting). Rulează într-un container Docker.
2.  **Clientul:** O interfață grafică (GUI) construită cu Tkinter care se conectează la server.



## 📂 Structura Proiectului

```text
├── client/
│   └── client.py          # Aplicația GUI pentru utilizatori
├── server/
│   ├── Dockerfile         # Configurația imaginii Docker
│   ├── docker-compose.yml # Orchestarea containerului
│   └── server.py          # Logica backend (TCP Socket)
├── .env.example           # Variabile de mediu (model)
├── requirements.txt       # Dependențe Python
└── README.md              # Documentație