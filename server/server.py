# -*- coding: utf-8 -*-
#specificam encodingul fisierului (important pentru caractere speciale in mesaj)
import socket # pentru comunicare TCP intre server si clienti
import threading # pentru fire de executie paralele
import time # pentru lucrul cu timp si pauze
import os # pentru variabile de mediu
import sys # pentru iesirea din program in caz de eroare

# se importa biblioteca Google Gemini AI
try:
    import google.generativeai as genai
except ImportError:
    print("EROARE: Libraria 'google-generativeai' lipseste.")
    sys.exit(1)

# configurare server
HOST = '0.0.0.0' # asculta pe toate adresele IP disponibile
PORT = 5555 # portul pe care serverul accepta conexiuni
BUFFER_SIZE = 1024 #dimensiunea buffer-ului pentru mesaje primite
SILENCE_THRESHOLD = 60  # NOU: Perioada marita de la 30s la 60s. Acestea sunt secunde dupa care AI intervine daca nu mai sunt mesaje

# cheie API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("EROARE: Variabila de mediu GEMINI_API_KEY nu este setata!")
    sys.exit(1)

# configuram biblioteca Gemini cu cheia API. Cheia API spune Google cine suntem si daca avem voie sa folosim serviciul Google. Fara ea, biblioteca nu are dreptul sa trimita cereri catre serverele Google.
genai.configure(api_key=GEMINI_API_KEY)

# --- VARIABILE GLOBALE DE STARE ---
ACTIVE_MODEL_NAME = "" # va fi completat cu modelul AI selectat
clients = [] # lista tuturor clientilor conectati
last_message_time = time.time() # ultimul moment in care s-a primit mesaj
conversation_history = [] # lista ultimelor meesaje
HISTORY_LIMIT = 30 # numarul maxim de mesaje pastrate in istoric
is_ai_active = True # starea AI: activ sau oprit

# NOUA LISTA DE PROMPTS
# Fiecare cheie reprezinta un rol diferit pentru AI, cu instructiuni specifice
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
current_prompt_key = "Mediator Comic" # setam rolul implicit
active_system_instruction = PROMPTS[current_prompt_key]


