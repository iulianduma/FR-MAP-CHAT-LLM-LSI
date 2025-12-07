import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk, messagebox
import random
import sys

# --- CONFIGURARE REȚEA ---
# IMPORTANT: Daca testezi de pe acelasi PC cu serverul, pune '127.0.0.1'
# Daca testezi de pe alt PC sau internet, pune 'iulianddd.ddns.net'
HOST = '192.168.1.254'
PORT = 5555

# --- TEMĂ MODERN LIGHT ---
COLOR_BG = "#f0f2f5"  # Gri foarte deschis (ca la WhatsApp Web)
COLOR_CHAT_BG = "#ffffff"  # Alb pur pentru zona de text
COLOR_TEXT = "#1c1e21"  # Aproape negru (lizibil)
COLOR_BTN = "#0084ff"  # Albastru Messenger
COLOR_BTN_TEXT = "#ffffff"
COLOR_AI = "#6c757d"  # Gri elegant pentru AI
COLOR_USER = "#000000"  # Negru pentru useri

PERSONALITIES = [
    "Expert IT (Cortex)", "Expert Contabil", "Avocat Corporatist",
    "Project Manager", "Medic (Consultant)", "Expert CyberSecurity",
    "UX/UI Designer", "Data Scientist", "HR Manager", "Marketing Strategist",
    "Business Analyst", "DevOps Engineer", "Quality Assurance (QA)",
    "Startup Founder", "Profesor Istorie", "Psiholog Organizational",
    "Investitor VC", "Jurnalist Tech", "Consultant GDPR", "Expert Logistică"
]


class ClientGui:
    def __init__(self):
        msg = tk.Tk()
        msg.withdraw()

        # 1. Login
        self.nickname = simpledialog.askstring("Autentificare", "Numele tău:", parent=msg)
        if not self.nickname:
            sys.exit()

        # 2. Conectare
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)  # 5 secunde maxim sa astepte serverul
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(None)
        except Exception as e:
            messagebox.showerror("Eroare Fatală",
                                 f"Nu m-am putut conecta la serverul: {HOST}\n\n"
                                 f"Verifică:\n1. Dacă serverul Docker rulează.\n2. Dacă adresa IP este corectă.\n3. Port Forwarding (5555)."
                                 )
            sys.exit()

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title(f"Team Chat - {self.nickname}")
        self.win.configure(bg=COLOR_BG)
        self.win.geometry("450x650")

        # Header simplu
        header = tk.Frame(self.win, bg="white", height=50)
        header.pack(fill='x', side='top')
        tk.Label(header, text="Echo Team Chat", font=("Helvetica", 12, "bold"), bg="white", fg=COLOR_TEXT).pack(pady=10)

        # Zona Chat
        frame_chat = tk.Frame(self.win, bg=COLOR_BG, padx=10, pady=10)
        frame_chat.pack(expand=True, fill='both')

        self.text_area = scrolledtext.ScrolledText(frame_chat, bg=COLOR_CHAT_BG, fg=COLOR_TEXT, font=("Helvetica", 10),
                                                   bd=0, padx=10, pady=10)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled')

        # Tag-uri vizuale
        self.text_area.tag_config('ai_tag', foreground=COLOR_AI, font=("Helvetica", 10, "italic"))
        self.text_area.tag_config('sys_tag', foreground="red", font=("Helvetica", 9))
        self.text_area.tag_config('me_tag', foreground=COLOR_BTN, font=("Helvetica", 10, "bold"))
        self.text_area.tag_config('bold', font=("Helvetica", 10, "bold"))

        # Zona Input
        input_frame = tk.Frame(self.win, bg="white", pady=10, padx=10)
        input_frame.pack(fill='x', side='bottom')

        # Buton Setari (mic, gri)
        tk.Button(input_frame, text="⚙", bg="#e4e6eb", fg="black", bd=0, padx=10, pady=5,
                  command=self.open_settings).pack(side="left", padx=(0, 5))

        self.input_area = tk.Entry(input_frame, bg="#f0f2f5", fg="black", font=("Helvetica", 11), relief="flat", bd=5)
        self.input_area.pack(side="left", fill='x', expand=True)
        self.input_area.bind("<Return>", self.write)

        # Buton Trimite (Albastru)
        tk.Button(input_frame, text="Trimite", bg=COLOR_BTN, fg="white", font=("Helvetica", 10, "bold"), bd=0, padx=15,
                  pady=5, command=self.write).pack(side="right", padx=(5, 0))

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def open_settings(self):
        top = tk.Toplevel(self.win)
        top.title("Setări Agent AI")
        top.geometry("350x250")
        top.configure(bg="white")

        tk.Label(top, text="Alege Rolul AI:", font=("Helvetica", 10, "bold"), bg="white").pack(pady=(20, 5))

        self.pers_var = tk.StringVar()
        combo = ttk.Combobox(top, textvariable=self.pers_var, values=PERSONALITIES, state="readonly", width=30)
        combo.current(0)
        combo.pack(pady=5)

        tk.Button(top, text="Aplică Schimbarea", bg=COLOR_BTN, fg="white", bd=0, pady=5,
                  command=lambda: self.send_config("PERS", self.pers_var.get())).pack(pady=15)

    def send_config(self, type, value):
        msg = f"CFG:{type}:{value}"
        try:
            self.sock.send(msg.encode('utf-8'))
            messagebox.showinfo("Info", "Configurația a fost actualizată.")
        except:
            pass

    def write(self, event=None):
        txt = self.input_area.get()
        if txt:
            message = f"{self.nickname}:{txt}"
            try:
                self.sock.send(message.encode('utf-8'))
                self.input_area.delete(0, 'end')
            except:
                self.text_area.config(state='normal')
                self.text_area.insert('end', "Eroare conexiune!\n", 'sys_tag')
                self.text_area.config(state='disabled')

    def stop(self):
        self.running = False
        self.win.destroy()
        try:
            self.sock.close()
        except:
            pass
        sys.exit()

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.text_area.config(state='normal')

                    if message.startswith("SYS:"):
                        clean = message.replace("SYS:", "")
                        self.text_area.insert('end', f"⚠ {clean}\n", 'sys_tag')

                    elif "AI (" in message:
                        # Format: AI (Rol): Mesaj
                        parts = message.split("): ", 1)
                        if len(parts) > 1:
                            role = parts[0] + ")"
                            msg = parts[1]
                            self.text_area.insert('end', role + ": ", 'ai_tag')
                            self.text_area.insert('end', msg + "\n")
                        else:
                            self.text_area.insert('end', message + "\n", 'ai_tag')

                    else:
                        # Format: User:Mesaj
                        if ":" in message:
                            parts = message.split(":", 1)
                            u_name = parts[0]
                            u_msg = parts[1]

                            if u_name == self.nickname:
                                self.text_area.insert('end', "Eu: ", 'me_tag')
                            else:
                                self.text_area.insert('end', u_name + ": ", 'bold')

                            self.text_area.insert('end', u_msg + "\n")
                        else:
                            self.text_area.insert('end', message + "\n")

                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except:
                break


if __name__ == "__main__":
    ClientGui()