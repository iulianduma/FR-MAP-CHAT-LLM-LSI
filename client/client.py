# -*- coding: utf-8 -*-
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

HOST = 'iulianddd.ddns.net'
PORT = 5555
APP_TITLE = "FR-MAP-CHAT-LLM-LSI"

# --- CONFIGURARE STIL ---
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10
COLOR_TEXT = "#ffffff"
COLOR_AI_TEXT = "#90caf9"
ACCENT_COLOR = "#4361ee"

CANDIDATE_THEMES = [
    "cosmo", "flatly", "journal", "literal", "lumen", "minty", "pulse",
    "superhero", "united", "yeti", "solar", "darkly", "cyborg", "vapor"
]

EMOTICON_MAP = {
    "Zambet": "😊", "Râs": "😃", "Cu ochiul": "😉", "Tristețe": "😞", "Neutru": "😐",
    "Foc": "🔥", "Bravo": "👍", "Nu e bine": "👎", "OK": "👌", "Salut": "👋",
    "Inimă": "❤️", "Stea": "⭐", "Sută": "💯", "Aplauze": "👏", "Lacrimi de Bucurie": "😂",
    "Ruga": "🙏", "Gânditor": "🤔", "Cool": "😎", "Plâns": "😢", "Supărat": "😠",
    "Cod": "💻", "Bug": "🐛", "Idee": "💡", "Unelte": "🛠️", "Bază de Date": "💾",
    "Euro": "💶", "Dolar": "💵", "Ceas": "⏰", "Rachetă": "🚀", "Petrecere": "🎉",
}
EMOTICON_LIST = [(v, k) for k, v in EMOTICON_MAP.items()]
EMOTICON_WIDTH_PX = 60

PERSONALITIES = [
    "Mediator Comic", "Receptor (Analist)", "Expert Juridic",
    "Evaluator Proiecte", "Expert HR", "Business Analist (BA)",
    "Expert Logistică"
]


# --- FUNCTII AJUTATOARE ---

