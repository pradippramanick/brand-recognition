import tkinter as tk
import customtkinter as ctk # type: ignore
from PIL import Image
from tkinter import messagebox

import subprocess
import threading
import time

from controller import Controller
from vad import Vad
from listener import Listener

class OperatorApp(ctk.CTk, Listener):
    def __init__(self):
        super().__init__()

        self.title("Riconoscitore vocale di brand")
        self.geometry("1920x1080")
        self.minsize(1067, 600)
        ctk.set_appearance_mode("light")

        self.colors = {
            "background": "#EDF6F9",    # sfondo
            "text_white": "#FFFFFF",    # bianco
            "button": "#006D77",        # blu
            "hover": "#01555D",         # blu scuro
            "primary": "#83C5BE",       # blu chiaro
            "error": "#C00000",         # rosso
            "closing": "BF9FF6",        # viola chiaro
            "listening": "F35A89",      # rosa
            "sent": "#BADE78",          # verde
            "processing": "#F4E784",    # giallo
            "confirm": "#C860C1"        # viola scuro
        }

        self.configure(fg_color=self.colors.get("background"))
        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.controller = None
        self.conn = None
        self.vad = None
        self.vad_thread = None
        self.pavucontrol = None

        self.connection_page()

    def connection_page(self):
        self.clear_screen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        frame_label = ctk.CTkFrame(master=self, fg_color="transparent")
        frame_label.grid(row=0, column=0, padx=(200, 0), pady=(70, 0), sticky='nsew')

        frame_img = ctk.CTkFrame(master=self, fg_color="transparent")
        frame_img.grid(row=1, column=0, padx=(0, 200), sticky='nsew')

        sidebar = ctk.CTkFrame(master=frame_label, width=15, fg_color=self.colors.get("primary"))
        sidebar.grid(row=0, column=0, sticky='nsw')

        string_var = tk.StringVar()
        string_var.set("connessione...")
        
        label_conn = ctk.CTkLabel(master=frame_label, textvariable=string_var, font=("Inter Display Thin", 64))
        label_conn.grid(row=0, column=1, padx=20, sticky='nsw')

        self.controller = Controller()
        self.conn = self.controller.connect()

        if self.conn:
            msg = self.controller.rec()
            if msg == "SERVER_SHUTDOWN":
                self.error_page(string_var, "Impossibile connettersi:\nil server è in chiusura", frame_img)
            elif msg == "ACCEPTED":
                self.controller.send("operator")
                self.login_page()
        else:
            self.error_page(string_var, "Impossibile connettersi:\nil server è spento", frame_img)

    def error_page(self, string_var, error_msg, frame_img):
        string_var.set(error_msg)
        
        image_path = "img/server_off.png"
        image_pil = Image.open(image_path)
        image = ctk.CTkImage(image_pil, size=(347, 321))

        frame_img.grid_rowconfigure(0, weight=1)
        frame_img.grid_columnconfigure(0, weight=1)

        image_label = ctk.CTkLabel(master=frame_img, image=image, text="")
        image_label.grid(row=0, column=0, sticky='nse')
        
    def login_page(self, init_vad=True):
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.clear_screen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        label = ctk.CTkLabel(master=self, text="Effettua l'accesso\ncome operatore", font=("Inter", 64))
        label.grid(row=0, column=0)

        self.login_frame = ctk.CTkFrame(master=self, fg_color=self.colors.get("primary"), corner_radius=25)
        self.login_frame.grid(row=1, column=0)
        
        code_label = ctk.CTkLabel(master=self.login_frame, text="codice:", font=("Inter Display Thin", 32))
        code_label.grid(row=0, column=0, pady=(25, 0), padx=25, sticky='w')

        self.code_entry = ctk.CTkEntry(master=self.login_frame, font=("Inter", 20), width=500, height=52,corner_radius=15, placeholder_text="codice")
        self.code_entry.grid(row=1, column=0, padx=25)

        self.code_error_str = tk.StringVar()
        self.code_error_str.set("")
        code_error_label = ctk.CTkLabel(master=self.login_frame, textvariable=self.code_error_str, font=("Display", 14), text_color=self.colors.get("error"))
        code_error_label.grid(row=2, column=0, pady=(0, 15))
        
        cart_label = ctk.CTkLabel(master=self.login_frame, text="carrello:", font=("Inter Display Thin", 32))
        cart_label.grid(row=3, column=0, padx=25, sticky='w')
        
        num_cart = int(self.controller.rec())
        values = []
        for i in range(1, num_cart + 1):
            values.append(f"{i}")
        self.cart_menu = ctk.CTkComboBox(master=self.login_frame, font=("Inter", 20), width=500, height=52, corner_radius=15, values=values, dropdown_font=("Inter", 20))
        self.cart_menu.grid(row=4, column=0)

        self.cart_error_str = tk.StringVar()
        self.cart_error_str.set("")
        cart_error_label = ctk.CTkLabel(master=self.login_frame, textvariable=self.cart_error_str, font=("Display", 14), text_color=self.colors.get("error"))
        cart_error_label.grid(row=5, column=0, pady=(0, 20))

        submit_button = ctk.CTkButton(master=self.login_frame, text="  Accedi  ", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=lambda: self.login(init_vad))
        submit_button.grid(row=6, column=0, pady=(0, 25))
        

    def login(self, init_vad):
        self.operator_code = self.code_entry.get()
        self.operator_cart = self.cart_menu.get()

        self.code_entry.configure(border_color=ctk.ThemeManager.theme["CTkEntry"]["border_color"])
        self.cart_menu.configure(border_color=ctk.ThemeManager.theme["CTkEntry"]["border_color"])

        self.code_error_str.set("")
        self.cart_error_str.set("")

        if not self.operator_code:
            self.operator_code = "\n\nNONE\n\n"
        if not self.operator_cart:
            self.operator_cart = "\n\nNONE\n\n"
        
        res = self.controller.check_data(self.operator_code, self.operator_cart)
        code_valid = res.get("code") # todo sometimes crashes AttributeError: 'list' object has no attribute 'get'
        cart_valid = res.get("cart")

        if code_valid == "none":
            self.code_entry.configure(border_color="red")
            self.code_error_str.set("Inserire codice")
        elif code_valid == "already logged":
            self.code_entry.configure(border_color="red")
            self.code_error_str.set("Operatore già connesso")
        elif code_valid == "not exists":
            self.code_entry.configure(border_color="red")
            self.code_error_str.set("Codice non esistente")

        if cart_valid == "none":
            self.cart_menu.configure(border_color="red")
            self.cart_error_str.set("Inserire carrello")
        elif cart_valid == "already logged":
            self.cart_menu.configure(border_color="red")
            self.cart_error_str.set("Carrello già in uso")
        elif cart_valid == "not int":
            self.cart_menu.configure(border_color="red")
            self.cart_error_str.set("Inserire un numero")
        elif cart_valid == "out of range":
            self.cart_menu.configure(border_color="red")
            self.cart_error_str.set("Carrello non disponibile")
        else:
            if cart_valid != "ok":
                try:
                    new_cart = int(cart_valid)
                except Exception:
                    self.cart_menu.configure(border_color="red")
                    self.cart_error_str.set("Errore server. Riprovare")
                values = []
                for i in range(1, new_cart + 1):
                    values.append(f"{i}")
                self.cart_menu.configure(values=values)
                self.cart_menu.configure(border_color="red")
                self.cart_error_str.set("Il numero di carrelli è stato modificato dall'admin. Riprovare")

        if code_valid  == "ok" and cart_valid == "ok":
            self.init_chain(init_vad)

    def init_chain(self, init_vad):
        msg = self.controller.rec()
        if msg == "not_init":
            self.init_chain_page(init_vad)
        else:
            self.main_page(init_vad)

    def main_page(self, init_vad):
        self.clear_screen()
        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Contenuto principale
        self.grid_rowconfigure(2, weight=0)  # Testo in basso

        self.load_img()
        
        # header        
        header_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky='new', ipady=5, pady=0)

        header_frame.grid_columnconfigure(0, weight=1)

        bottom_border = ctk.CTkFrame(master=header_frame, height=2, fg_color="#000000")
        bottom_border.grid(row=0, column=0, sticky="sew", pady=0)
    
        header_label = ctk.CTkLabel(master=header_frame, text=f"codice: {self.operator_code}  carrello: {self.operator_cart}", font=("Inter", 48))
        header_label.grid(row=0, column=0, sticky="w", padx=40, pady=10)
        
        # Frame centrale per microfono (trasparente)
        mic_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        mic_frame.grid(row=1, column=0, sticky="nsew")
        mic_frame.grid_columnconfigure(0, weight=1)
        mic_frame.grid_rowconfigure(0, weight=1)

        # Img microfono
        image = ctk.CTkImage(self.img_chiusura, size=(375, 375))
        self.icon = ctk.CTkLabel(master=mic_frame, image=image, text="")
        self.icon.grid(row=0, column=0)

        self.string = tk.StringVar()
        self.string.set("avviamento...")
        label = ctk.CTkLabel(master=self, textvariable=self.string, font=("Inter", 64))
        label.grid(row=2, column=0, sticky="ew", pady=(0, 40))

        self.update_idletasks()  # Forza il rendering immediato
        
        if init_vad:
            self.init_vad()
        
        logout_img = ctk.CTkImage(light_image=Image.open("img/logout.png"), size=(48, 48))
        logout_button = ctk.CTkButton(master=header_frame, text="", image=logout_img, fg_color="transparent", hover=False, command=self.logout)
        logout_button.grid(row=0, column=0, sticky="e", pady=10)
        
        self.vad_thread = threading.Thread(target=self.vad.listen, daemon=True)
        self.vad_thread.start()


    def init_chain_page(self, init_vad):
        self.clear_screen()
        self.protocol("WM_DELETE_WINDOW", lambda: messagebox.showerror("Errore", "Configura la filiera"))

        self.brands = self.controller.rec_long_msg()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(master=self, text="Inizializza filiera", font=("Inter", 64))
        label.grid(row=0, column=0, pady=20)

        # Dizionario per salvare le selezioni di ogni bottone (1–24)
        self.selected = {i: [] for i in range(1, 25)}

        # Layout dei 24 bottoni in griglia
        frame_btns = ctk.CTkFrame(master=self, corner_radius=25)
        frame_btns.grid(row=1, column=0, pady=20)

        for i in range(1, 25):
            btn = ctk.CTkButton(
                master=frame_btns,
                text=str(i),
                width=80,
                text_color=self.colors.get("text_white"),
                font=("Inter", 32),
                fg_color=self.colors.get("button"),
                hover_color=self.colors.get("hover"),
                corner_radius=15,
                command=lambda idx=i: self.open_window(idx)
            )
            row, col = divmod(i - 1, 6)  # 6 colonne
            btn.grid(row=row, column=col, padx=15, pady=15)

        send_btn = ctk.CTkButton(
            master=self,
            text="Conferma",
            text_color=self.colors.get("text_white"),
            border_spacing=10,
            font=("Inter", 32),
            fg_color=self.colors.get("button"),
            hover_color=self.colors.get("hover"),
            corner_radius=15,
            command=lambda: self.send_bins(init_vad)
        )
        send_btn.grid(row=3, column=0, pady=20)

    def open_window(self, idx):
        window = ctk.CTkToplevel(self)
        window.title(f"Selezione per cassettone {idx}")
        window.geometry("400x600")
        window.minsize(400, 600)

        checkbox_vars = {}

        # Scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(master=window, width=380, height=500)
        scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # --- Aggancio del mousewheel per lo scroll con touchpad ---
        def _on_mousewheel(event):
            scrollable_frame._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # Windows e Mac (event.delta)
        scrollable_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux (event.num)
        scrollable_frame._parent_canvas.bind_all("<Button-4>", lambda e: scrollable_frame._parent_canvas.yview_scroll(-1, "units"))
        scrollable_frame._parent_canvas.bind_all("<Button-5>", lambda e: scrollable_frame._parent_canvas.yview_scroll(1, "units"))
        # ---------------------------------------------------------

        # Checkbox per ogni brand
        for brand in self.brands:
            var = ctk.BooleanVar(value=brand in self.selected[idx])
            checkbox = ctk.CTkCheckBox(master=scrollable_frame, text=brand, variable=var)
            checkbox.pack(anchor="w", padx=10, pady=4)
            checkbox_vars[brand] = var

        # Bottone di salvataggio
        save_button = ctk.CTkButton(
            master=window,
            text="Salva",
            text_color=self.colors.get("text_white"),
            border_spacing=10,
            font=("Inter", 32),
            fg_color=self.colors.get("button"),
            hover_color=self.colors.get("hover"),
            corner_radius=15,
            command=lambda: self.save_selection(idx, checkbox_vars, window))
        save_button.pack(pady=10)

    def save_selection(self, idx, checkbox_vars, window):
        self.selected[idx] = [brand for brand, var in checkbox_vars.items() if var.get()]
        window.destroy()

    def send_bins(self, init_vad):
        list = [self.selected[i] for i in range(1, 25)]
        print(list)
        if not any(list):  # tutte le sottoliste sono vuote
            messagebox.showerror("Errore", "Almeno un cassettone deve essere associato ad almeno un brand.")
        else:
            self.controller.send_long_msg(list)
            self.main_page(init_vad)


    def load_img(self):
        self.img_attivo = Image.open("img/attivo.png")
        self.img_elaborazione = Image.open("img/elaborazione.png")
        self.img_ascolto = Image.open("img/in ascolto.png")
        self.img_conf_chiedi = Image.open("img/conferma chiedi.png")
        self.img_conf_ascolta = Image.open("img/conferma ascolta.png")
        self.img_inviato = Image.open("img/inviato.png")
        self.img_chiusura = Image.open("img/chiusura.png")

    def init_vad(self):
        self.pavucontrol = subprocess.Popen(["pavucontrol"])   # Avvia il processo pavucontrol in background
        time.sleep(1)
        subprocess.run(["wmctrl", "-r", "PulseAudio Volume Control", "-b", "add,hidden"])  # Minimizza la finestra
 
        hotwords = self.controller.rec_long_msg()
        print("hw ricevute")

        self.vad = Vad(self, self.controller, hotwords)

    def on_waiting_keyword(self):
        """Per impostare la pagina di ascolto della keyword"""
        self.img_attivo.load()
        image = ctk.CTkImage(self.img_attivo, size=(375, 375))
        self.icon.configure(image=image)

        self.string.set('dire "ATTIVAZIONE" per iniziare')

        self.update_idletasks()  # Forza il rendering immediato

    def on_processing(self):
        """Per impostare la pagina di elaborazione"""
        image = ctk.CTkImage(self.img_elaborazione, size=(375, 375))
        self.icon.configure(image=image)

        self.string.set('sto elaborando...')

    def on_listening(self):
        """Per impostare la pagina di ascolto del brand"""
        image = ctk.CTkImage(self.img_ascolto, size=(375, 375))
        self.icon.configure(image=image)

        self.string.set('dire il brand o "STOP"')

    def on_asking_confirm(self):
        """Per impostare la pagina di richiesta conferma"""
        image = ctk.CTkImage(self.img_conf_chiedi, size=(375, 375))
        self.icon.configure(image=image)

        self.string.set('dire "CONFERMA" o "RIPROVA"')

    def on_listening_confirm(self):
        """Per impostare la pagina di ascolto conferma"""
        image = ctk.CTkImage(self.img_conf_ascolta, size=(375, 375))
        self.icon.configure(image=image)

    def on_sent(self, brand):
        """Per impostare la pagina conferma dell'invio del brand"""
        image = ctk.CTkImage(self.img_inviato, size=(375, 375))
        self.icon.configure(image=image)

        self.string.set(f"inviato: {brand}")

    def logout(self):
        self.controller.send("logout")
        if self.vad:
            # Termino listen senza chiudere lo stream
            self.vad.running = False
            self.vad.pause = True
        self.after(500, lambda: self.login_page(init_vad=False))

    def exit(self):
        if hasattr(self, "icon"):
            image = ctk.CTkImage(self.img_chiusura, size=(375, 375))
            self.icon.configure(image=image)
            self.update_idletasks()  # Forza il rendering immediato

        if hasattr(self, "string"):
            self.string.set('chiusura...')
            self.update_idletasks()  # Forza il rendering immediato

        if self.conn:
            self.controller.send("exit")

        if self.pavucontrol:
            self.pavucontrol.terminate()

        if self.vad:
            if self.vad.pause == True:
                self.vad.close()
            else:
                self.vad.running = False
            self.vad_thread.join()  # Aspetta la chiusura del thread

        self.destroy()
    
    def exit2(self):
        if self.conn:
            self.controller.send("exit")

        if self.pavucontrol:
            self.pavucontrol.terminate()

        if self.vad:
            self.vad.close()
            self.vad_thread.join()  # Aspetta la chiusura del thread

        self.destroy()

    def clear_screen(self):
        for widget in self.winfo_children()[:]:
            widget.destroy()


if __name__ == "__main__":
    app = OperatorApp()
    app.mainloop()