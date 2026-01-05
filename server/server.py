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
SILENCE_THRESHOLD = 60  # NOU: Perioada marita de la 30s la 60s

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("EROARE: Variabila de mediu GEMINI_API_KEY nu este setata!")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# --- VARIABILE GLOBALE DE STARE ---
ACTIVE_MODEL_NAME = ""
clients = []
last_message_time = time.time()
conversation_history = []
HISTORY_LIMIT = 30
is_ai_active = True

# NOUA LISTA DE PROMPTS
PROMPTS = {
    "Mediator Comic": "Ești un mediator de echipa cu simțul umorului. Răspunde la întrebările echipei, analizează problemele și oferă soluții, dar cu o notă de umor fin și auto-deriziune. Folosește limbaj prietenos. Dacă subiectul este trivial, intervii cu o glumă. Dacă subiectul este serios, tratează-l serios, dar încheie cu o remarcă amuzantă.",
    "Receptor (Analist)": "Ești un receptor pasiv. Doar urmărești conversația și intervii doar când ești etichetat direct sau când discuția stagnează (SILENCE_DETECTED). Oferă rezumate concise, nu soluții proactive.",
    "Expert Juridic": "Ești un expert juridic specializat în dreptul corporatist și GDPR. Răspunde punctual la întrebările legale, identificând riscurile. NU interveni pe subiecte non-legale.",
    "Evaluator Proiecte": "Ești un evaluator care se concentrează pe buget, resurse și rentabilitate (ROI). Intervine pe orice subiect care afectează planificarea, costurile sau termenele proiectului.",
    "Expert HR": "Ești Manager HR. Menirea ta este să menții armonia echipei. Intervine la semne de conflict, burnout sau întrebări legate de proceduri interne și etică.",
    "Business Analist (BA)": "Ești un Business Analyst. Sarcina ta este să te asiguri că soluțiile tehnice propuse se aliniază cu obiectivele de business. Intervine dacă o soluție deviază de la nevoia inițială sau dacă specificatiile sunt neclare.",
    "Expert Logistică": "Ești un specialist în optimizarea lanțurilor de aprovizionare și a fluxurilor de resurse. Intervine pe subiecte legate de eficiență, stocuri, transport sau resurse fizice."
}

# Inițializarea prompt-ului la nivel global (DEFAULT: Mediator Comic)
current_prompt_key = "Mediator Comic"
active_system_instruction = PROMPTS[current_prompt_key]


