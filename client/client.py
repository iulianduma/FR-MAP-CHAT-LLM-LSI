# -*- coding: utf-8 -*-
# Aici aducem uneltele necesare: pentru internet (socket), pentru a face mai multe lucruri deodată (threading) și pentru ferestre (tkinter).
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, filedialog, font as tkfont
import sys
import time
import hashlib
import platform
import psutil
import os
import re
import queue
import ttkbootstrap as tb
from tkinter import ttk

# Acestea sunt setările principale: adresa serverului, mărimea literelor și culorile de bază.
HOST = 'iulianddd.ddns.net'
PORT = 5555
APP_TITLE = "FR-MAP-CHAT-LLM-LSI"
FONT_FAMILY = "Roboto"
FONT_SIZE = 11
COLOR_TEXT = "#ffffff"
ACCENT_COLOR = "#4361ee"

# Aici avem dicționarul care știe să transforme un nume în simbolul grafic corespunzător (emoticon).
EMOTICON_MAP = {
    "Zambet": "😊", "Râs": "😃", "Cu ochiul": "😉", "Tristețe": "😞", "Neutru": "😐",
    "Foc": "🔥", "Bravo": "👍", "Nu e bine": "👎", "OK": "👌", "Salut": "👋",
    "Inimă": "❤️", "Stea": "⭐", "Sută": "💯", "Aplauze": "👏", "Lacrimi de Bucurie": "😂",
    "Ruga": "🙏", "Gânditor": "🤔", "Cool": "😎", "Plâns": "😢", "Supărat": "😠",
    "Cod": "💻", "Bug": "🐛", "Idee": "💡", "Unelte": "🛠️", "Bază de Date": "💾",
    "Euro": "💶", "Dolar": "💵", "Ceas": "⏰", "Rachetă": "🚀", "Petrecere": "🎉",
}
EMOTICON_LIST = [(v, k) for k, v in EMOTICON_MAP.items()]
EMOTICON_WIDTH_PX = 75  # Spațiul pe care îl ocupă fiecare emoticon pe ecran.

# Rolurile pe care le poate lua inteligența artificială în acest chat.
PERSONALITIES = [
    "Mediator Comic", "Receptor (Analist)", "Expert Juridic",
    "Evaluator Proiecte", "Expert HR", "Business Analist (BA)",
    "Expert Logistică"
]

