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


def pick_best_model():
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

        chosen = None

        for priority in priority_list:
            if priority in available_models:
                chosen = priority
                break

        if not chosen:
            for m in available_models:
                if "flash" in m.lower():
                    chosen = m
                    break

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


pick_best_model()

clients = []
last_message_time = time.time()
conversation_history = []
HISTORY_LIMIT = 30

PROMPTS = {
    "Expert IT (Cortex)": "Ești Cortex, Arhitect Software Senior. Analizezi tehnic. Dacă e banal -> PASS. Dacă e risc -> INTERVINE. La [SILENCE_DETECTED] propui soluții.",
    "Expert Contabil": "Ești Contabil. Dacă nu sunt bani la mijloc -> PASS. Altfel -> INTERVINE.",
    "Avocat Corporatist": "Ești Avocat. Riscuri legale/GDPR -> INTERVINE. Altfel -> PASS.",
    "Project Manager": "Ești PM. Dacă echipa deviază -> INTERVINE. La [SILENCE_DETECTED] cere status.",
    "Medic (Consultant)": "Ești Medic. Doar subiecte medicale -> INTERVINE. Altfel -> PASS.",
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
    "Jurnalist Tech": "Întrebări etice. Altfel -> PASS.",
    "Consultant GDPR": "Date personale -> INTERVINE. Altfel -> PASS.",
    "Expert Logistică": "Eficiență fluxuri. Altfel -> PASS."
}

current_prompt_key = "Expert IT (Cortex)"
active_system_instruction = PROMPTS[current_prompt_key]


def call_gemini(messages_history, trigger_msg=None):
    try:
        model = genai.GenerativeModel(
            model_name=ACTIVE_MODEL_NAME,
            system_instruction=active_system_instruction
        )
        gemini_history = []
        for msg in messages_history:
            gemini_history.append({"role": "user", "parts": [msg]})

        chat = model.start_chat(history=gemini_history)

        prompt_to_send = trigger_msg if trigger_msg else "Analizează contextul. Răspunde conform rolului (PASS sau intervenție)."
        response = chat.send_message(prompt_to_send)
        return response.text.strip()
    except Exception as e:
        print(f"Eroare API Gemini: {e}")
        return "PASS"


def get_ai_decision(trigger_type="review", explicit_msg=None):
    global conversation_history
    context_msgs = conversation_history[-HISTORY_LIMIT:]

    trigger_text = explicit_msg
    if trigger_type == "silence":
        trigger_text = "[SILENCE_DETECTED] - Discuția a murit. Propune o direcție nouă."
    elif trigger_text is None:
        trigger_text = "Review this conversation."

    ai_raw_text = call_gemini(context_msgs, trigger_msg=trigger_text)

    clean_text = ai_raw_text.strip()
    if clean_text.endswith("."): clean_text = clean_text[:-1]

    if clean_text.upper() == "PASS":
        print(f"Gemini ({current_prompt_key}) -> PASS")
        return None
    return ai_raw_text


def broadcast(message, is_binary=False):
    if not is_binary:
        message = message.encode('utf-8')
    for client in clients:
        try:
            client.send(message)
        except:
            if client in clients:
                clients.remove(client)


def silence_watchdog():
    global last_message_time
    print("Watchdog pornit.")
    while True:
        time.sleep(5)
        if time.time() - last_message_time > SILENCE_THRESHOLD:
            print("Liniște detectată...")
            response = get_ai_decision(trigger_type="silence")
            if response:
                last_message_time = time.time()
                broadcast(f"AI ({current_prompt_key}): {response}")
            else:
                last_message_time = time.time() - (SILENCE_THRESHOLD - 10)


def handle_client(client):
    global last_message_time, active_system_instruction, current_prompt_key, BUFFER_SIZE, HISTORY_LIMIT
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
                    broadcast(f"SYS:PERSONALITATE SCHIMBATA IN: {current_prompt_key}")
                elif parts[1] == "BUFF":
                    try:
                        BUFFER_SIZE = int(parts[2])
                        broadcast(f"SYS:BUFFER SERVER SETAT LA: {BUFFER_SIZE}")
                    except:
                        pass
                elif parts[1] == "CACHE":
                    try:
                        new_limit = int(parts[2])
                        HISTORY_LIMIT = new_limit
                        broadcast(f"SYS:LIMITA ISTORIC SETATĂ LA: {HISTORY_LIMIT}")
                    except:
                        pass
            else:
                broadcast(message, is_binary=True)
                conversation_history.append(decoded_msg)
                if len(conversation_history) > HISTORY_LIMIT: conversation_history.pop(0)

                if not decoded_msg.startswith("SYS:") and "AI (" not in decoded_msg:
                    threading.Thread(target=run_ai_review, args=(decoded_msg,)).start()
        except:
            if client in clients: clients.remove(client)
            client.close()
            break


def run_ai_review(latest_msg):
    response = get_ai_decision(trigger_type="review", explicit_msg=latest_msg)
    if response:
        broadcast(f"AI ({current_prompt_key}): {response}")


def receive():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"SERVER DOCKER PORNIT PE {HOST}:{PORT}")
    threading.Thread(target=silence_watchdog, daemon=True).start()
    while True:
        client, address = server.accept()
        clients.append(client)
        print(f"Conectat: {address}")
        client.send(f"SYS:CONECTAT LA SERVER. ROL: {current_prompt_key}".encode('utf-8'))
        client.send(f"SYS:AI ACTIV: {ACTIVE_MODEL_NAME}".encode('utf-8'))
        client.send(f"SYS:ROL INIȚIAL: {current_prompt_key}".encode('utf-8'))
        threading.Thread(target=handle_client, args=(client,)).start()


if __name__ == "__main__":
    receive()