def pick_best_model():
    """Alege cel mai bun model disponibil pentru chat."""
    global ACTIVE_MODEL_NAME
    print("--- Cautare modele disponibile ---")
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        priority_list = ["models/gemini-2.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]
        chosen = next((priority for priority in priority_list if priority in available_models), None)

        if not chosen and available_models:
            chosen = next((m for m in available_models if "flash" in m.lower()), None)

        if not chosen and available_models:
            chosen = available_models[0]

        if chosen:
            ACTIVE_MODEL_NAME = chosen
            print(f"SUCCESS: Model selectat automat: {ACTIVE_MODEL_NAME}")
        else:
            print("CRITIC: Nu s-a gasit niciun model compatibil!")
            sys.exit(1)

    except Exception as e:
        print(f"Eroare la listarea modelelor: {e}")
        ACTIVE_MODEL_NAME = "models/gemini-2.5-flash"
        print(f"Se incearca fallback fortat la: {ACTIVE_MODEL_NAME}")


def call_gemini(messages_history, trigger_msg=None):
    """Apeleaza API-ul Gemini cu istoric si instructiuni de sistem."""
    try:
        model = genai.GenerativeModel(
            model_name=ACTIVE_MODEL_NAME,
            system_instruction=active_system_instruction
        )
        gemini_history = [{"role": "user", "parts": [msg]} for msg in messages_history]
        chat = model.start_chat(history=gemini_history)
        prompt_to_send = trigger_msg if trigger_msg else "Analizează contextul. Răspunde conform rolului."
        response = chat.send_message(prompt_to_send)
        return response.text.strip()
    except Exception as e:
        print(f"Eroare API Gemini: {e}")
        return "PASS"


def get_ai_decision(trigger_type="review", explicit_msg=None):
    """Decide daca AI trebuie sa intervina."""
    global conversation_history
    if not is_ai_active:
        return None

    context_msgs = conversation_history[-HISTORY_LIMIT:]

    trigger_text = explicit_msg
    if trigger_type == "silence":
        trigger_text = "[SILENCE_DETECTED] - Discuția a murit. Propune o direcție nouă."

    ai_raw_text = call_gemini(context_msgs, trigger_msg=trigger_text)
    clean_text = ai_raw_text.strip().upper()

    if clean_text == "PASS" or clean_text == "PASS.":
        print(f"Gemini ({current_prompt_key}) -> PASS")
        return None

    if len(clean_text) > 4:
        return ai_raw_text

    return None


def broadcast(message, is_binary=False):
    """Trimite mesaj la toti clientii conectati."""
    if not is_binary:
        message = message.encode('utf-8')
    for client in clients:
        try:
            client.send(message)
        except:
            if client in clients:
                clients.remove(client)


def silence_watchdog():
    """Verifica periodic linistea in chat si declanseaza AI-ul."""
    global last_message_time
    print("Watchdog pornit.")
    while True:
        time.sleep(5)
        if not is_ai_active:
            last_message_time = time.time()
            continue

        if time.time() - last_message_time > SILENCE_THRESHOLD:
            print("Liniște detectată...")
            response = get_ai_decision(trigger_type="silence")
            if response:
                last_message_time = time.time()
                broadcast(f"AI ({current_prompt_key}): {response}")
            else:
                # Resetam timpul de liniste cu 10s mai putin decat pragul pentru a forta o verificare rapida daca nu a intervenit
                last_message_time = time.time() - (SILENCE_THRESHOLD - 10)


def handle_client(client, client_address):
    """Gestioneaza comunicarea cu un client."""
    global last_message_time, active_system_instruction, current_prompt_key, HISTORY_LIMIT, conversation_history, is_ai_active

    client_ip = client_address[0]

    while True:
        try:
            message = client.recv(BUFFER_SIZE)
            if not message: break

            decoded_msg = message.decode('utf-8')
            last_message_time = time.time()

            if decoded_msg.startswith("CFG:"):
                parts = decoded_msg.split(":")

                if parts[1] == "PERS" and parts[2] in PROMPTS:
                    current_prompt_key = parts[2]
                    active_system_instruction = PROMPTS[parts[2]]
                    conversation_history = []
                    broadcast(f"SYS:PERSONALITATE SCHIMBATA ÎN: {current_prompt_key} (Istoric resetat)")

                elif parts[1] == "CACHE":
                    try:
                        new_limit = int(parts[2])
                        HISTORY_LIMIT = new_limit
                        broadcast(f"SYS:LIMITA ISTORIC SETATĂ LA: {HISTORY_LIMIT}")
                    except:
                        pass

                elif parts[1] == "AISTATE":
                    if parts[2] == "ON":
                        is_ai_active = True
                        broadcast(f"SYS:Agentul AI a fost ACTIVAT de catre un utilizator.")
                    else:
                        is_ai_active = False
                        broadcast(f"SYS:Agentul AI a fost OPRIT de catre un utilizator.")

                elif parts[1] == "WORDS":
                    broadcast(f"SYS:LIMITA CUVINTE AI SETATĂ LA: {parts[2]}")

            elif decoded_msg.startswith("SYS:JOIN_INFO:"):
                # Interceptam mesajul de join si adaugam IP-ul
                join_info_with_ip = decoded_msg + f"|IP:{client_ip}"

                try:
                    nickname = decoded_msg.split(':')[2].split('|')[0]
                    broadcast(f"SYS:{nickname} s-a alaturat chat-ului.")
                except:
                    pass

                # Propagam mesajul de info tehnic COMPLET (inclusiv IP)
                broadcast(join_info_with_ip)

            else:
                # Mesaj normal (nu CFG)
                broadcast(message, is_binary=True)

                conversation_history.append(decoded_msg)
                if len(conversation_history) > HISTORY_LIMIT: conversation_history.pop(0)

                if not decoded_msg.startswith("SYS:") and "AI (" not in decoded_msg:
                    if is_ai_active:
                        # NOU: Verificarea finala a starii AI trebuie sa fie in run_ai_review
                        threading.Thread(target=run_ai_review, args=(decoded_msg,)).start()
        except:
            if client in clients: clients.remove(client)
            client.close()
            break


def run_ai_review(latest_msg):
    """Ruleaza decizia AI pe un thread separat, verificand starea finala."""
    global is_ai_active, current_prompt_key

    # Verificam starea AI inainte de a incepe procesarea
    if not is_ai_active:
        return

    response = get_ai_decision(trigger_type="review", explicit_msg=latest_msg)

    # Verificam starea AI imediat inainte de a trimite raspunsul
    if response and is_ai_active:
        broadcast(f"AI ({current_prompt_key}): {response}")


def receive():
    """Porneste serverul si accepta conexiuni."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"SERVER DOCKER PORNIT PE {HOST}:{PORT}")

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

        threading.Thread(target=handle_client, args=(client, address)).start()


if __name__ == "__main__":
    pick_best_model()
    receive()