# -*- coding: utf-8 -*-
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk, messagebox
import sys
import time
import hashlib

HOST = 'iulianddd.ddns.net'
PORT = 5555

# --- TEMĂ MODERN CHAT (STIL WHATSAPP LIGHT) ---
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10

# Culorile cerute de utilizator
COLOR_BG = "#a2a7f5"  # Fundal fereastra (Light Indigo)
COLOR_CHAT_BG = "#d1d2e6"  # Fundal zona de text (Muted Light Purple)

# Alte culori pentru contrast
COLOR_TEXT = "#212529"  # Text negru/gri închis
COLOR_BTN = "#4361ee"  # Albastru primar
COLOR_BTN_TEXT = "#ffffff"
COLOR_AI_TEXT = "#495057"  # Gri închis pentru citate AI


def get_user_color(nickname):
    """Generează o culoare pastelată unică pe baza numelui utilizatorului."""
    hash_object = hashlib.sha1(nickname.encode('utf-8'))
    hex_dig = hash_object.hexdigest()

    # Asigură o culoare deschisă/pastelată
    r = int(hex_dig[0:2], 16) % 150 + 50
    g = int(hex_dig[2:4], 16) % 150 + 50
    b = int(hex_dig[4:6], 16) % 150 + 50

    return f"#{r:02x}{g:02x}{b:02x}"


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

        self.nickname = simpledialog.askstring("Autentificare", "Numele tău:", parent=msg)
        if not self.nickname:
            sys.exit()

        self.gui_done = False
        self.running = True

        self.host_address = HOST
        self.connection_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.current_ai_model = "Necunoscut"
        self.current_ai_role = "Expert IT (Cortex)"
        self.user_tags = {}  # Dictionary pentru a stoca culorile dinamice

        self.gui_loop()

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title(f"Team Chat - {self.nickname}")
        self.win.configure(bg=COLOR_BG)
        self.win.geometry("450x650")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(None)
        except Exception as e:
            messagebox.showerror("Eroare Fatală",
                                 f"Nu m-am putut conecta la serverul: {HOST}\n\n"
                                 f"Verifică:\n1. Dacă serverul Docker rulează.\n2. Dacă adresa IP este corectă.\n3. Port Forwarding (5555)."
                                 )
            self.win.destroy()
            sys.exit()

        # 1. Header (Titlu)
        header = tk.Frame(self.win, bg="white", height=30)
        header.pack(fill='x', side='top')
        tk.Label(header, text=f"Team Chat - {self.nickname}", font=(FONT_FAMILY, 12, "bold"), bg="white",
                 fg=COLOR_TEXT).pack(pady=5)

        # 2. Control Frame (Dropdowns)
        control_frame = tk.Frame(self.win, bg=COLOR_BG, padx=10, pady=5)
        control_frame.pack(fill='x', side='top')

        # --- Dropdown Personalitate ---
        tk.Label(control_frame, text="Rol AI:", bg=COLOR_BG, fg=COLOR_TEXT, font=(FONT_FAMILY, 9, "bold")).pack(
            side="left", padx=(0, 5))
        self.pers_var = tk.StringVar(self.win, value=self.current_ai_role)
        self.pers_combo = ttk.Combobox(control_frame, textvariable=self.pers_var, values=PERSONALITIES,
                                       state="readonly", width=20, font=(FONT_FAMILY, 9))
        self.pers_combo.pack(side="left", padx=(0, 15))
        self.pers_combo.bind("<<ComboboxSelected>>", self.send_pers_config)

        # --- Dropdown Cache ---
        CACHE_OPTIONS = [str(i) for i in range(5, 51, 5)]  # 5, 10, 15, ..., 50
        tk.Label(control_frame, text="Istoric Cache:", bg=COLOR_BG, fg=COLOR_TEXT, font=(FONT_FAMILY, 9, "bold")).pack(
            side="left", padx=(0, 5))
        self.cache_var = tk.StringVar(self.win, value="30")
        self.cache_combo = ttk.Combobox(control_frame, textvariable=self.cache_var, values=CACHE_OPTIONS,
                                        state="readonly", width=5, font=(FONT_FAMILY, 9))
        self.cache_combo.pack(side="left")
        self.cache_combo.bind("<<ComboboxSelected>>", self.send_cache_config)

        # 3. Chat Area
        frame_chat = tk.Frame(self.win, bg=COLOR_BG, padx=10, pady=10)
        frame_chat.pack(expand=True, fill='both')

        # Text Area cu Fundalul cerut (#d1d2e6)
        self.text_area = scrolledtext.ScrolledText(frame_chat, bg=COLOR_CHAT_BG, fg=COLOR_TEXT,
                                                   font=(FONT_FAMILY, FONT_SIZE), bd=0, padx=10, pady=10)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled')

        # Configurare Tag-uri
        self.text_area.tag_config('normal', font=(FONT_FAMILY, FONT_SIZE))
        self.text_area.tag_config('ai_style', foreground=COLOR_AI_TEXT, font=(FONT_FAMILY, FONT_SIZE, "italic"))
        self.text_area.tag_config('sys_tag', foreground="#dc3545", font=(FONT_FAMILY, 9))
        self.text_area.tag_config('me_tag', foreground=COLOR_BTN, font=(FONT_FAMILY, FONT_SIZE, "bold"))
        self.text_area.tag_config('bold', font=(FONT_FAMILY, FONT_SIZE, "bold"))

        self.text_area.config(state='normal')
        self.text_area.insert('end', f"⚠ Conectat la: {self.host_address}:{PORT}\n", 'sys_tag')
        self.text_area.insert('end', f"⚠ Oră conexiune: {self.connection_time}\n", 'sys_tag')
        self.text_area.insert('end', f"{self.nickname} s-a alăturat!\n", 'bold')
        self.text_area.config(state='disabled')

        # 4. Input Frame
        input_frame = tk.Frame(self.win, bg="white", pady=10, padx=10)
        input_frame.pack(fill='x', side='bottom')

        # Am eliminat butonul '⚙'

        self.input_area = tk.Entry(input_frame, bg="#e9ecef", fg=COLOR_TEXT, font=(FONT_FAMILY, 11), relief="flat",
                                   bd=5)
        self.input_area.pack(side="left", fill='x', expand=True)
        self.input_area.bind("<Return>", self.write)

        tk.Button(input_frame, text="Trimite", bg=COLOR_BTN, fg=COLOR_BTN_TEXT, font=(FONT_FAMILY, 10, "bold"), bd=0,
                  padx=15,
                  pady=5, command=self.write).pack(side="right", padx=(5, 0))

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.win.mainloop()

    # --- Funcții de Configurare Directă ---
    def send_pers_config(self, event=None):
        pers_value = self.pers_var.get()
        self.send_config("PERS", pers_value)
        self.current_ai_role = pers_value

    def send_cache_config(self, event=None):
        cache_value = self.cache_var.get()
        try:
            cache_limit = int(cache_value)
            if 5 <= cache_limit <= 50:
                self.send_config("CACHE", str(cache_limit))
            else:
                messagebox.showerror("Eroare", "Limita de istoric trebuie să fie între 5 și 50.")
        except ValueError:
            messagebox.showerror("Eroare", "Limita de istoric trebuie să fie un număr întreg.")

    def send_config(self, type, value):
        msg = f"CFG:{type}:{value}"
        try:
            self.sock.send(msg.encode('utf-8'))
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

                        if "AI ACTIV:" in clean:
                            self.current_ai_model = clean.split("AI ACTIV: ")[1].strip()
                        if "ROL INIȚIAL:" in clean:
                            self.current_ai_role = clean.split("ROL INIȚIAL: ")[1].strip()

                    elif "AI (" in message:
                        parts = message.split("): ", 1)
                        if len(parts) > 1:
                            role = parts[0] + ")"
                            msg = parts[1]
                            # Aplică stilul gri-italic (ai_style) la nume și la text
                            self.text_area.insert('end', role + ": ", 'ai_style')
                            self.text_area.insert('end', msg + "\n", 'ai_style')
                        else:
                            self.text_area.insert('end', message + "\n", 'ai_style')

                    else:
                        if ":" in message:
                            parts = message.split(":", 1)
                            u_name = parts[0]
                            u_msg = parts[1]

                            # Logica pentru generarea tag-urilor dinamice
                            if u_name not in self.user_tags:
                                self.user_tags[u_name] = get_user_color(u_name)
                                self.text_area.tag_config(f'user_name_{u_name}', foreground=self.user_tags[u_name],
                                                          font=(FONT_FAMILY, FONT_SIZE, "bold"))
                                self.text_area.tag_config(f'user_msg_{u_name}', foreground=self.user_tags[u_name],
                                                          font=(FONT_FAMILY, FONT_SIZE))

                            user_name_tag = f'user_name_{u_name}'
                            user_msg_tag = f'user_msg_{u_name}'

                            if u_name == self.nickname:
                                # Userul local: Nume colorat (blue), text standard (negru)
                                self.text_area.insert('end', f"{u_name}: ", 'me_tag')
                                self.text_area.insert('end', u_msg + "\n", 'normal')
                            else:
                                # User extern: Nume și text cu aceeași culoare pastelată
                                self.text_area.insert('end', u_name + ": ", user_name_tag)
                                self.text_area.insert('end', u_msg + "\n", user_msg_tag)
                        else:
                            self.text_area.insert('end', message + "\n", 'normal')

                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except:
                break


if __name__ == "__main__":
    ClientGui()