def get_user_color(nickname):
    hash_object = hashlib.sha1(nickname.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    r = int(hex_dig[0:2], 16) % 100 + 155
    g = int(hex_dig[2:4], 16) % 100 + 155
    b = int(hex_dig[4:6], 16) % 100 + 155
    return f"#{r:02x}{g:02x}{b:02x}"


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


def filter_ai_text(text):
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[*_#`~>]+', '', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def replace_emoticons(text):
    for seq, emo in EMOTICON_MAP.items():
        text = text.replace(f":{emo.replace(' ', '_').lower()}:", emo)
    return text


class ClientGui:
    def __init__(self):
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

        self.gui_queue = queue.Queue()

        self.win = tb.Window(themename=self.current_theme)
        self.available_themes = self.filter_available_themes()
        self.win.withdraw()

        self.nickname = simpledialog.askstring("Autentificare", "Numele tău:", parent=self.win)

        if not self.nickname:
            self.win.destroy()
            sys.exit()

        self.gui_loop()

    def filter_available_themes(self):
        try:
            all_available_themes = self.win.style.theme_names()
            return [theme for theme in CANDIDATE_THEMES if theme in all_available_themes]
        except Exception:
            return [self.current_theme]

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

    def update_status_bar(self):
        if hasattr(self, 'status_label') and self.win.winfo_exists():
            status_text = (
                f"Sistem: {self.system_info['OS']} | "
                f"CPU: {self.system_info['CPU']} | "
                f"RAM: {self.system_info['RAM']} | "
                f"AI ROL: {self.current_ai_role} | "
                f"Model: {self.current_ai_model}"
            )
            self.status_label.config(text=status_text)

    def clear_chat_window(self):
        if messagebox.askyesno("Confirmare", "Sigur dorești să ștergi tot istoricul chat-ului?"):
            self.text_area.config(state='normal')
            self.text_area.delete('1.0', tk.END)
            self.text_area.config(state='disabled')

    def save_chat_log(self):
        try:
            chat_content = self.text_area.get("1.0", tk.END)
            if not chat_content.strip():
                messagebox.showinfo("Info", "Chat-ul este gol.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Salvează Log Chat",
                initialfile=f"chat_log_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(chat_content)
                messagebox.showinfo("Succes", f"Salvat în:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut salva:\n{e}")

    def insert_emoticon(self, emo):
        self.input_area.insert(tk.END, emo)

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

        for emo_symbol, emo_name in emoticons_to_draw:
            btn = ttk.Label(self.emo_frame, text=emo_symbol, font=(FONT_FAMILY, 24),
                            anchor='center', width=2, background=self.win.style.colors.bg)
            btn.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
            btn.bind('<Button-1>', lambda e, symbol=emo_symbol: self.insert_emoticon(symbol))
            # Tooltip-ul a fost eliminat de aici

        self.emo_frame.config(height=80)

    def on_window_resize(self, event):
        if event.widget == self.win:
            if event.width != self.last_win_width:
                self.last_win_width = event.width
                if self._resize_timer:
                    self.win.after_cancel(self._resize_timer)
                self._resize_timer = self.win.after(500, self.update_emoticon_layout)

    def toggle_emoticon_panel(self):
        self.emoticon_panel_visible = not self.emoticon_panel_visible
        if self.emoticon_panel_visible:
            self.emo_frame.pack(fill='x', side='bottom', padx=10, pady=5)
            self.win.after(10, self.update_emoticon_layout)
        else:
            self.emo_frame.pack_forget()

    def gui_loop(self):
        self.win.title(f"{APP_TITLE} - {self.nickname}")
        self.win.geometry("1500x750")
        self.win.deiconify()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(None)

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
            messagebox.showerror("Eroare", f"Nu m-am putut conecta la server!\n{e}")
            self.win.destroy()
            sys.exit()

        # UI Construction
        header = ttk.Frame(self.win)
        header.pack(fill='x', side='top')
        ttk.Label(header, text=f"{APP_TITLE} - {self.nickname}", font=(FONT_FAMILY, 12, "bold")).pack(pady=5)

        control_frame = ttk.Frame(self.win)
        control_frame.pack(fill='x', side='top', padx=10, pady=5)

        ttk.Label(control_frame, text="Tema:", font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.theme_var = tk.StringVar(self.win, value=self.current_theme)
        self.theme_combo = ttk.Combobox(control_frame, textvariable=self.theme_var, values=self.available_themes,
                                        state="readonly", width=12)
        self.theme_combo.pack(side="left", padx=(0, 20))
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        ttk.Label(control_frame, text="Rol AI:", font=(FONT_FAMILY, 10, "bold")).pack(side="left", padx=(0, 5))
        self.pers_var = tk.StringVar(self.win, value=self.current_ai_role)
        self.pers_combo = ttk.Combobox(control_frame, textvariable=self.pers_var, values=PERSONALITIES,
                                       state="readonly", width=20)
        self.pers_combo.pack(side="left", padx=(0, 15))
        self.pers_combo.bind("<<ComboboxSelected>>", self.send_pers_config)

        # Butoane Control (Dreapta Sus)
        self.ai_toggle_button = tb.Button(control_frame, text="AI ON", bootstyle="success",
                                          command=self.toggle_ai_state)
        self.ai_toggle_button.pack(side="right")

        tb.Button(control_frame, text="😄", bootstyle="secondary-outline", command=self.toggle_emoticon_panel,
                  width=5).pack(side="right", padx=(0, 5))

        tb.Button(control_frame, text="Salvează", bootstyle="success-outline", command=self.save_chat_log).pack(
            side="right", padx=(0, 5))

        tb.Button(control_frame, text="Curăță Chat", bootstyle="info", command=self.clear_chat_window).pack(
            side="right", padx=(15, 5))

        # Chat Area
        frame_chat = ttk.Frame(self.win)
        frame_chat.pack(expand=True, fill='both', padx=10, pady=10)

        self.text_area = scrolledtext.ScrolledText(frame_chat, fg=COLOR_TEXT, font=(FONT_FAMILY, FONT_SIZE),
                                                   bd=1, padx=10, pady=10, relief=tk.FLAT)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled', bg=self.win.style.colors.bg, wrap=tk.WORD)

        # Frame Emoticoane (Ascuns initial)
        self.emo_frame = ttk.Frame(self.win, height=80)
        self.win.bind("<Configure>", self.on_window_resize)

        # Tags
        self.normal_font = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        self.bold_font = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE, weight="bold")
        self.small_font = tkfont.Font(family=FONT_FAMILY, size=8)

        self.text_area.tag_config('ai_style', foreground=COLOR_TEXT, font=self.normal_font, justify='left')
        self.text_area.tag_config('normal', font=self.normal_font, justify='left')
        self.text_area.tag_config('sys_tag', foreground="#ff8a80", font=self.small_font, justify='left')
        self.text_area.tag_config('me_tag', foreground=ACCENT_COLOR, font=self.bold_font)
        self.text_area.tag_config('bold', foreground=COLOR_TEXT, font=self.bold_font)
        self.text_area.tag_config('tech_info', foreground="#80deea", font=self.small_font)

        # Status Bar
        self.status_label = ttk.Label(self.win, text="Se conectează...", anchor="w", font=(FONT_FAMILY, 8),
                                      bootstyle="inverse-secondary")
        self.status_label.pack(side="bottom", fill="x")
        self.update_status_bar()

        # Input Area
        input_frame = ttk.Frame(self.win)
        input_frame.pack(fill='x', side='bottom', pady=10, padx=10)
        self.input_area = tb.Entry(input_frame, bootstyle="primary", font=(FONT_FAMILY, 11))
        self.input_area.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        self.input_area.bind("<Return>", self.write)
        tb.Button(input_frame, text="Trimite", bootstyle="primary", command=self.write).pack(side=tk.RIGHT)

        # Pornire thread retea
        self.receive_thread = threading.Thread(target=self.receive, daemon=True)
        self.receive_thread.start()

        self.process_queue_loop()

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    # --- Procesare Coada (Thread Safety) ---
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

    def toggle_ai_state(self):
        self.is_ai_on = not self.is_ai_on
        if self.is_ai_on:
            self.ai_toggle_button.config(text="AI ON", bootstyle="success")
            self.send_config("AISTATE", "ON")
        else:
            self.ai_toggle_button.config(text="AI OFF", bootstyle="danger")
            self.send_config("AISTATE", "OFF")

    def send_pers_config(self, event=None):
        pers_value = self.pers_var.get()
        self.send_config("PERS", pers_value)
        self.current_ai_role = pers_value

    def send_cache_config(self, event=None):
        pass

    def send_word_limit_config(self, value):
        pass

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
                pass

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        self.win.destroy()
        sys.exit()

    def display_join_info(self, clean_message):
        parts = clean_message.split('|')
        info = {"IP": "N/A"}
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                info[key] = value
        nickname = info.get('NICKNAME', 'Anonim')
        tech_line = f"({info.get('IP')} | {info.get('CPU').split(' Processor')[0].strip()} | {info.get('OS')} | {info.get('RAM')})"

        self.text_area.insert('end', f"{nickname} s-a conectat! ", 'bold')
        self.text_area.insert('end', tech_line + "\n", 'tech_info')
        self.text_area.insert('end', "\n", 'sys_tag')

    def display_message(self, message):
        self.text_area.config(state='normal')

        # Mesaje de sistem
        if message.startswith("SYS:"):
            clean = message.replace("SYS:", "")
            if clean.startswith("JOIN_INFO:"):
                self.display_join_info(clean.replace("JOIN_INFO:", ""))
            else:
                if "AI ACTIV:" in clean:
                    self.current_ai_model = clean.split("AI ACTIV: ")[1].strip()
                elif "ROL INIȚIAL:" in clean or "PERSONALITATE SCHIMBATA ÎN:" in clean:
                    new_role = clean.split(": ")[1].strip()
                    self.current_ai_role = new_role
                    self.pers_combo.set(new_role)
                self.update_status_bar()
                if not clean.startswith("Oră conexiune:"):
                    self.text_area.insert('end', f"⚠ {clean}\n", 'sys_tag')

        # Mesaje AI
        elif "AI (" in message:
            parts = message.split(":", 1)
            if len(parts) > 1:
                u_name = parts[0] + ":"
                u_msg = parts[1]
                u_msg = filter_ai_text(u_msg)
                u_msg = replace_emoticons(u_msg)
                self.text_area.insert('end', u_name, 'ai_style')
                self.text_area.insert('end', u_msg + "\n", 'ai_style')
            else:
                self.text_area.insert('end', message + "\n", 'ai_style')

        # Mesaje User
        else:
            if ":" in message:
                parts = message.split(":", 1)
                u_name = parts[0]
                u_msg = parts[1]
                u_msg = replace_emoticons(u_msg)

                if u_name not in self.user_tags:
                    user_color = get_user_color(u_name)
                    self.user_tags[u_name] = user_color
                    self.text_area.tag_config(f'user_name_{u_name}', foreground=user_color, font=self.bold_font)

                user_name_tag = f'user_name_{u_name}'
                if u_name == self.nickname:
                    self.text_area.insert('end', f"{u_name}: ", 'me_tag')
                else:
                    self.text_area.insert('end', u_name + ": ", user_name_tag)
                self.text_area.insert('end', u_msg + "\n", 'normal')
            else:
                self.text_area.insert('end', message + "\n", 'normal')

        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                self.gui_queue.put(("MSG", message))
            except Exception as e:
                if self.running:
                    self.gui_queue.put(("DISCONNECT", str(e)))
                break

    def _handle_disconnection(self, error):
        self.text_area.config(state='normal')
        self.text_area.insert('end', "\n!!! EROARE CRITICĂ: Conexiunea cu serverul a fost pierdută.\n", 'sys_tag')
        self.text_area.config(state='disabled')
        self.running = False


if __name__ == "__main__":
    ClientGui()