import socket
import threading
import os
import time
from openai import OpenAI

# --- CONFIGURARE ---
HOST = '0.0.0.0'
PORT = int(os.getenv('PORT', 5555))
OLLAMA_URL = os.getenv('OLLAMA_HOST', 'http://ollama:11434/v1')

# Prompt-ul care definește personalitatea AI-ului
SYSTEM_PROMPT = """
Ești 'AI-Lead', un asistent tehnic într-un chat de developeri.
1. Răspunde scurt și la obiect (maxim 2 fraze).
2. Dacă userii vorbesc despre cod, dă sfaturi bune.
3. Dacă e liniște, propune un subiect tehnic interesant.
"""


# --- CLASA AI AGENT ---
class LLMParticipant:
    def __init__(self, silence_threshold=60):
        self.client = OpenAI(base_url=OLLAMA_URL, api_key='ollama')
        self.history = []
        self.silence_threshold = silence_threshold
        self.last_msg_time = time.time()
        self.running = True

        # Thread care verifică liniștea
        self.monitor = threading.Thread(target=self._silence_watchdog)
        self.monitor.daemon = True
        self.monitor.start()

    def add_message(self, user, content):
        self.last_msg_time = time.time()
        self.history.append({"role": "user", "content": f"{user}: {content}"})
        if len(self.history) > 10:  # Păstrăm context mic
            self.history.pop(0)

        # Trigger: Răspunde doar dacă este strigat sau e o întrebare directă
        if "ai" in content.lower() or "@ai" in content.lower():
            return self._generate_response("reply")
        return None

    def _generate_response(self, trigger_type):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history

        if trigger_type == "silence":
            messages.append({"role": "user", "content": "E liniște. Generează o întrebare tehnică scurtă."})

        try:
            response = self.client.chat.completions.create(
                model="llama3",
                messages=messages,
                max_tokens=100
            )
            reply = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"Eroare AI: {e}")
            return None

    def _silence_watchdog(self):
        while self.running:
            time.sleep(10)
            if time.time() - self.last_msg_time > self.silence_threshold:
                print("Liniște detectată... AI-ul intervine.")
                reply = self._generate_response("silence")
                if reply:
                    broadcast_function(f"AI-Lead: {reply}".encode('utf-8'))
                self.last_msg_time = time.time()


# --- SERVER SOCKET ---
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

# Inițializăm AI-ul (intervine după 60 secunde de liniște)
ai_bot = LLMParticipant(silence_threshold=60)


# Funcție globală pentru a permite AI-ului să vorbească singur
def broadcast_function(message):
    for client in clients:
        try:
            client.send(message)
        except:
            pass


def broadcast(message):
    broadcast_function(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)

            # Trimitem copia mesajului la AI
            try:
                decoded = message.decode('utf-8')
                if ": " in decoded:
                    user, text = decoded.split(": ", 1)
                    ai_reply = ai_bot.add_message(user, text)
                    if ai_reply:
                        broadcast(f"AI-Lead: {ai_reply}".encode('utf-8'))
            except:
                pass  # Ignorăm erori de decodare

        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} a iesit!'.encode('utf-8'))
                nicknames.remove(nickname)
                break


def receive():
    print(f"Server AI pornit pe portul {PORT}...")
    while True:
        client, address = server.accept()
        print(f"Conectat: {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname: {nickname}")
        broadcast(f"{nickname} s-a alaturat!".encode('utf-8'))
        client.send('Conectat la serverul AI!\n'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    receive()