# Functii AI:
def pick_best_model():
    """Alege cel mai bun model disponibil pentru chat."""
    global ACTIVE_MODEL_NAME
    print("--- Cautare modele disponibile ---")
    try:
        available_models = []
        # Iteram prin modelele disponibile si pastram doar cele care suporta generare de continut
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        # lista de prioritati
        priority_list = ["models/gemini-2.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]
        chosen = next((priority for priority in priority_list if priority in available_models), None) #functia next() returneaza urmatorul element din iterator. Daca iteratorul este gol returneaza default (None)

        # daca nu exista niciun model prioritar, alegem primul model flash disponibil
        if not chosen and available_models:
            chosen = next((m for m in available_models if "flash" in m.lower()), None)

        #daca nu exista niciun flash, alegem primul model disponibil
        if not chosen and available_models:
            chosen = available_models[0]

        # setam modelul ales si afisam
        if chosen:
            ACTIVE_MODEL_NAME = chosen
            print(f"SUCCESS: Model selectat automat: {ACTIVE_MODEL_NAME}")
        else:
            print("CRITIC: Nu s-a gasit niciun model compatibil!")
            sys.exit(1)

    # in caz de eroare, folosim fallback.
    except Exception as e:
        print(f"Eroare la listarea modelelor: {e}")
        ACTIVE_MODEL_NAME = "models/gemini-2.5-flash"
        print(f"Se incearca fallback fortat la: {ACTIVE_MODEL_NAME}")



def call_gemini(messages_history, trigger_msg=None):
    # aceasta functie face un apel complet la Gemini AI si returneaza textul generat de AI pe baza istoricului conversatiei, rolului (promptului) activ si unui mesaj de declansare (trigger)
    # primeste ca parametri message_history care este o lista de string-uri si reprezinta contextul conversatiei. Ii spune AI-ului ce s-a discutat pana acum. Fara asta, AI ar raspunde "orb", fara context.
    # de intrebat ce rol are trigger_msg.
    # trigger_msg este mesajul care cere explicit un raspuns. Poate fi ultimul mesaj al unui utilizator sau un mesaj artificial ([silence_detecter]). Daca este None, AI primeste un mesaj generic.
    """Apeleaza API-ul Gemini cu istoric si instructiuni de sistem."""
    try:
        #se creeaza un "client" Gemini.
        model = genai.GenerativeModel(
            model_name=ACTIVE_MODEL_NAME, # modelul AI folosit
            system_instruction=active_system_instruction # personalitatea AI-ului
        )
        gemini_history = [{"role": "user", "parts": [msg]} for msg in messages_history] # generam un format structurat deoarece Gemini nu accepta direct o lista de string-uri.
        chat = model.start_chat(history=gemini_history) # aici Gemini "invata" conversatia de pana acum. Istoria este injectata o singura data si fiecare apel creeaza un chat nou, izolat
        prompt_to_send = trigger_msg if trigger_msg else "Analizează contextul. Răspunde conform rolului."
        response = chat.send_message(prompt_to_send) # trimite mesajul catre Gemini AI si asteapta raspunsul. Prompt_to_send este fie ultimul mesaj al utilizatorului, fie un mesaj artificial, fie un mesaj generic. Send_message() adauga un nou mesaj peste acel context si returneaza un obiect (nu un string simplu).
        return response.text.strip() # .text extrage doar textul generat de AI, fara metadate. Fara .text primim un obiect complex greu de folosit. .strip() elimina spatiile de la inceput si de la final si newline-uri (\n)
    except Exception as e:
        print(f"Eroare API Gemini: {e}")
        return "PASS"


def get_ai_decision(trigger_type="review", explicit_msg=None):
    # aceasta functie decide daca AI trebuie sa intervina in chat si, daca da, ce text trimite.
    # trigger_type controleaza de ce este apelata functia. "review" -> a aparut un mesaj nou, "silence" -> nu a mai vorbit nimeni de ceva timp
    # explicit_msg -> mesajul care declanseaza analiza AI. De obicei ultimul mesaj al unui utilizator. Poate fi None
    """Decide daca AI trebuie sa intervina."""
    global conversation_history
    if not is_ai_active:
        return None

    context_msgs = conversation_history[-HISTORY_LIMIT:] # construirea contextului ia ultimele N mesaje din chat. AI trebuie sa stie despre ce se discuta si limitam contextul pentru cost si performanta

    trigger_text = explicit_msg # stabilirea promptului. Initial este mesajul utilizatorului
    if trigger_type == "silence": # aici fortam un prompt artificial. AI nu raspunde la un utilizator ci la starea conversatiei.
        trigger_text = "[SILENCE_DETECTED] - Discuția a murit. Propune o direcție nouă."

    ai_raw_text = call_gemini(context_msgs, trigger_msg=trigger_text) # aici se face efectiv apelul AI. Se trimite contextul + trigger si se primeste un raspuns brut (string)
    clean_text = ai_raw_text.strip().upper() 

    if clean_text == "PASS" or clean_text == "PASS.": # decizia "nu intervin". Aici AI decide sa nu intervina, doar iese.
        print(f"Gemini ({current_prompt_key}) -> PASS")
        return None

    if len(clean_text) > 4: # daca raspunsul este mai lung decat "OK" presupunem ca e mesaj real si returneaza textul AI-ului.
        return ai_raw_text
    
    # psudo-cod:
# dacă AI e oprit → STOP

# context = ultimele mesaje

# dacă trigger = silence
#     prompt special
# altfel
#     prompt = mesaj utilizator

# răspuns = întreabă Gemini

# dacă răspuns = PASS
#     nu vorbi

# dacă răspuns e „real”
#     întoarce-l

# altfel
#     nu vorbi


    # psudo-cod:
# dacă AI e oprit → STOP

# context = ultimele mesaje

# dacă trigger = silence
#     prompt special
# altfel
#     prompt = mesaj utilizator

# răspuns = întreabă Gemini

# dacă răspuns = PASS
#     nu vorbi

# dacă răspuns e „real”
#     întoarce-l

# altfel
#     nu vorbi


    return None


def broadcast(message, is_binary=False):
    # aceasta functie este motorul de distributie al aplicatiei. Trimite un mesaj catre toti clientii conectati
    # parametrul message este mesajul care trebuie trimis
    # is_binary False = mesaj text / True mesajul este deja binar. Punem pentru siguranta ca sa nu encodam de doua ori.
    """Trimite mesaj la toti clientii conectati."""
    if not is_binary:
        message = message.encode('utf-8') # socketurile nu pot trimite string-uri ci doar bytes
    for client in clients: # clients este o lista globala si contine socket-urile tuturor utilizatorilor conectati
        try:
            client.send(message) # trimiterea efectiva catre un client. Se executa odata pentru fiecare client inclusiv pentru cel care a trimis mesajul
        except:
            if client in clients: # in caz de utilizatorul nu mai exista eliminam clientul pentru a preveni crash-uri viitoare.
                clients.remove(client)


def silence_watchdog():
    #aceasta functie urmareste linistea in chat. Verifica daca nu s-a mai vorbit nimic si, daca este cazul, porneste AI-ul sa intervina.
    # functia ruleaza continuu pe un thread separat si monitorizeaza timpul scurs de la ultimul mesaj si daca AI-ul trebuie sa intervina
    """Verifica periodic linistea in chat si declanseaza AI-ul."""
    global last_message_time
    print("Watchdog pornit.")
    while True:
        time.sleep(5) # la fiecare 5 secunde verifica starea chat-ului. Folosim sleep() ca sa nu consumam CPU inutil
        if not is_ai_active: # verificam starea AI. Daca este oprit reseteaza timer-ul
            last_message_time = time.time() #detecteaza linistea. tim() -> timpul curent in secunde. Last_message_time -> ultimul mesaj.
            continue

        if time.time() - last_message_time > SILENCE_THRESHOLD: # silcence_threshold -> pragul
            print("Liniște detectată...")
            response = get_ai_decision(trigger_type="silence")
            if response: # se foloseste un trigger_type="silence" si functia decide daca AI trebuie sa raspunda.
                last_message_time = time.time() # daca AI intervine reseteaza timerul linistii. Trimite mesajul la toti clientii
                broadcast(f"AI ({current_prompt_key}): {response}")
            else:
                # Resetam timpul de liniste cu 10s mai putin decat pragul pentru a forta o verificare rapida daca nu a intervenit
                last_message_time = time.time() - (SILENCE_THRESHOLD - 10)


def handle_client(client, client_address):
    """Gestioneaza comunicarea cu un client."""
    # aceasta functie este inima comunicarii pentru fiecare client conectat la server. Ea ruleaza pe un thread separat pentru fiecare utilizator si gestioneaza tot ce tine
    # de primirea, interpretarea si redirectionarea mesajelor
    # client -> socket-ul clientului
    # client_address -> adresa IP + portul clientului
    # trimite mesajele de la client, le interpreteaza si le trimite mai departe (broadcast) sau declanseaza AI-ul.
    # last_message_time → pentru watchdog-ul de liniște 
    
    global last_message_time, active_system_instruction, current_prompt_key, HISTORY_LIMIT, conversation_history, is_ai_active
    # active_system_instruction → promptul AI
    # current_prompt_key → rolul AI
    # HISTORY_LIMIT → câte mesaje păstrăm în memorie
    # conversation_history → istoricul conversației
    # is_ai_active → dacă AI-ul e activ
    client_ip = client_address[0]

    while True:
        try:
            message = client.recv(BUFFER_SIZE) # recv() primeste date de la client. Daca message este gol -> clientul s-a deconectat si iesim din loop.
            if not message: break

            decoded_msg = message.decode('utf-8') # transformam bytes in str
            last_message_time = time.time() # actualizam last_message_time pentru watchdog-ul de liniste

            if decoded_msg.startswith("CFG:"): # mesaje speciale trimise de client pentru schimbarea rolului AI, setarea limitei istoricului si activarea/dezactivarea AI, setarea limitei de cuvinte AI
                parts = decoded_msg.split(":")

                if parts[1] == "PERS" and parts[2] in PROMPTS: # schimbam rolul AI, resetam istoricul conversatiei si anuntam toti clientii
                    current_prompt_key = parts[2]
                    active_system_instruction = PROMPTS[parts[2]]
                    conversation_history = []
                    broadcast(f"SYS:PERSONALITATE SCHIMBATA ÎN: {current_prompt_key} (Istoric resetat)")

                elif parts[1] == "CACHE": # modifica, cate mesaje vrem sa pastram in memorie
                    try:
                        new_limit = int(parts[2])
                        HISTORY_LIMIT = new_limit
                        broadcast(f"SYS:LIMITA ISTORIC SETATĂ LA: {HISTORY_LIMIT}")
                    except:
                        pass

                elif parts[1] == "AISTATE": # control manual asupra AI. Anunta toti clientii
                    if parts[2] == "ON":
                        is_ai_active = True
                        broadcast(f"SYS:Agentul AI a fost ACTIVAT de catre un utilizator.")
                    else:
                        is_ai_active = False
                        broadcast(f"SYS:Agentul AI a fost OPRIT de catre un utilizator.")

                elif parts[1] == "WORDS": # trimite un mesaj informativ pentru utilizatori
                    broadcast(f"SYS:LIMITA CUVINTE AI SETATĂ LA: {parts[2]}")

            elif decoded_msg.startswith("SYS:JOIN_INFO:"): # mesaje de tip "join"
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

                conversation_history.append(decoded_msg) # actualizarea istoricului. Pastreaza ultimele history_limit mesaje
                if len(conversation_history) > HISTORY_LIMIT: conversation_history.pop(0)

                if not decoded_msg.startswith("SYS:") and "AI (" not in decoded_msg: # declansarea AI (daca este activ). Evitam ca AI sa raspunda la propriile mesaje sau la mesaje de sistem. Pornim un thread separat pentru run_ai_review()
                    if is_ai_active:
                        # NOU: Verificarea finala a starii AI trebuie sa fie in run_ai_review
                        threading.Thread(target=run_ai_review, args=(decoded_msg,)).start()

# Citeste mesaje de la client

# Actualizeaza last_message_time

# Proceseaza mesaje speciale:

# configurari (CFG:)

# join info (SYS:JOIN_INFO:)

# Trimite mesaje normale la toti clientii (broadcast)

# Actualizeaza istoria conversatiei

# Declanseaza AI pentru mesaje noi daca este activ

# Gestioneaza deconectarea clientului
        except:
            if client in clients: clients.remove(client)
            client.close()
            break


def run_ai_review(latest_msg):
    # aceasta functie este executorul deciziei AI pentru meesajele recente.
    # se ocupa de declansarea AI-ului pe un thread separat (ca sa nu blocheze serverul) si de trimiterea raspunului, dar doar daca AI-ul este activ
    """Ruleaza decizia AI pe un thread separat, verificand starea finala."""
    global is_ai_active, current_prompt_key
    # is_ai_active -> daca AI-ul este activ
    # current_prompt_key -> rolul curent al AI-ului (mediator comic, exper juridic, etc.)

    # Verificam starea AI inainte de a incepe procesarea
    if not is_ai_active:
        return

    #apeleaza functia get_ai_decision. Transmite trigger_type="review" -> mesaj normal, nu liniste / explicit_msg=latest_msg -> mesajul curent al utilizatorului
    # primeste response = textul AI, sau None daca AI-ul decide sa nu intervina
    response = get_ai_decision(trigger_type="review", explicit_msg=latest_msg)

    # Verificam starea AI imediat inainte de a trimite raspunsul
    if response and is_ai_active:
        broadcast(f"AI ({current_prompt_key}): {response}")


def receive():
    # aceasta functie este motorul principal al serverului de chat. Ea porneste serverul, accepta clienti noi si initiaza toate thread-urile necesare pentru comunicare si AI
    # creeaza serverul TCP, asculta conexiuni noi, porneste thread-uri pentru fiecare client, porneste "watchdog-ul linistii" pentru AI
    """Porneste serverul si accepta conexiuni."""
    # crearea serverului socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen() # serverul incepe sa asculte conexinui
    print(f"SERVER DOCKER PORNIT PE {HOST}:{PORT}")

    threading.Thread(target=silence_watchdog, daemon=True).start()

    while True:
        client, address = server.accept() # programul se blocheaza aici pana cand un client se conecteaza
        clients.append(client) # atasam clientul in lista
        print(f"Conectat: {address}")

        # Trimitere mesaje de stare la client
        client.send(f"SYS:Oră conexiune: {time.strftime('%Y-%m-%d %H:%M:%S')}".encode('utf-8'))
        client.send(f"SYS:CONECTAT LA SERVER. ROL: {current_prompt_key}".encode('utf-8'))
        client.send(f"SYS:AI ACTIV: {ACTIVE_MODEL_NAME}".encode('utf-8'))
        client.send(f"SYS:ROL INIȚIAL: {current_prompt_key}".encode('utf-8'))

        # creeaza un thread separat pentru fiecare client. Permite serverului sa accepte conexiuni noi fara sa fie blocat
        threading.Thread(target=handle_client, args=(client, address)).start()


# acesta este punctul de pornire al programului, adica ceea ce ruleaza cand executam fisierul direct
if __name__ == "__main__":
    pick_best_model()
    receive()