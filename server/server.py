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

# --- VARIABILE GLOBALE DE STARE ---
ACTIVE_MODEL_NAME = ""
clients = []
last_message_time = time.time()
conversation_history = []
HISTORY_LIMIT = 30
is_ai_active = True

# --- CONFIGURARE AI ---
PROMPTS = {
    "Expert IT (Cortex)": "Ești Cortex, Arhitect Software Senior. Răspunde direct, precis și tehnic. Dacă subiectul este banal/irelevant, NU interveni. Dacă e o provocare tehnică sau risc, oferă soluții punctuale.",
    "Expert Contabil": "Ești Contabil. Răspunde punctual la întrebări despre contabilitate, taxe sau finanțe. Folosește limbaj specific. Dacă subiectul nu este financiar, NU interveni.",
    "Avocat Corporatist": "Ești Avocat. Oferă informații bazate pe principii juridice generale și legi cunoscute (fără a pretinde consultanță directă, dar oferind context). Dacă subiectul nu este legal, NU interveni.",
    "Project Manager": "Ești PM. Răspunde punctual la întrebări de organizare și management de proiect. Dacă echipa deviază, intervino cerând status sau re-aliniere. La [SILENCE_DETECTED] cere status.",
    "Medic (Consultant)": "Ești Medic. Oferă informații medicale generale și educaționale (NU sfaturi medicale personalizate). Dacă subiectul nu este medical, NU interveni.",
    "Expert CyberSecurity": "Ești Hacker. Scanezi vulnerabilități. Sigur -> PASS. Risc -> ALERTA.",
    "UX/UI Designer": "Ești Designer. Backend -> PASS. Interfață -> INTERVINE.",
    "Data Scientist": "Ești Data Scientist. Opinii -> PASS. Date greșite -> INTERVINE.",
    "HR Manager": "Ești HR. Conflicte -> INTERVINE. Altfel -> PASS.",
    "Marketing Strategist": "Ești Marketing. Produs plictisitor -> INTERVINE. Altfel -> PASS.",
    "Business Analyst": "Ești BA. Soluția nu rezolvă nevoia -> INTERVINE. Altfel -> PASS.",
    "DevOps Engineer": "Ești DevOps. Deploy greu -> INTERVINE. Altfel -> PASS.",
    "Quality Assurance (QA)": "Ești QA. Cauți bug-uri. Altfel -> PASS.",
    "Startup Founder": "Ești Fondator. Vrei viteză ('Ship it!'). Altfel -> PASS.",
    "Profesor Istorie": "Analizezi greșelile istorice. Altfel -> PASS.",
    "Psiholog Organizational": "Analizezi dinamica grupului. Armonie -> PASS.",
    "Investitor VC": "Dacă ideea nu face bani -> INTERVINE. Altfel -> PASS.",
    "Jurnalist Tech": "Ești Jurnalist Tech. Răspunde analitic la întrebări despre piața tehnologică, inovații sau economie IT. Dacă subiectul nu este Tech, NU interveni.",
    "Consultant GDPR": "Date personale -> INTERVINE. Altfel -> PASS."
}

# Inițializarea prompt-ului la nivel global (necesar pentru a evita NameError)
current_prompt_key = "Expert IT (Cortex)"
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

        priority_list = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash",
            "models/gemini-flash-latest",
            "models/gemini-2.5-pro",
            "models/gemini-pro-latest"
        ]
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

        prompt_to_send = trigger_msg if trigger_msg else "Analizează contextul. Răspunde conform rolului (PASS sau intervenție)."
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
    elif trigger_text is None:
        trigger_text = "Review this conversation."

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
                    # Resetarea contextului la schimbarea personalitatii
                    current_prompt_key = parts[2]
                    active_system_instruction = PROMPTS[parts[2]]
                    conversation_history = []  # RESETARE ISTORIC
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
                    # Configurarea limitei de cuvinte (fara a reseta contextul)
                    broadcast(f"SYS:LIMITA CUVINTE AI SETATĂ LA: {parts[2]}")

            elif decoded_msg.startswith("SYS:JOIN_INFO:"):
                # Interceptam mesajul de join si adaugam IP-ul
                join_info_with_ip = decoded_msg + f"|IP:{client_ip}"

                # Extragem nickname-ul pentru notificare
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
                        threading.Thread(target=run_ai_review, args=(decoded_msg,)).start()
        except:
            if client in clients: clients.remove(client)
            client.close()
            break


def run_ai_review(latest_msg):
    """Ruleaza decizia AI pe un thread separat."""
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

        # Trimitem adresa clientului in handle_client
        threading.Thread(target=handle_client, args=(client, address)).start()


if __name__ == "__main__":
    pick_best_model()
    receive()