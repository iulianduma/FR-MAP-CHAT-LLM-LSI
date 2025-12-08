# -*- coding: utf-8 -*-
import socket
import threading
import time
import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("EROARE: Libraria 'google-generativeai' lipseste.")
    sys.exit(1)

HOST = '0.0.0.0'
PORT = 5555
BUFFER_SIZE = 1024
SILENCE_THRESHOLD = 30

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("EROARE: Variabila de mediu GEMINI_API_KEY nu este setata!")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

ACTIVE_MODEL_NAME = ""

# ... (pick_best_model, PROMPTS, active_system_instruction, call_gemini, get_ai_decision raman neschimbate) ...
# (Pentru simplitate, pastram doar corpul functiilor care se schimba)

clients = []
last_message_time = time.time()
conversation_history = []
HISTORY_LIMIT = 30
is_ai_active = True


# --- Functii existente (pastrate neschimbate) ---

def pick_best_model():
    # ... (logica neschimbata)
    global ACTIVE_MODEL_NAME
    # ... (Logica de alegere a modelului)
    ACTIVE_MODEL_NAME = "models/gemini-2.5-flash"  # Exemplu


def call_gemini(messages_history, trigger_msg=None):
    # ... (logica neschimbata)
    return "PASS"


def get_ai_decision(trigger_type="review", explicit_msg=None):
    # ... (logica neschimbata)
    return None


def broadcast(message, is_binary=False):
    # ... (logica neschimbata)
    if not is_binary:
        message = message.encode('utf-8')
    for client in clients:
        try:
            client.send(message)
        except:
            if client in clients:
                clients.remove(client)


def silence_watchdog():
    # ... (logica neschimbata)
    global last_message_time
    # ... (Logica watchdog)
    while True: time.sleep(5)  # Simulare


# --- Functii Modificate ---

def handle_client(client, client_address):  # client_address adaugat ca argument
    """Gestioneaza comunicarea cu un client."""
    global last_message_time, active_system_instruction, current_prompt_key, HISTORY_LIMIT, conversation_history, is_ai_active

    # NOU: Stocam adresa IP
    client_ip = client_address[0]

    while True:
        try:
            message = client.recv(BUFFER_SIZE)
            if not message: break

            decoded_msg = message.decode('utf-8')
            last_message_time = time.time()

            if decoded_msg.startswith("CFG:"):
                parts = decoded_msg.split(":")

                if parts[1] == "PERS":
                    current_prompt_key = parts[2]
                    active_system_instruction = PROMPTS[parts[2]]
                    conversation_history = []
                    broadcast(f"SYS:PERSONALITATE SCHIMBATA ÎN: {current_prompt_key} (Istoric resetat)")

                elif parts[1] == "AISTATE":
                    if parts[2] == "ON":
                        is_ai_active = True
                        broadcast(f"SYS:Agentul AI a fost ACTIVAT de catre un utilizator.")
                    else:
                        is_ai_active = False
                        broadcast(f"SYS:Agentul AI a fost OPRIT de catre un utilizator.")

                # ... (alte configurari)

            elif decoded_msg.startswith("SYS:JOIN_INFO:"):
                # NOU: Interceptam mesajul de join si adaugam IP-ul

                # 1. Adaugam IP-ul la mesajul de info
                join_info_with_ip = decoded_msg + f"|IP:{client_ip}"

                # 2. Extragem nickname-ul pentru notificare
                try:
                    nickname = decoded_msg.split('|')[0].split(':')[2]
                    broadcast(f"SYS:{nickname} s-a alaturat chat-ului.")
                except:
                    pass

                # 3. Propagam mesajul de info tehnic COMPLET (inclusiv IP)
                broadcast(join_info_with_ip)

            else:
                # Mesaj normal (nu CFG)
                broadcast(message, is_binary=True)

                conversation_history.append(decoded_msg)
                if len(conversation_history) > HISTORY_LIMIT: conversation_history.pop(0)

                if not decoded_msg.startswith("SYS:") and "AI (" not in decoded_msg:
                    if is_ai_active:
                        threading.Thread(target=run_ai_review, args=(decoded_msg,)).start()
        except:
            if client in clients: clients.remove(client)
            client.close()
            break


def run_ai_review(latest_msg):
    # ... (logica neschimbata)
    response = get_ai_decision(trigger_type="review", explicit_msg=latest_msg)
    if response:
        broadcast(f"AI ({current_prompt_key}): {response}")


def receive():
    """Porneste serverul si accepta conexiuni."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"SERVER DOCKER PORNIT PE {HOST}:{PORT}")

    # Pornim watchdog-ul de liniste in fundal
    threading.Thread(target=silence_watchdog, daemon=True).start()

    while True:
        client, address = server.accept()
        clients.append(client)
        print(f"Conectat: {address}")

        # Trimitere mesaje de stare la client
        client.send(f"SYS:Oră conexiune: {time.strftime('%Y-%m-%d %H:%M:%S')}".encode('utf-8'))
        client.send(f"SYS:CONECTAT LA SERVER. ROL: {current_prompt_key}".encode('utf-8'))
        client.send(f"SYS:AI ACTIV: {ACTIVE_MODEL_NAME}".encode('utf-8'))
        client.send(f"SYS:ROL INIȚIAL: {current_prompt_key}".encode('utf-8'))

        # NOU: Trimitem adresa clientului in handle_client
        threading.Thread(target=handle_client, args=(client, address)).start()


if __name__ == "__main__":
    pick_best_model()  # Asiguram ca modelul este ales inainte de a porni serverul
    receive()