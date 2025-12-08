# -*- coding: utf-8 -*-
import socket
import threading
import customtkinter as ctk
from customtkinter import simpledialog, CTkTextbox, CTkLabel, CTkButton, CTkOptionMenu, CTkFrame
from tkinter import messagebox
import sys
import time
import hashlib

HOST = 'iulianddd.ddns.net'
PORT = 5555

# --- TEMĂ LIGHT MODE (CustomTkinter) ---
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 12

# Culori Light Mode (conform standardelor CTk)
BG_COLOR = "#ededed"  # Fundal fereastra
CHAT_BG_COLOR = "#ffffff"  # Fundal zona de chat
TEXT_COLOR = "#000000"  # Text negru
AI_TEXT_COLOR = "#6c757d"  # Gri (pentru citatul AI)

# Setată dinamic
ACCENT_COLOR = "#4361ee"


def get_user_color(nickname):
    """Generează o culoare pastelată unică pe baza numelui utilizatorului (pentru widget-urile de accent)."""
    hash_object = hashlib.sha1(nickname.encode('utf-8'))
    hex_dig = hash_object.hexdigest()

    # Asigură o culoare pastelată
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
        # Setăm tema CTk global la Light
        ctk.set_appearance_mode("Light")

        msg = ctk.CTk()
        msg.withdraw()

        self.nickname = simpledialog.ask_string("Autentificare", "Numele tău:", parent=msg)
        if not self.nickname:
            sys.exit()

        # Setăm culoarea de accent dinamică
        global ACCENT_COLOR
        ACCENT_COLOR = get_user_color(self.nickname)

        self.gui_done = False
        self.running = True

        self.host_address = HOST
        self.connection_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.current_ai_model = "Necunoscut"
        self.current_ai_role = "Expert IT (Cortex)"
        self.user_tags = {}

        self.gui_loop()

    def gui_loop(self):
        self.win = ctk.CTk()
        self.win.title(f"Team Chat - {self.nickname}")
        self.win.geometry("800x600")
        self.win.configure(fg_color=BG_COLOR)

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
        header = ctk.CTkFrame(self.win, fg_color="#f8f8f8", height=30, corner_radius=0)
        header.pack(fill='x', side='top')
        ctk.CTkLabel(header, text=f"Team Chat - {self.nickname}", font=(FONT_FAMILY, 14, "bold"),
                     text_color=TEXT_COLOR).pack(pady=5)

        # 2. Control Frame (Dropdowns)
        control_frame = ctk.CTkFrame(self.win, fg_color=BG_COLOR, height=40, corner_radius=0)
        control_frame.pack(fill='x', side='top', padx=10, pady=(5, 0))

        # --- Dropdown Personalitate ---
        ctk.CTkLabel(control_frame, text="Rol AI:", fg_color=BG_COLOR, text_color=TEXT_COLOR,
                     font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.pers_var = ctk.StringVar(self.win, value=self.current_ai_role)
        self.pers_combo = ctk.CTkOptionMenu(control_frame, variable=self.pers_var, values=PERSONALITIES,
                                            command=self.send_pers_config, width=180,
                                            fg_color=ACCENT_COLOR, button_color=ACCENT_COLOR,
                                            button_hover_color=ACCENT_COLOR)
        self.pers_combo.pack(side="left", padx=(0, 20))

        # --- Dropdown Istoric Mesaje ---
        CACHE_OPTIONS = [str(i) for i in range(5, 51, 5)]
        ctk.CTkLabel(control_frame, text="Istoric Mesaje:", fg_color=BG_COLOR, text_color=TEXT_COLOR,
                     font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.cache_var = ctk.StringVar(self.win, value="30")
        self.cache_combo = ctk.CTkOptionMenu(control_frame, variable=self.cache_var, values=CACHE_OPTIONS,
                                             command=self.send_cache_config, width=60,
                                             fg_color=ACCENT_COLOR, button_color=ACCENT_COLOR,
                                             button_hover_color=ACCENT_COLOR)
        self.cache_combo.pack(side="left")

        # 3. Chat Area
        frame_chat = ctk.CTkFrame(self.win, fg_color=BG_COLOR, corner_radius=0)
        frame_chat.pack(expand=True, fill='both', padx=10, pady=10)

        # CTkTextbox - Note: Nu suportă tag-uri!
        self.text_area = ctk.CTkTextbox(frame_chat, fg_color=CHAT_BG_COLOR, text_color=TEXT_COLOR,
                                        font=(FONT_FAMILY, FONT_SIZE), activate_scrollbars=True, wrap="word")
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)
        self.text_area.configure(state='disabled')

        # Mesaje inițiale
        self.text_area.configure(state='normal')
        self.text_area.insert("end", f"⚠ Conectat la: {self.host_address}:{PORT}\n", "sys_tag")
        self.text_area.insert("end", f"⚠ Oră conexiune: {self.connection_time}\n", "sys_tag")
        self.text_area.insert("end", f"*** {self.nickname} s-a alăturat! ***\n\n", "bold")
        self.text_area.configure(state='disabled')

        # 4. Input Frame
        input_frame = ctk.CTkFrame(self.win, fg_color="#f8f8f8", height=50, corner_radius=0)
        input_frame.pack(fill='x', side='bottom', padx=10, pady=(0, 10))

        self.input_area = ctk.CTkEntry(input_frame, fg_color=CHAT_BG_COLOR, text_color=TEXT_COLOR,
                                       font=(FONT_FAMILY, 11),
                                       placeholder_text="Scrie un mesaj...", height=35)
        self.input_area.pack(side="left", fill='x', expand=True, padx=10)
        self.input_area.bind("<Return>", self.write)

        # Buton cu culoarea dinamică a utilizatorului
        ctk.CTkButton(input_frame, text="Trimite", fg_color=ACCENT_COLOR, text_color=TEXT_COLOR,
                      hover_color=ACCENT_COLOR, font=(FONT_FAMILY, 10, "bold"), width=80,
                      command=self.write).pack(side="right", padx=10)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.win.mainloop()

    # --- Funcții de Configurare Directă ---
    def send_pers_config(self, value):  # Primește valoarea de la CTkOptionMenu
        self.send_config("PERS", value)
        self.current_ai_role = value

    def send_cache_config(self, value):  # Primește valoarea de la CTkOptionMenu
        try:
            cache_limit = int(value)
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
                self.text_area.configure(state='normal')
                self.text_area.insert("end", "Eroare conexiune!\n")
                self.text_area.configure(state='disabled')

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
                    self.text_area.configure(state='normal')

                    if message.startswith("SYS:"):
                        clean = message.replace("SYS:", "")
                        self.text_area.insert("end", f"⚠ {clean}\n\n", "sys_tag")

                        # --- SINCRONIZARE ---
                        if "PERSONALITATE SCHIMBATA ÎN:" in clean:
                            new_role = clean.split("PERSONALITATE SCHIMBATA ÎN: ")[1].strip()
                            self.current_ai_role = new_role
                            self.pers_combo.set(new_role)  # Actualizează Combobox

                        if "LIMITA ISTORIC SETATĂ LA:" in clean:
                            new_limit = clean.split("LIMITA ISTORIC SETATĂ LA: ")[1].strip()
                            self.cache_var.set(new_limit)  # Actualizează Combobox

                        if "AI ACTIV:" in clean:
                            self.current_ai_model = clean.split("AI ACTIV: ")[1].strip()
                        if "ROL INIȚIAL:" in clean:
                            self.current_ai_role = clean.split("ROL INIȚIAL: ")[1].strip()

                    elif "AI (" in message:
                        # Formatare AI (Gri, Italic - folosind o setare fixă de font)
                        parts = message.split("): ", 1)
                        role = parts[0] + "): "
                        msg = parts[1] if len(parts) > 1 else ""

                        # Inserăm cu culoarea AI și stilul italic pentru întregul bloc
                        self.text_area.insert("end", role, (FONT_FAMILY, FONT_SIZE, "italic"), text_color=AI_TEXT_COLOR)
                        self.text_area.insert("end", msg + "\n\n", (FONT_FAMILY, FONT_SIZE, "italic"),
                                              text_color=AI_TEXT_COLOR)

                    else:
                        # Formatare Utilizator (Folosim doar Text Color, fără culori pastelate individuale)
                        if ":" in message:
                            parts = message.split(":", 1)
                            u_name = parts[0]
                            u_msg = parts[1]

                            # Utilizatorii vor avea text normal (negru/TEXT_COLOR)
                            self.text_area.insert("end", u_name + ": ", (FONT_FAMILY, FONT_SIZE, "bold"))
                            self.text_area.insert("end", u_msg + "\n\n")
                        else:
                            self.text_area.insert("end", message + "\n\n")

                    self.text_area.see("end")  # Scrollează la final
                    self.text_area.configure(state='disabled')
            except:
                break


if __name__ == "__main__":
    ClientGui()