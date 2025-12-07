import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk, messagebox
import sys
import time

HOST = 'iulianddd.ddns.net'
PORT = 5555

COLOR_BG = "#f0f2f5"
COLOR_CHAT_BG = "#ffffff"
COLOR_TEXT = "#1c1e21"
COLOR_BTN = "#0084ff"
COLOR_BTN_TEXT = "#ffffff"
COLOR_AI = "#6c757d"
COLOR_USER = "#000000"

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

        # Apelam GUI loop direct din firul principal
        self.gui_loop()

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title(f"Team Chat - {self.nickname}")
        self.win.configure(bg=COLOR_BG)
        self.win.geometry("450x650")

        # 1. Conectare (Mutată aici, dar nu blochează mainloop încă)
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

        header = tk.Frame(self.win, bg="white", height=50)
        header.pack(fill='x', side='top')
        tk.Label(header, text="Echo Team Chat", font=("Helvetica", 12, "bold"), bg="white", fg=COLOR_TEXT).pack(pady=10)

        frame_chat = tk.Frame(self.win, bg=COLOR_BG, padx=10, pady=10)
        frame_chat.pack(expand=True, fill='both')

        self.text_area = scrolledtext.ScrolledText(frame_chat, bg=COLOR_CHAT_BG, fg=COLOR_TEXT, font=("Helvetica", 10),
                                                   bd=0, padx=10, pady=10)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state='disabled')

        self.text_area.tag_config('normal', font=("Helvetica", 10))
        self.text_area.tag_config('ai_tag', foreground=COLOR_AI, font=("Helvetica", 10, "italic"))
        self.text_area.tag_config('sys_tag', foreground="red", font=("Helvetica", 9))
        self.text_area.tag_config('me_tag', foreground=COLOR_BTN, font=("Helvetica", 10, "bold"))
        self.text_area.tag_config('bold', font=("Helvetica", 10, "bold"))

        self.text_area.config(state='normal')
        self.text_area.insert('end', f"⚠ Conectat la: {self.host_address}:{PORT}\n", 'sys_tag')
        self.text_area.insert('end', f"⚠ Oră conexiune: {self.connection_time}\n", 'sys_tag')
        self.text_area.insert('end', f"{self.nickname} s-a alăturat!\n", 'bold')
        self.text_area.config(state='disabled')

        input_frame = tk.Frame(self.win, bg="white", pady=10, padx=10)
        input_frame.pack(fill='x', side='bottom')

        tk.Button(input_frame, text="⚙", bg="#e4e6eb", fg="black", bd=0, padx=10, pady=5,
                  command=self.open_settings).pack(side="left", padx=(0, 5))

        self.input_area = tk.Entry(input_frame, bg="#f0f2f5", fg="black", font=("Helvetica", 11), relief="flat", bd=5)
        self.input_area.pack(side="left", fill='x', expand=True)
        self.input_area.bind("<Return>", self.write)

        tk.Button(input_frame, text="Trimite", bg=COLOR_BTN, fg="white", font=("Helvetica", 10, "bold"), bd=0, padx=15,
                  pady=5, command=self.write).pack(side="right", padx=(5, 0))

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        # MUTAT: Pornim firul de RECEIVE AICI
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.win.mainloop()  # Acesta ruleaza in firul principal

    def open_settings(self):
        # AICI NU MAI DA EROARE, deoarece variabila se creeaza in firul principal
        top = tk.Toplevel(self.win)
        top.title("Setări Agent AI")
        top.geometry("350x300")
        top.configure(bg="white")

        tk.Label(top, text="Alege Rolul AI:", font=("Helvetica", 10, "bold"), bg="white").pack(pady=(20, 5))

        self.pers_var = tk.StringVar(top, value=self.current_ai_role)  # Adaugam 'top' ca master
        combo = ttk.Combobox(top, textvariable=self.pers_var, values=PERSONALITIES, state="readonly", width=30)
        combo.pack(pady=5)

        tk.Label(top, text="Limitează Istoricul (Mesaje, 5-50):", font=("Helvetica", 10, "bold"), bg="white").pack(
            pady=(15, 5))

        self.cache_var = tk.StringVar(top, value="30")  # Adaugam 'top' ca master
        cache_input = tk.Entry(top, textvariable=self.cache_var, width=10)
        cache_input.pack(pady=5)

        tk.Button(top, text="Aplică Schimbarea", bg=COLOR_BTN, fg="white", bd=0, pady=5,
                  command=self.apply_all_settings).pack(pady=15)

    def apply_all_settings(self):
        pers_value = self.pers_var.get()
        self.send_config("PERS", pers_value)
        self.current_ai_role = pers_value

        try:
            cache_limit = int(self.cache_var.get())
            if 5 <= cache_limit <= 50:
                self.send_config("CACHE", str(cache_limit))
            else:
                messagebox.showerror("Eroare", "Limita de istoric trebuie să fie între 5 și 50.")
        except ValueError:
            messagebox.showerror("Eroare", "Limita de istoric trebuie să fie un număr întreg.")

        messagebox.showinfo("Info", "Configurația a fost actualizată.")

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
                            self.text_area.insert('end', role + ": ", 'ai_tag')
                            self.text_area.insert('end', msg + "\n", 'normal')
                        else:
                            self.text_area.insert('end', message + "\n", 'ai_tag')

                    else:
                        if ":" in message:
                            parts = message.split(":", 1)
                            u_name = parts[0]
                            u_msg = parts[1]

                            if u_name == self.nickname:
                                self.text_area.insert('end', f"{u_name}: ", 'me_tag')
                            else:
                                self.text_area.insert('end', u_name + ": ", 'bold')

                            self.text_area.insert('end', u_msg + "\n", 'normal')
                        else:
                            self.text_area.insert('end', message + "\n", 'normal')

                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except:
                break


if __name__ == "__main__":
    ClientGui()