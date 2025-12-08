# -*- coding: utf-8 -*-
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import sys
import time
import hashlib
import platform
import psutil
import os
import ttkbootstrap as tb
from tkinter import ttk

HOST = 'iulianddd.ddns.net'
PORT = 5555

# --- STIL CHAT (FARA INDENTARE, FARA SPATII MARGINALE) ---
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10
COLOR_TEXT = "#ffffff"
COLOR_AI_TEXT = "#90caf9"
ACCENT_COLOR = "#4361ee"


def get_user_color(nickname):
    """Genereaza o culoare unica pentru user bazata pe numele lui."""
    hash_object = hashlib.sha1(nickname.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    r = int(hex_dig[0:2], 16) % 100 + 155
    g = int(hex_dig[2:4], 16) % 100 + 155
    b = int(hex_dig[4:6], 16) % 100 + 155
    return f"#{r:02x}{g:02x}{b:02x}"


def get_system_info():
    """Colecteaza informatiile hardware locale."""
    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "CPU": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "GPU": "Necunoscută",
        "VRAM": "N/A"
    }
    try:
        if platform.system() == "Windows":
            info["CPU"] = os.popen('wmic cpu get name').read().strip().split('\n')[-1].strip()
        elif platform.system() == "Linux":
            info["CPU"] = os.popen("lscpu | grep 'Model name'").read().split(':')[-1].strip()
    except Exception:
        pass
    return info


PERSONALITIES = [
    "Mediator Comic", "Receptor (Analist)", "Expert Juridic",
    "Evaluator Proiecte", "Expert HR", "Business Analist (BA)",
    "Expert Logistică"
]


