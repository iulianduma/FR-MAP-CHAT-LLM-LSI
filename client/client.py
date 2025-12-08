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

# --- TEMĂ TKINTER MODERNĂ DARK MODE ---
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10  # Mărimea standard pentru oameni (care vor fi indentati)

# Culori optimizate pentru Dark Mode
COLOR_BG = "#1e1e1e"  # Fundal fereastra (Gri foarte închis)
COLOR_CHAT_BG = "#2c2c2c"  # Fundal zona de chat (Gri mai deschis)
COLOR_TEXT = "#ffffff"  # Text standard (Alb)
COLOR_BTN_TEXT = "#ffffff"  # Text buton (Alb)
COLOR_AI_TEXT = "#90caf9"  # Albastru deschis pentru AI

ACCENT_COLOR = "#4361ee"  # Culoarea de accent


def get_user_color(nickname):
    """Generează o culoare unică pentru user bazată pe numele lui."""
    hash_object = hashlib.sha1(nickname.encode('utf-8'))
    hex_dig = hash_object.hexdigest()

    # Generăm culori deschise care să se vadă bine pe fundalul întunecat
    r = int(hex_dig[0:2], 16) % 100 + 155
    g = int(hex_dig[2:4], 16) % 100 + 155
    b = int(hex_dig[4:6], 16) % 100 + 155

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

        # Cere nickname-ul la început
        self.nickname = simpledialog.askstring("Autentificare", "Numele tău:", parent=msg)
        if not self.nickname:
            sys.exit()

        self.gui_done = False
        self.running = True

        self.host_address = HOST
        self.connection_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.current_ai_model = "Necunoscut"
        self.current_ai_role = "Expert IT (Cortex)"
        self.user_tags = {}
        self.max_words = 50

        self.gui_loop()

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title(f"Team Chat - {self.nickname}")
        self.win.geometry("1500x750")
        self.win.configure(bg=COLOR_BG)

        # Încearcă să te conecteze la server
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
        header = tk.Frame(self.win, bg=COLOR_CHAT_BG, height=30)
        header.pack(fill='x', side='top')
        tk.Label(header, text=f"Team Chat - {self.nickname}", font=(FONT_FAMILY, 12, "bold"), bg=COLOR_CHAT_BG,
                 fg=COLOR_TEXT).pack(pady=5)

        # 2. Control Frame (Dropdowns + Slider)
        control_frame = tk.Frame(self.win, bg=COLOR_BG, padx=10, pady=5)
        control_frame.pack(fill='x', side='top')

        # Dropdown Personalitate AI
        tk.Label(control_frame, text="Rol AI:", bg=COLOR_BG, fg=COLOR_TEXT, font=(FONT_FAMILY, 10, "bold")).pack(
            side="left", padx=(0, 5))
        self.pers_var = tk.StringVar(self.win, value=self.current_ai_role)
        self.pers_combo = ttk.Combobox(control_frame, textvariable=self.pers_var, values=PERSONALITIES,
                                       state="readonly", width=20, font=(FONT_FAMILY, 9))
        self.pers_combo.pack(side="left", padx=(0, 15))
        self.pers_combo.bind("<<ComboboxSelected>>", self.send_pers_config)

        # Dropdown Istoric Mesaje
        CACHE_OPTIONS = [str(i) for i in range(5, 51, 5)]
        tk.Label(control_frame, text="Istoric Mesaje:", bg=COLOR_BG, fg=COLOR_TEXT,
                 font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.cache_var = tk.StringVar(self.win, value="30")
        self.cache_combo = ttk.Combobox(control_frame, textvariable=self.cache_var, values=CACHE_OPTIONS,
                                        state="readonly", width=5, font=(FONT_FAMILY, 9))
        self.cache_combo.pack(side="left", padx=(0, 15))
        self.cache_combo.bind("<<ComboboxSelected>>", self.send_cache_config)

        # Slider Limită Cuvinte AI
        tk.Label(control_frame, text="Max Cuvinte AI:", bg=COLOR_BG, fg=COLOR_TEXT,
                 font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(10, 5))

        self.words_var = tk.IntVar(value=self.max_words)
        self.words_slider = tk.Scale(control_frame, from_=10, to=100, orient=tk.HORIZONTAL, resolution=10,
                                     variable=self.words_var, command=self.send_word_limit_config,
                                     label="", troughcolor=ACCENT_COLOR, sliderrelief=tk.FLAT, bd=0,
                                     bg=COLOR_BG, fg=COLOR_TEXT, highlightthickness=0)
        self.words_slider.pack(side="left")

        # 3. Chat Area - Aici se afișează mesajele
        frame_chat = tk.Frame(self.win, bg=COLOR_BG, padx=10, pady=10)
        frame_chat.pack(expand=True, fill='both')

        # Zona de text
        self.text_area = scrolledtext.ScrolledText(frame_chat, bg=COLOR_CHAT_BG, fg=COLOR_TEXT,
                                                   font=(FONT_FAMILY, FONT_SIZE), bd=1, padx=10, pady=10,
                                                   relief=tk.FLAT)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled')

        # Configurare Tag-uri: Indentarea este INVERSATĂ

        # AI: Default (fără indentare), font 8, italic, culoare AI
        self.text_area.tag_config('ai_style',
                                  foreground=COLOR_AI_TEXT,
                                  font=(FONT_FAMILY, 8, "italic"),
                                  justify='left')

        # OAMENI: Font 10, normal/bold, culoare, și Indentare 40px
        self.text_area.tag_config('user_indent',
                                  font=(FONT_FAMILY, FONT_SIZE),
                                  justify='left',
                                  lmargin1=40,
                                  lmargin2=40)

        # Mesaje de sistem (fără indentare)
        self.text_area.tag_config('sys_tag', foreground="#ff8a80", font=(FONT_FAMILY, 9), justify='left')

        # Mesajele tale (culoarea ta, bold, indentat)
        self.text_area.tag_config('me_tag', foreground=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE, "bold"))

        # Text bold (folosit pentru notificarea de alăturare)
        self.text_area.tag_config('bold', foreground=COLOR_TEXT, font=(FONT_FAMILY, FONT_SIZE, "bold"))

        # --- PREAMBUL SIMPLIFICAT ---
        self.text_area.config(state='normal')

        # Linia 1: Conectare, Ora, Rol AI, Model AI
        preambule_line = (
            f"Conectat la: {self.host_address}   "
            f"Oră conexiune: {self.connection_time}   "
            f"AI ROL: {self.current_ai_role}   "
            f"AI ACTIV: Necunoscut"  # Vom actualiza modelul la primirea primului mesaj SYS
        )
        self.text_area.insert('end', f"⚠ {preambule_line}\n", 'sys_tag')

        # Linia 2: Notificarea de alăturare
        self.text_area.insert('end', f"{self.nickname} s-a alăturat!\n", 'bold')
        self.text_area.config(state='disabled')

        # 4. Input Frame - Aici scriem
        input_frame = tk.Frame(self.win, bg=COLOR_CHAT_BG, pady=10, padx=10)
        input_frame.pack(fill='x', side='bottom')

        # Caseta de text (Input)
        self.input_area = tk.Entry(input_frame, bg="#3a3a3a", fg=COLOR_TEXT, font=(FONT_FAMILY, 11), relief="flat",
                                   bd=5)
        self.input_area.pack(side="left", fill='x', expand=True, padx=10)
        self.input_area.bind("<Return>", self.write)  # Trimite la apăsarea Enter

        # Buton "Trimite"
        tk.Button(input_frame, text="Trimite", bg=ACCENT_COLOR, fg=COLOR_BTN_TEXT, font=(FONT_FAMILY, 10, "bold"), bd=0,
                  padx=15,
                  pady=5, command=self.write).pack(side="right", padx=10)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        # Pornește thread-ul de primire mesaje în fundal
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.win.mainloop()

    # --- Funcții de Configurare Directă (pentru AI) ---
    # bla bla bla
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

    def send_word_limit_config(self, value):
        self.max_words = int(value)
        self.send_config("WORDS", str(self.max_words))

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
        # Aici ascultăm mesajele care vin de la server
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.text_area.config(state='normal')

                    if message.startswith("SYS:"):
                        # Mesaje de sistem
                        clean = message.replace("SYS:", "")
                        self.text_area.insert('end', f"⚠ {clean}\n", 'sys_tag')

                        # SINCRONIZARE: Actualizăm AI ACTIV în preambulul static
                        if "AI ACTIV:" in clean:
                            self.current_ai_model = clean.split("AI ACTIV: ")[1].strip()
                            # Notă: Preambulul nu poate fi ușor actualizat după inserare, dar variabila este setată.

                        # Alte sincronizări
                        if "PERSONALITATE SCHIMBATA ÎN:" in clean:
                            new_role = clean.split("PERSONALITATE SCHIMBATA ÎN: ")[1].strip()
                            self.current_ai_role = new_role
                            self.pers_combo.set(new_role)

                        if "LIMITA ISTORIC SETATĂ LA:" in clean:
                            new_limit = clean.split("LIMITA ISTORIC SETATĂ LA: ")[1].strip()
                            self.cache_combo.set(new_limit)

                        if "LIMITA CUVINTE AI SETATĂ LA:" in clean:
                            new_limit = clean.split("LIMITA CUVINTE AI SETATĂ LA: ")[1].strip()
                            try:
                                self.words_slider.set(int(new_limit))
                            except ValueError:
                                pass

                    elif "AI (" in message:
                        # Mesaj primit de la AI - FARA INDENTARE, stil AI (font 8, italic)
                        parts = message.split(":", 1)
                        if len(parts) > 1:
                            u_name = parts[0] + ":"
                            u_msg = parts[1]

                            # Aplicăm doar stilul AI (fără indentare)
                            self.text_area.insert('end', u_name, 'ai_style')
                            self.text_area.insert('end', u_msg + "\n", 'ai_style')

                            # Adăugăm o linie goală la sfârșit pentru a reseta contextul de formatare.
                            self.text_area.insert('end', "\n", 'sys_tag')

                        else:
                            # În cazul în care formatul nu este cel așteptat
                            self.text_area.insert('end', message + "\n", 'ai_style')

                    else:
                        # Mesaj primit de la un user - INDENTAT, stil utilizator (font 10)
                        if ":" in message:
                            parts = message.split(":", 1)
                            u_name = parts[0]
                            u_msg = parts[1]

                            if u_name not in self.user_tags:
                                # Dacă e un user nou, îi generăm o culoare unică
                                user_color = get_user_color(u_name)
                                self.user_tags[u_name] = user_color
                                self.text_area.tag_config(f'user_name_{u_name}', foreground=user_color,
                                                          font=(FONT_FAMILY, FONT_SIZE, "bold"))

                            # Aplicăm indentarea și stilul de text normal/bold pe întregul mesaj al utilizatorului
                            user_name_tag = f'user_name_{u_name}'
                            user_tags_combined = ('user_indent',)

                            if u_name == self.nickname:
                                # Mesaj de la tine
                                self.text_area.insert('end', f"{u_name}: ", 'me_tag', *user_tags_combined)
                                self.text_area.insert('end', u_msg + "\n", *user_tags_combined)
                            else:
                                # Mesaj de la alt user
                                self.text_area.insert('end', u_name + ": ", user_name_tag, *user_tags_combined)
                                self.text_area.insert('end', u_msg + "\n", *user_tags_combined)
                        else:
                            # Mesaj fără ':' (rar)
                            self.text_area.insert('end', message + "\n", 'user_indent')

                    # Derulează automat la ultimul mesaj
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except Exception as e:
                print(f"Eroare în thread-ul de primire: {e}")
                break


if __name__ == "__main__":
    ClientGui()