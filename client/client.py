import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk
import random
import os
import ctypes
import requests

HOST = '127.0.0.1'
PORT = 5555

COLOR_BG = "#0d0d0d"  # Aproape negru
COLOR_FG = "#00ffff"  # Cyan Neon
COLOR_ACCENT = "#ff00ff"  # Magenta Neon
COLOR_AI = "#808080"  # Gri
FONT_NAME = "Poppins"

# Aceeasi lista ca pe server (doar cheile)
PERSONALITIES = [
    "Expert IT (Cortex)", "Expert Contabil", "Avocat Corporatist",
    "Project Manager", "Medic (Consultant)", "Expert CyberSecurity",
    "UX/UI Designer", "Data Scientist", "HR Manager", "Marketing Strategist",
    "Business Analyst", "DevOps Engineer", "Quality Assurance (QA)",
    "Startup Founder", "Profesor Istorie", "Psiholog Organizational",
    "Investitor VC", "Jurnalist Tech", "Consultant GDPR", "Expert Logistică"
]


def install_poppins():
    """Descarcă și instalează fontul temporar (Windows)"""
    font_path = os.path.join(os.getcwd(), "Poppins-Regular.ttf")
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf"
            r = requests.get(url, allow_redirects=True)
            with open(font_path, 'wb') as f:
                f.write(r.content)
        except:
            pass  # Folosim fallback

    try:
        if os.name == 'nt':
            ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
    except:
        pass


class ClientGui:
    def __init__(self):
        install_poppins()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
        except:
            print("Nu s-a putut conecta la server!")
            exit()

        msg = tk.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Login", "Nume utilizator:", parent=msg)
        if not self.nickname:
            self.nickname = f"User{random.randint(100, 999)}"

        self.gui_done = False
        self.running = True
        self.user_colors = {}  # Cache pentru culori useri

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def get_pastel_color(self):
        # Generam culori pastelate luminoase pentru contrast pe negru
        r = random.randint(150, 250)
        g = random.randint(150, 250)
        b = random.randint(150, 250)
        return f'#{r:02x}{g:02x}{b:02x}'

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title(f"Neon Pro Chat - {self.nickname}")
        self.win.configure(bg=COLOR_BG)
        self.win.geometry("600x750")

        # Configurare stiluri
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#2a2a2a", background=COLOR_ACCENT, foreground="white",
                        arrowcolor="white")

        # Header
        header_frame = tk.Frame(self.win, bg=COLOR_BG)
        header_frame.pack(fill='x', padx=20, pady=10)

        self.label_title = tk.Label(header_frame, text="AI TEAM CHAT", font=(FONT_NAME, 18, "bold"), bg=COLOR_BG,
                                    fg=COLOR_ACCENT)
        self.label_title.pack(side="left")

        status_dot = tk.Label(header_frame, text="● ONLINE", font=(FONT_NAME, 8), bg=COLOR_BG, fg="#00ff00")
        status_dot.pack(side="right", anchor="s")

        # Zona Chat
        self.text_area = scrolledtext.ScrolledText(self.win, bg="#111111", fg="white", font=(FONT_NAME, 10),
                                                   insertbackground="white", bd=0)
        self.text_area.pack(padx=20, pady=5, expand=True, fill='both')
        self.text_area.config(state='disabled')

        # Tag-uri stilizare
        self.text_area.tag_config('ai_style', foreground=COLOR_AI, font=(FONT_NAME, 10, 'italic'))
        self.text_area.tag_config('sys_style', foreground=COLOR_ACCENT, font=(FONT_NAME, 9, 'bold'))
        self.text_area.tag_config('self_style', foreground=COLOR_FG)

        # Zona Input
        input_frame = tk.Frame(self.win, bg=COLOR_BG)
        input_frame.pack(padx=20, pady=10, fill='x')

        self.input_area = tk.Entry(input_frame, bg="#222222", fg="white", font=(FONT_NAME, 11),
                                   insertbackground="white", relief="flat")
        self.input_area.pack(side="left", fill='x', expand=True, ipady=5)
        self.input_area.bind("<Return>", self.write)

        # Butoane
        btn_config = tk.Button(input_frame, text="⚙ SETĂRI", font=(FONT_NAME, 9, "bold"), bg="#333333", fg="white",
                               borderwidth=0, command=self.open_settings)
        btn_config.pack(side="left", padx=(10, 5))

        btn_send = tk.Button(input_frame, text="➤", font=(FONT_NAME, 12, "bold"), bg=COLOR_ACCENT, fg="black",
                             borderwidth=0, command=self.write)
        btn_send.pack(side="left")

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def open_settings(self):
        top = tk.Toplevel(self.win)
        top.title("Configurare AI")
        top.geometry("400x350")
        top.configure(bg=COLOR_BG)

        tk.Label(top, text="Alege Expertul AI:", font=(FONT_NAME, 12, "bold"), bg=COLOR_BG, fg="white").pack(
            pady=(20, 5))

        self.pers_var = tk.StringVar()
        self.pers_combo = ttk.Combobox(top, textvariable=self.pers_var, values=PERSONALITIES, state="readonly",
                                       font=(FONT_NAME, 10))
        self.pers_combo.current(0)
        self.pers_combo.pack(pady=5, padx=30, fill='x')

        tk.Button(top, text="Activează Expert", bg=COLOR_FG, fg="black", font=(FONT_NAME, 10, "bold"),
                  command=lambda: self.send_config("PERS", self.pers_var.get())).pack(pady=10)

        tk.Label(top, text="--- Retea ---", bg=COLOR_BG, fg="grey").pack(pady=10)

        tk.Label(top, text="Buffer Size:", font=(FONT_NAME, 10), bg=COLOR_BG, fg="white").pack()
        self.buff_var = tk.StringVar(value="1024")
        tk.Entry(top, textvariable=self.buff_var, bg="#222222", fg="white", justify="center").pack(pady=5)

        tk.Button(top, text="Update Buffer", bg="#333333", fg="white",
                  command=lambda: self.send_config("BUFF", self.buff_var.get())).pack(pady=5)

    def send_config(self, type, value):
        msg = f"CFG:{type}:{value}"
        self.sock.send(msg.encode('utf-8'))

    def write(self, event=None):
        txt = self.input_area.get()
        if txt:
            message = f"{self.nickname}: {txt}"
            self.sock.send(message.encode('utf-8'))
            self.input_area.delete(0, 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.text_area.config(state='normal')

                    if message.startswith("SYS:"):
                        clean_msg = message.replace("SYS:", "")
                        self.text_area.insert('end', f"█ {clean_msg}\n", 'sys_style')

                    elif "AI (" in message:
                        # Format AI: AI (Rol): Mesaj
                        self.text_area.insert('end', message + "\n", 'ai_style')

                    else:
                        # Format User: Nume: Mesaj
                        try:
                            parts = message.split(":", 1)
                            username = parts[0]
                            content = parts[1] if len(parts) > 1 else ""

                            if username not in self.user_colors:
                                self.user_colors[username] = self.get_pastel_color()

                            # Scriem numele cu culoare
                            self.text_area.insert('end', username, username)
                            self.text_area.tag_config(username, foreground=self.user_colors[username],
                                                      font=(FONT_NAME, 10, "bold"))

                            # Scriem mesajul normal
                            self.text_area.insert('end', f":{content}\n")
                        except:
                            self.text_area.insert('end', message + "\n")

                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except:
                break


client = ClientGui()