# Această funcție calculează o culoare unică pentru fiecare nume, astfel încât fiecare utilizator să aibă culoarea lui.
def get_user_color(nickname):
    hash_object = hashlib.sha1(nickname.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    r = int(hex_dig[0:2], 16) % 100 + 155
    g = int(hex_dig[2:4], 16) % 100 + 155
    b = int(hex_dig[4:6], 16) % 100 + 155
    return f"#{r:02x}{g:02x}{b:02x}"

# Verifică specificațiile calculatorului tău: ce sistem de operare ai, ce procesor și câtă memorie RAM.
def get_system_info():
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

# Curăță textul de la inteligența artificială de semne inutile (precum steluțe sau linii) pentru a fi mai ușor de citit.
def filter_ai_text(text):
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[*_#`~>]+', '', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

# Caută în text anumite cuvinte și le transformă în emoticonele desenate mai sus.
def replace_emoticons(text):
    for seq, emo in EMOTICON_MAP.items():
        text = text.replace(f":{emo.replace(' ', '_').lower()}:", emo)
    return text

# Aceasta este partea principală a programului care gestionează fereastra și conversația.
class ClientGui:
    def __init__(self):
        # Aici pregătim datele de pornire, inclusiv informațiile despre sistem și lista de mesaje.
        self.system_info = get_system_info()
        self.running = True
        self.current_ai_role = PERSONALITIES[0]
        self.current_ai_model = "Necunoscut"
        self.is_ai_on = True
        self.user_tags = {}
        self.max_words = 50
        self.current_theme = "darkly"
        self.emoticon_panel_visible = False
        self._resize_timer = None
        self.last_win_width = 0

        # Creăm o listă de așteptare pentru mesaje și fereastra principală.
        self.gui_queue = queue.Queue()
        self.win = tb.Window(themename=self.current_theme)
        self.available_themes = self.filter_available_themes()
        self.win.withdraw()

        # Întrebăm utilizatorul cum îl cheamă înainte de a intra în chat.
        self.nickname = simpledialog.askstring("Autentificare", "Numele tău:", parent=self.win)
        if not self.nickname:
            self.win.destroy()
            sys.exit()

        self.gui_loop()

    # Verifică ce stiluri vizuale (teme) sunt instalate și pot fi folosite.
    def filter_available_themes(self):
        try:
            all_installed = self.win.style.theme_names()
            complet_list = [
                "cosmo", "flatly", "journal", "literal", "lumen", "minty",
                "pulse", "superhero", "united", "yeti", "solar", "darkly",
                "cyborg", "vapor"
            ]
            return [t for t in complet_list if t in all_installed]
        except Exception:
            return [self.current_theme]

    # Schimbă culorile și aspectul ferestrei atunci când alegi o altă temă.
    def change_theme(self, event=None):
        new_theme = self.theme_var.get()
        if new_theme in self.available_themes:
            try:
                self.win.style.theme_use(new_theme)
                self.current_theme = new_theme
                self.text_area.config(bg=self.win.style.colors.bg)
                self.update_status_bar()
                if self.emoticon_panel_visible:
                    self.update_emoticon_layout()
            except Exception:
                pass

    # Actualizează rândul de jos al ferestrei cu informații despre calculator și rolul AI-ului.
    def update_status_bar(self):
        if hasattr(self, 'status_label') and self.win.winfo_exists():
            status_text = (
                f"Sistem: {self.system_info['OS']} | "
                f"CPU: {self.system_info['CPU']} | "
                f"RAM: {self.system_info['RAM']} | "
                f"AI ROL: {self.current_ai_role}"
            )
            self.status_label.config(text=status_text)

    # Șterge tot ce scrie în zona de mesaje dacă apeși butonul de curățare.
    def clear_chat_window(self):
        if messagebox.askyesno("Confirmare", "Sigur dorești să ștergi tot istoricul chat-ului?"):
            self.text_area.config(state='normal')
            self.text_area.delete('1.0', tk.END)
            self.text_area.config(state='disabled')

    # Salvează toată conversația într-un fișier text pe calculatorul tău.
    def save_chat_log(self):
        try:
            chat_content = self.text_area.get("1.0", tk.END)
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvează Log Chat")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(chat_content)
                messagebox.showinfo("Succes", "Log salvat.")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la salvare: {e}")

    # Pune un emoticon în câmpul unde scrii mesajul.
    def insert_emoticon(self, emo):
        self.input_area.insert(tk.END, emo)

    # Desenează butoanele cu fețe zâmbitoare și le așează în funcție de cât de lată este fereastra.
    def update_emoticon_layout(self):
        if not self.emoticon_panel_visible or not self.win.winfo_exists():
            return
        try:
            current_width = self.emo_frame.winfo_width()
            if current_width < 50: current_width = self.win.winfo_width()
        except:
            return

        max_emoticons = int(current_width / EMOTICON_WIDTH_PX)
        if max_emoticons < 1: max_emoticons = 1
        for widget in self.emo_frame.winfo_children():
            widget.destroy()

        emoticons_to_draw = EMOTICON_LIST[:max_emoticons]

        emo_colors = {
            "Inimă": "#ff4d4d", "Foc": "#ff9800", "Stea": "#ffeb3b",
            "Bravo": "#4caf50", "Cod": "#00e5ff", "Idee": "#ffeb3b"
        }

        for emo_symbol, emo_name in emoticons_to_draw:
            color = emo_colors.get(emo_name, "#ffffff")
            btn = tk.Label(self.emo_frame, text=emo_symbol,
                           font=("Segoe UI Emoji", 22),
                           anchor='center',
                           background=self.win.style.colors.bg,
                           foreground=color,
                           cursor="hand2")
            btn.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=15)
            btn.bind('<Button-1>', lambda e, symbol=emo_symbol: self.insert_emoticon(symbol))

        self.emo_frame.config(height=100)

    # Dacă tragi de marginea ferestrei să o mărești, recalculează așezarea elementelor după o scurtă pauză.
    def on_window_resize(self, event):
        if event.widget == self.win:
            if event.width != self.last_win_width:
                self.last_win_width = event.width
                if self._resize_timer:
                    self.win.after_cancel(self._resize_timer)
                self._resize_timer = self.win.after(500, self.update_emoticon_layout)

    # Arată sau ascunde panoul cu emoticoane.
    def toggle_emoticon_panel(self):
        self.emoticon_panel_visible = not self.emoticon_panel_visible
        if self.emoticon_panel_visible:
            self.emo_frame.pack(fill='x', side='bottom', padx=10, pady=5)
            self.win.after(10, self.update_emoticon_layout)
        else:
            self.emo_frame.pack_forget()

    # Aici construim vizual toată fereastra: titlu, butoane, zona de scris și zona de mesaje.
    def gui_loop(self):
        self.win.title(f"{APP_TITLE} - {self.nickname}")
        self.win.geometry("600x900")
        self.win.deiconify()

        # Încercăm să ne conectăm la serverul de chat prin internet.
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(None)

            # Trimitem datele noastre tehnice către server imediat ce ne-am conectat.
            info_message = f"SYS:JOIN_INFO:{self.nickname}|OS:{self.system_info['OS']}|CPU:{self.system_info['CPU']}|RAM:{self.system_info['RAM']}"
            self.sock.send(info_message.encode('utf-8'))
            self.update_status_bar()

        except Exception as e:
            messagebox.showerror("Eroare", f"Nu m-am putut conecta la server!\n{e}")
            self.win.destroy()
            sys.exit()

        # Construim butoanele de sus pentru temă, rolul AI-ului și curățare chat.
        header = ttk.Frame(self.win)
        header.pack(fill='x', side='top')

        control_frame = ttk.Frame(self.win)
        control_frame.pack(fill='x', side='top', padx=10, pady=5)

        self.theme_var = tk.StringVar(self.win, value=self.current_theme)
        self.theme_combo = ttk.Combobox(control_frame, textvariable=self.theme_var, values=self.available_themes,
                                        state="readonly", width=12)
        self.theme_combo.pack(side="left", padx=(0, 20))
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        self.pers_var = tk.StringVar(self.win, value=self.current_ai_role)
        self.pers_combo = ttk.Combobox(control_frame, textvariable=self.pers_var, values=PERSONALITIES,
                                       state="readonly", width=20)
        self.pers_combo.pack(side="left", padx=(0, 15))
        self.pers_combo.bind("<<ComboboxSelected>>", self.send_pers_config)

        self.ai_toggle_button = tb.Button(control_frame, text="AI ON", bootstyle="success",
                                          command=self.toggle_ai_state)
        self.ai_toggle_button.pack(side="right")

        tb.Button(control_frame, text="😄", bootstyle="secondary-outline", command=self.toggle_emoticon_panel,
                  width=5).pack(side="right", padx=(0, 5))
        tb.Button(control_frame, text="Curăță Chat", bootstyle="info", command=self.clear_chat_window).pack(
            side="right", padx=(15, 5))

        # Aceasta este zona mare unde apar toate mesajele.
        frame_chat = ttk.Frame(self.win)
        frame_chat.pack(expand=True, fill='both', padx=10, pady=10)

        self.text_area = scrolledtext.ScrolledText(frame_chat, fg=COLOR_TEXT, font=(FONT_FAMILY, FONT_SIZE), bd=1,
                                                   padx=10, pady=10, relief=tk.FLAT)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled', bg=self.win.style.colors.bg, wrap=tk.WORD)

        self.emo_frame = ttk.Frame(self.win, height=100)
        self.win.bind("<Configure>", self.on_window_resize)

        # Pregătim stilurile pentru scris: îngroșat, colorat sau mic pentru informații tehnice.
        self.bold_font = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE, weight="bold")
        self.text_area.tag_config('sys_tag', foreground="#ff8a80", font=(FONT_FAMILY, 8))
        self.text_area.tag_config('me_tag', foreground=ACCENT_COLOR, font=self.bold_font)

        # Bara de jos care arată dacă ești conectat.
        self.status_label = ttk.Label(self.win, text="Se conectează...", anchor="w", font=(FONT_FAMILY, 8),
                                      bootstyle="inverse-secondary")
        self.status_label.pack(side="bottom", fill="x")

        # Zona de jos unde scrii mesajul propriu-zis.
        input_frame = ttk.Frame(self.win)
        input_frame.pack(fill='x', side='bottom', pady=10, padx=10)
        self.input_area = tb.Entry(input_frame, bootstyle="primary", font=(FONT_FAMILY, 11))
        self.input_area.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        self.input_area.bind("<Return>", self.write)
        tb.Button(input_frame, text="Trimite", bootstyle="primary", command=self.write).pack(side=tk.RIGHT)

        # Pornim un proces separat care stă și "ascultă" dacă primim mesaje noi de pe internet.
        self.receive_thread = threading.Thread(target=self.receive, daemon=True)
        self.receive_thread.start()
        self.process_queue_loop()

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    # Verifică periodic dacă au apărut mesaje noi în "lista de așteptare" și le afișează pe ecran.
    def process_queue_loop(self):
        try:
            while True:
                msg_type, content = self.gui_queue.get_nowait()
                if msg_type == "MSG":
                    self.display_message(content)
                elif msg_type == "DISCONNECT":
                    self._handle_disconnection(content)
        except queue.Empty:
            pass
        if self.running:
            self.win.after(100, self.process_queue_loop)

    # Pornește sau oprește inteligența artificială pentru acest chat.
    def toggle_ai_state(self):
        self.is_ai_on = not self.is_ai_on
        state = "ON" if self.is_ai_on else "OFF"
        self.ai_toggle_button.config(text=f"AI {state}", bootstyle="success" if self.is_ai_on else "danger")
        self.send_config("AISTATE", state)

    # Spune serverului ce personalitate ai ales pentru AI.
    def send_pers_config(self, event=None):
        pers_value = self.pers_var.get()
        self.send_config("PERS", pers_value)
        self.current_ai_role = pers_value

    # Trimite setări tehnice către server.
    def send_config(self, type, value):
        try:
            self.sock.send(f"CFG:{type}:{value}".encode('utf-8'))
        except:
            pass

    # Ia textul scris de tine în căsuță și îl trimite prin internet către ceilalți.
    def write(self, event=None):
        txt = self.input_area.get()
        if txt:
            try:
                self.sock.send(f"{self.nickname}:{txt}".encode('utf-8'))
                self.input_area.delete(0, 'end')
            except:
                pass

    # Închide conexiunea și oprește programul.
    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        self.win.destroy()
        sys.exit()

    # Această funcție decide cum să arate fiecare mesaj: dacă e de sistem, de la AI sau de la un prieten.
    def display_message(self, message):
        self.text_area.config(state='normal')

        # Ignoră mesajele automate de rețea care nu sunt utile pentru utilizator.
        if "', " in message and any(char.isdigit() for char in message):
            self.text_area.config(state='disabled')
            return

        # Mesajele de sistem (ex: cineva s-a conectat) apar cu un semn de atenție.
        if message.startswith("SYS:"):
            clean = message.replace("SYS:", "")
            for key in ["CONECTAT LA SERVER", "AI ACTIV:", "ROL INIȚIAL:", "ROL:", "JOIN_INFO:"]:
                clean = clean.replace(key, f"\n{key}")
            if "AI ACTIV:" in clean:
                self.current_ai_model = clean.split("AI ACTIV:")[1].split('\n')[0].strip()
            if "ROL INIȚIAL:" in clean:
                self.current_ai_role = clean.split("ROL INIȚIAL:")[1].split('\n')[0].strip()
            self.update_status_bar()
            self.text_area.insert('end', f"⚠ {clean.strip()}\n", 'sys_tag')

        # Mesajele normale de chat: pune numele persoanei, culoarea ei și apoi mesajul.
        else:
            if ":" in message:
                u_name, u_msg = message.split(":", 1)
                u_msg = replace_emoticons(u_msg)
                tag = 'me_tag' if u_name == self.nickname else 'normal'

                if u_name not in self.user_tags:
                    color = get_user_color(u_name)
                    self.user_tags[u_name] = color
                    self.text_area.tag_config(f'user_{u_name}', foreground=color, font=self.bold_font)

                final_tag = 'me_tag' if u_name == self.nickname else f'user_{u_name}'
                self.text_area.insert('end', f"{u_name}: ", final_tag)
                self.text_area.insert('end', f"{u_msg}\n", 'normal')
            else:
                self.text_area.insert('end', f"{message}\n", 'normal')

        # Mută automat vizualizarea la ultimul mesaj primit.
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    # Aceasta funcție rulează mereu în fundal și primește datele care vin de pe internet.
    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message:
                    self.gui_queue.put(("MSG", message))
            except:
                if self.running:
                    self.gui_queue.put(("DISCONNECT", "Eroare rețea"))
                break

    # Anunță utilizatorul dacă s-a pierdut conexiunea cu serverul.
    def _handle_disconnection(self, error):
        self.text_area.config(state='normal')
        self.text_area.insert('end', f"\n!!! EROARE: {error}\n", 'sys_tag')
        self.text_area.config(state='disabled')
        self.running = False

# Punctul de start: aici pornește aplicația.
if __name__ == "__main__":
    ClientGui()