class ClientGui:
    def __init__(self):
        msg = tk.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Autentificare", "Numele tău:", parent=msg)
        if not self.nickname:
            sys.exit()

        self.system_info = get_system_info()
        self.gui_done = False
        self.running = True
        self.current_ai_role = PERSONALITIES[0]
        self.current_ai_model = "Necunoscut"
        self.is_ai_on = True
        self.user_tags = {}
        self.max_words = 50

        self.gui_loop()

    def update_status_bar(self):
        """Actualizeaza bara de status cu informatii extinse."""
        status_text = (
            f"Sistem: {self.system_info['OS']} | "
            f"CPU: {self.system_info['CPU']} | "
            f"RAM: {self.system_info['RAM']} | "
            f"GPU: {self.system_info['GPU']} | "
            f"VRAM: {self.system_info['VRAM']} | "
            f"AI ROL: {self.current_ai_role} | "
            f"AI MODEL: {self.current_ai_model} | "
            f"Conectat la: {HOST}:{PORT}"
        )
        self.status_label.config(text=status_text)

    def gui_loop(self):
        self.win = tb.Window(themename="darkly")
        self.win.title(f"Team Chat - {self.nickname}")
        self.win.geometry("1500x750")

        # Încearcă să te conecteze la server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(None)

            # Trimitem informatiile sistemului catre server
            info_message = (
                f"SYS:JOIN_INFO:{self.nickname}|"
                f"OS:{self.system_info['OS']}|"
                f"CPU:{self.system_info['CPU']}|"
                f"RAM:{self.system_info['RAM']}|"
                f"GPU:{self.system_info['GPU']}|"
                f"VRAM:{self.system_info['VRAM']}"
            )
            self.sock.send(info_message.encode('utf-8'))

        except Exception as e:
            messagebox.showerror("Eroare Fatală", f"Nu m-am putut conecta la serverul: {HOST}\nEroare: {e}")
            self.win.destroy()
            sys.exit()

        # 1. Header (Titlu)
        header = ttk.Frame(self.win)
        header.pack(fill='x', side='top')
        ttk.Label(header, text=f"Team Chat - {self.nickname}", font=(FONT_FAMILY, 12, "bold")).pack(pady=5)

        # 2. Control Frame
        control_frame = ttk.Frame(self.win)
        control_frame.pack(fill='x', side='top', padx=10, pady=5)

        # Dropdown Personalitate AI
        ttk.Label(control_frame, text="Rol AI:", font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.pers_var = tk.StringVar(self.win, value=self.current_ai_role)
        self.pers_combo = ttk.Combobox(control_frame, textvariable=self.pers_var, values=PERSONALITIES,
                                       state="readonly", width=20, font=(FONT_FAMILY, 9))
        self.pers_combo.pack(side="left", padx=(0, 15))
        self.pers_combo.bind("<<ComboboxSelected>>", self.send_pers_config)

        # Dropdown Istoric Mesaje
        CACHE_OPTIONS = [str(i) for i in range(5, 51, 5)]
        ttk.Label(control_frame, text="Istoric Mesaje:", font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.cache_var = tk.StringVar(self.win, value="30")
        self.cache_combo = ttk.Combobox(control_frame, textvariable=self.cache_var, values=CACHE_OPTIONS,
                                        state="readonly", width=5, font=(FONT_FAMILY, 9))
        self.cache_combo.pack(side="left", padx=(0, 15))
        self.cache_combo.bind("<<ComboboxSelected>>", self.send_cache_config)

        # Slider Limită Cuvinte AI
        ttk.Label(control_frame, text="Max Cuvinte AI:", font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(10, 5))
        self.words_var = tk.IntVar(value=self.max_words)
        self.words_slider = tb.Scale(control_frame, from_=10, to=100, orient=tk.HORIZONTAL,
                                     variable=self.words_var, command=self.send_word_limit_config,
                                     style="primary", length=150)
        self.words_slider.pack(side="left")

        # Buton ON/OFF AI
        self.ai_toggle_button = tb.Button(control_frame, text="AI ON", bootstyle="success",
                                          command=self.toggle_ai_state)
        self.ai_toggle_button.pack(side="right", padx=(15, 0))

        # 3. Chat Area
        frame_chat = ttk.Frame(self.win)
        frame_chat.pack(expand=True, fill='both', padx=10, pady=10)

        self.text_area = scrolledtext.ScrolledText(frame_chat,
                                                   fg=COLOR_TEXT,
                                                   font=(FONT_FAMILY, FONT_SIZE), bd=1, padx=10, pady=10,
                                                   relief=tk.FLAT)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled',
                              bg=self.win.style.colors.bg,
                              wrap=tk.WORD)  # Asiguram word wrap pentru EOL automat

        # --- CONFIGURARE TAG-URI ---

        # AI: Fara indentare, Font 8, Italic
        self.text_area.tag_config('ai_style', foreground=COLOR_AI_TEXT, font=(FONT_FAMILY, 8, "italic"), justify='left')

        # OAMENI (Standard): Fara indentare, Font 10
        self.text_area.tag_config('normal', font=(FONT_FAMILY, FONT_SIZE), justify='left')

        # Mesaje de sistem
        self.text_area.tag_config('sys_tag', foreground="#ff8a80", font=(FONT_FAMILY, 9), justify='left')

        # Mesajele tale (culoarea ta, bold)
        self.text_area.tag_config('me_tag', foreground=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE, "bold"))

        # Text bold
        self.text_area.tag_config('bold', foreground=COLOR_TEXT, font=(FONT_FAMILY, FONT_SIZE, "bold"))

        # Info tehnice (pentru bara de status/join)
        self.text_area.tag_config('tech_info', foreground="#80deea", font=(FONT_FAMILY, 8))

        # --- BARA DE STATUS (Status Bar) ---
        self.status_label = ttk.Label(self.win, text="Se conectează...", anchor="w",
                                      font=(FONT_FAMILY, 8), bootstyle="inverse-secondary")
        self.status_label.pack(side="bottom", fill="x")
        self.update_status_bar()

        # --- PREAMBUL SIMPLIFICAT ---
        self.text_area.config(state='normal')
        self.text_area.insert('end', f"⚠ Tentativă de conectare la {HOST}:{PORT}...\n", 'sys_tag')
        self.text_area.config(state='disabled')

        # 4. Input Frame
        input_frame = ttk.Frame(self.win)
        input_frame.pack(fill='x', side='bottom', pady=10, padx=10)

        self.input_area = tb.Entry(input_frame, bootstyle="primary", font=(FONT_FAMILY, 11))
        self.input_area.pack(side="left", fill='x', expand=True, padx=10)
        self.input_area.bind("<Return>", self.write)

        tb.Button(input_frame, text="Trimite", bootstyle="primary",
                  command=self.write).pack(side="right", padx=10)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.win.mainloop()

    # --- Logica Butoane si Configurare (Metode neschimbate) ---

    def toggle_ai_state(self):
        """Porneste/Opreste AI-ul si trimite semnal la server."""
        self.is_ai_on = not self.is_ai_on
        if self.is_ai_on:
            self.ai_toggle_button.config(text="AI ON", bootstyle="success")
            self.send_config("AISTATE", "ON")
        else:
            self.ai_toggle_button.config(text="AI OFF", bootstyle="danger")
            self.send_config("AISTATE", "OFF")

    def send_pers_config(self, event=None):
        """Trimite personalitatea noua si semnal de reset context."""
        pers_value = self.pers_var.get()
        self.send_config("PERS", pers_value)
        self.current_ai_role = pers_value

    def send_cache_config(self, event=None):
        cache_value = self.cache_var.get()
        try:
            cache_limit = int(cache_value)
            if 5 <= cache_limit <= 50:
                self.send_config("CACHE", str(cache_limit))
        except ValueError:
            pass

    def send_word_limit_config(self, value):
        self.max_words = int(value)
        self.send_config("WORDS", str(self.max_words))

    def send_config(self, type, value):
        """Functie generica pentru trimitere configurari catre server."""
        msg = f"CFG:{type}:{value}"
        try:
            self.sock.send(msg.encode('utf-8'))
        except:
            pass

    def write(self, event=None):
        """Trimite mesajul catre server."""
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

    def display_join_info(self, clean_message):
        """Afiseaza detaliile tehnice simplificate ale unui utilizator care s-a alaturat."""
        parts = clean_message.split('|')

        info = {"IP": "N/A"}
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                info[key] = value

        nickname = info.get('NICKNAME', 'Anonim')

        # Formatare compacta: Nume s-a conectat! (IP | CPU | OS | RAM)
        tech_line = (
            f"({info.get('IP')} | "
            f"{info.get('CPU').split(' Processor')[0].strip()} | "
            f"{info.get('OS')} | "
            f"{info.get('RAM')})"
        )

        # Afisam mesajul de alaturare principal
        self.text_area.insert('end', f"{nickname} s-a conectat! ", 'bold')

        # Afisam detaliile tehnice cu font mic si culoare stearsa
        self.text_area.insert('end', tech_line + "\n", 'tech_info')

        # Adaugam o linie goala de separare
        self.text_area.insert('end', "\n", 'sys_tag')

    def receive(self):
        # Aici ascultam mesajele care vin de la server
        first_message_received = False
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.text_area.config(state='normal')

                    # Curatam fereastra la primirea primului mesaj de stare
                    if not first_message_received and message.startswith("SYS:"):
                        self.text_area.delete('1.0', tk.END)
                        first_message_received = True

                    if message.startswith("SYS:"):
                        clean = message.replace("SYS:", "")

                        # 1. Tratare mesaje de join cu info tehnice (afisam doar info)
                        if clean.startswith("JOIN_INFO:"):
                            self.display_join_info(clean.replace("JOIN_INFO:", ""))

                        # 2. Mesajele de sistem normale (care nu sunt JOIN_INFO)
                        else:
                            # Actualizare status bar si ROL/MODEL AI
                            if "AI ACTIV:" in clean:
                                self.current_ai_model = clean.split("AI ACTIV: ")[1].strip()
                            elif "ROL INIȚIAL:" in clean or "PERSONALITATE SCHIMBATA ÎN:" in clean:
                                new_role = clean.split(": ")[1].strip()
                                self.current_ai_role = new_role
                                self.pers_combo.set(new_role)

                            self.update_status_bar()

                            # Afisam mesajul de sistem (ex: Ora conexiune, ROL, etc.)
                            self.text_area.insert('end', f"⚠ {clean}\n", 'sys_tag')

                    elif "AI (" in message:
                        # Mesaj primit de la AI - FARA INDENTARE
                        parts = message.split(":", 1)
                        if len(parts) > 1:
                            u_name = parts[0] + ":"
                            u_msg = parts[1]
                            self.text_area.insert('end', u_name, 'ai_style')
                            self.text_area.insert('end', u_msg + "\n", 'ai_style')
                            self.text_area.insert('end', "\n", 'sys_tag')
                        else:
                            self.text_area.insert('end', message + "\n", 'ai_style')

                    else:
                        # Mesaj primit de la un user - FARA INDENTARE
                        if ":" in message:
                            parts = message.split(":", 1)
                            u_name = parts[0]
                            u_msg = parts[1]

                            if u_name not in self.user_tags:
                                user_color = get_user_color(u_name)
                                self.user_tags[u_name] = user_color
                                self.text_area.tag_config(f'user_name_{u_name}', foreground=user_color,
                                                          font=(FONT_FAMILY, FONT_SIZE, "bold"))

                            user_name_tag = f'user_name_{u_name}'

                            # APLICARE SIMPLIFICATĂ FARA INDENTARE
                            if u_name == self.nickname:
                                # Mesajele tale folosesc me_tag
                                self.text_area.insert('end', f"{u_name}: ", 'me_tag')
                                self.text_area.insert('end', u_msg + "\n", 'normal')
                            else:
                                # Mesajele altor useri folosesc user_name_tag + normal
                                self.text_area.insert('end', u_name + ": ", user_name_tag)
                                self.text_area.insert('end', u_msg + "\n", 'normal')
                        else:
                            self.text_area.insert('end', message + "\n", 'normal')

                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except Exception as e:
                if self.running:
                    print(f"Eroare de conexiune la server: {e}")
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', "\n!!! EROARE CRITICĂ: Conexiunea cu serverul a fost pierdută.\n",
                                          'sys_tag')
                    self.text_area.config(state='disabled')
                    self.running = False
                break


if __name__ == "__main__":
    ClientGui()