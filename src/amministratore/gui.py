import tkinter as tk
import customtkinter as ctk      # type: ignore
from tkcalendar import DateEntry # type: ignore
from tkinter import ttk, messagebox
from PIL import Image
import re
from controller import Controller

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()  # Inizializza ctk.CTk

        self.title("Amministratore")
        self.geometry("1920x1080")
        self.minsize(1067, 600)
        ctk.set_appearance_mode("light")

        self.colors = {
            "background": "#EDF6F9",    # sfondo
            "text_white": "#FFFFFF",    # bianco
            "button": "#006D77",        # blu
            "hover": "#01555D",         # blu scuro
            "primary": "#83C5BE",       # blu chiaro
            "error": "#C00000"          # rosso
        }

        self.configure(fg_color=self.colors.get("background"))
        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.admin_code = None
        self.controller = None
        self.conn = None

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
                self.error_page(string_var, "Impossibile connettersi:\nil server è in chiusura", frame_img, "img/server_off.png")
            elif msg == "ACCEPTED":
                self.controller.send("admin")
                if self.controller._rec_msg():
                    self.login_page()
                else:
                    self.error_page(string_var, "Impossibile connettersi:\nc'è un amministratore\ngià connesso", frame_img, "img/admin_error.png")
        else:
            self.error_page(string_var, "Impossibile connettersi:\nil server è spento", frame_img, "img/server_off.png")

    def error_page(self, string_var, error_msg, frame_img, image_path):
        string_var.set(error_msg)
        
        image_pil = Image.open(image_path)
        if image_path == "img/server_off.png":
            image = ctk.CTkImage(image_pil, size=(347, 321))
        else:
            image = ctk.CTkImage(image_pil, size=(347, 247))

        frame_img.grid_rowconfigure(0, weight=1)
        frame_img.grid_columnconfigure(0, weight=1)

        image_label = ctk.CTkLabel(master=frame_img, image=image, text="")
        image_label.grid(row=0, column=0, sticky='nse')

    def login_page(self):
        self.clear_screen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        label = ctk.CTkLabel(master=self, text="Effettua l'accesso\ncome amministratore", font=("Inter", 64))
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
        code_error_label.grid(row=2, column=0, pady=(0, 30))

        submit_button = ctk.CTkButton(master=self.login_frame, text="  Accedi  ", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=self.login)
        submit_button.grid(row=6, column=0, pady=(0, 25))

    def login(self):
        self.admin_code = self.code_entry.get()

        self.code_entry.configure(border_color=ctk.ThemeManager.theme["CTkEntry"]["border_color"])
        self.code_error_str.set("")

        if self.admin_code:
            if self.controller.check_code(self.admin_code): 
                self.home_page()
            else:
                self.code_entry.configure(border_color="red")
                self.code_error_str.set("Codice non esistente")
        else:
            self.code_entry.configure(border_color="red")
            self.code_error_str.set("Inserire codice")
   
    def home_page(self):
        self.clear_screen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # header
        self.header_frame = ctk.CTkFrame(master=self, fg_color=self.colors.get("primary"))
        self.header_frame.grid(row=0, column=0, sticky='new', pady=0, ipady=5)

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_rowconfigure(0, weight=1)

        header_label = ctk.CTkLabel(master=self.header_frame, text=f"codice: {self.admin_code}", font=("Inter", 48))
        header_label.grid(row=0, column=0, pady=15)

        logout_img = ctk.CTkImage(light_image=Image.open("img/logout.png"), size=(48, 48))
        logout_button = ctk.CTkButton(master=self.header_frame, text="", image=logout_img, fg_color="transparent", hover=False, command=self.logout)
        logout_button.grid(row=0, column=0, sticky="e", pady=15)

        # bottoni
        self.page_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.page_frame.grid(row=1, column=0, sticky="news", pady=0)

        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure(0, weight=1)

        button_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        button_frame.grid(row=0, column=0)
        button_frame.grid_columnconfigure(0, weight=1)

        button_width = 400

        admin_button = ctk.CTkButton(master=button_frame, width=button_width, text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, text="Gestione Amministratori", command=lambda: self.handle_user_page("admin"))
        admin_button.grid(row=0, pady=15)

        operator_button = ctk.CTkButton(master=button_frame, width=button_width, text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, text="Gestione Operatori", command=lambda: self.handle_user_page("operator"))
        operator_button.grid(row=1, pady=15)

        brand_button = ctk.CTkButton(master=button_frame, width=button_width, text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, text="Gestione Brand", command=self.handle_brand_page)
        brand_button.grid(row=2, pady=15)

        log_button = ctk.CTkButton(master=button_frame, width=button_width, text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, text="Visualizza Log", command=self.handle_log_page)
        log_button.grid(row=3, pady=15)

        cart_button = ctk.CTkButton(master=button_frame, width=button_width, text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, text="Cambia numero carrelli", command=self.change_cart_page)
        cart_button.grid(row=4, pady=15)

    # Operatore e admin
    def handle_user_page(self, type):
        self.clear_page_frame()

        back_img = ctk.CTkImage(light_image=Image.open("img/back.png"), size=(48, 48))
        back_button = ctk.CTkButton(master=self.header_frame, text="", image=back_img, fg_color="transparent", hover=False, command=self.home_page)
        back_button.grid(row=0, column=0, sticky="w")

        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure((0,1), weight=1)
        
        # Tabella
        table_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Scrollbar verticale
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.grid(row=0, column=1, sticky='ns')

        # Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", font=("Inter", 14, "bold"), background=self.colors.get("hover"), foreground="white")
        style.configure("Custom.Treeview", font=("Inter", 12), rowheight=30, fieldbackground="#f0f0f0")
        style.map("Custom.Treeview", background=[("selected", self.colors.get("button"))], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            master=table_frame,
            columns=("Codice", "Nome", "Cognome"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Custom.Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.config(command=self.tree.yview)

        # Colonne
        self.tree.heading("Codice", text="Codice")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Cognome", text="Cognome")

        self.tree.column("Codice", anchor="center", width=100)
        self.tree.column("Nome", anchor="center", width=150)
        self.tree.column("Cognome", anchor="center", width=150)

        # Bottoni
        button_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0)

        button_width = 300

        add_button = ctk.CTkButton(master=button_frame, width=button_width, text="Aggiungi", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=lambda: self.add_user(type))
        add_button.grid(row=0, column=0, padx=10)

        edit_button = ctk.CTkButton(master=button_frame, width=button_width, text="Modifica", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=lambda: self.edit_user(type))
        edit_button.grid(row=0, column=1, padx=10)

        delete_button = ctk.CTkButton(master=button_frame, width=button_width, text="Elimina", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=lambda: self.delete_user(type))
        delete_button.grid(row=0, column=2, padx=10)

        # Caricare gli operatori o gli admin dal server
        self.load_users(type)

    def load_users(self, type):
        data = self.controller.get_users(type)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for elem in data:
            self.tree.insert("", "end", values=(elem["code"], elem["first_name"], elem["last_name"]))

    def add_user(self, type):
        """Apre una finestra per aggiungere un operatore o un admin."""
        if type == "operator":
            self.user_form("Aggiungi Operatore", type)
        else:
            self.user_form("Aggiungi Amministratore", type)

    def edit_user(self, type):
        """Apre una finestra per modificare l'operatore o l'admin selezionato."""
        selected_item = self.tree.selection()
        if not selected_item:
            if type == "operator":
                messagebox.showerror("Errore", "Seleziona un operatore da modificare.")
            else:
                messagebox.showerror("Errore", "Seleziona un amministratore da modificare.")
            return

        values = self.tree.item(selected_item, "values")
        if type == "operator":
                self.user_form("Modifica Operatore", type, values)
        else:
            self.user_form("Modifica Amministratore", type, values)

    def delete_user(self, type):
        """Elimina l'operatore selezionato."""
        selected_item = self.tree.selection()
        if not selected_item:
            if type == "operator":
                messagebox.showerror("Errore", "Seleziona un operatore da eliminare.")
            else:
                messagebox.showerror("Errore", "Seleziona un amministratore da eliminare.")
            return

        values = self.tree.item(selected_item, "values")
        code = values[0]

        confirm = messagebox.askyesno("Conferma", f"Vuoi eliminare {values[1]} {values[2]}?")
        if confirm:
            if self.controller.delete_user(type, code):
                self.load_users(type)
            else:
                messagebox.showerror("Errore", "Impossibile completare l'operazione.")

    def user_form(self, title, type, user_data=None):
        """Apre una finestra per aggiungere o modificare un operatore o un admin."""
        form = ctk.CTkToplevel(self)
        form.title(title)
        form.geometry("550x470")
        form.resizable(False, False)
        form.configure(fg_color=self.colors.get("background"))

        code_label = ctk.CTkLabel(master=form, text="codice:", font=("Inter Display Thin", 32))
        code_label.grid(row=0, column=0, pady=(25, 0), padx=40, sticky='w')

        code_entry = ctk.CTkEntry(master=form, font=("Inter", 20), width=500, height=52, corner_radius=15, placeholder_text="codice")
        code_entry.grid(row=1, column=0, padx=25)

        name_label = ctk.CTkLabel(master=form, text="nome:", font=("Inter Display Thin", 32))
        name_label.grid(row=2, column=0, pady=(25, 0), padx=40, sticky='w')

        first_name_entry = ctk.CTkEntry(master=form, font=("Inter", 20), width=500, height=52,corner_radius=15, placeholder_text="nome")
        first_name_entry.grid(row=3, column=0, padx=25)

        last_name_label = ctk.CTkLabel(master=form, text="cognome:", font=("Inter Display Thin", 32))
        last_name_label.grid(row=4, column=0, pady=(25, 0), padx=40, sticky='w')

        last_name_entry = ctk.CTkEntry(master=form, font=("Inter", 20), width=500, height=52,corner_radius=15, placeholder_text="cognome")
        last_name_entry.grid(row=5, column=0, padx=25, pady=(0, 25))

        if user_data:
            code_entry.insert(0, user_data[0])
            first_name_entry.insert(0, user_data[1])
            last_name_entry.insert(0, user_data[2])
            code_entry.configure(state="disabled", fg_color="#A3A3A3")  # Il codice non si può modificare

        def submit_user():
            code = code_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()

            if not code or not first_name or not last_name:
                messagebox.showerror("Errore", "Tutti i campi sono obbligatori.")
                return

            action = "update" if user_data else "create"
            if self.controller.update_or_create_user(action, type, code, first_name, last_name):
                self.load_users(type)
                form.destroy()
            else:
                messagebox.showerror("Errore", "Operazione fallita.")

        submit_button = ctk.CTkButton(master=form, text="Salva", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=submit_user)
        submit_button.grid(row=6, column=0)

    # Brand
    def handle_brand_page(self):
        self.clear_page_frame()

        back_img = ctk.CTkImage(light_image=Image.open("img/back.png"), size=(48, 48))
        back_button = ctk.CTkButton(master=self.header_frame, text="", image=back_img, fg_color="transparent", hover=False, command=self.home_page)
        back_button.grid(row=0, column=0, sticky="w")

        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure((0,1), weight=1)
        self.page_frame.grid_rowconfigure(2, weight=1)
      
        # Tabella
        table_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Scrollbar verticale
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.grid(row=0, column=1, sticky='ns')

        # Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", font=("Inter", 14, "bold"), background=self.colors.get("hover"), foreground="white")
        style.configure("Custom.Treeview", font=("Inter", 12), rowheight=30, fieldbackground="#f0f0f0")
        style.map("Custom.Treeview", background=[("selected", self.colors.get("button"))], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            master=table_frame,
            columns=("Nome", "Nome normalizzato", "Lingua"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Custom.Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.config(command=self.tree.yview)

        # Colonne
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Nome normalizzato", text="Nome normalizzato")
        self.tree.heading("Lingua", text="Lingua")

        self.tree.column("Nome", width=150)
        self.tree.column("Nome normalizzato", width=150)
        self.tree.column("Lingua", width=150)

        # Bottoni
        button_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0)

        button_width = 300

        add_button = ctk.CTkButton(master=button_frame, width=button_width, text="Aggiungi", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=self.add_brand)
        add_button.grid(row=0, column=0, padx=10)

        edit_button = ctk.CTkButton(master=button_frame, width=button_width, text="Modifica", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=self.edit_brand)
        edit_button.grid(row=0, column=1, padx=10)

        delete_button = ctk.CTkButton(master=button_frame, width=button_width, text="Elimina", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=self.delete_brand)
        delete_button.grid(row=0, column=2, padx=10)

        # Label
        label = ctk.CTkLabel(self.page_frame, text="Aggiungi il nome normalizzato quando il brand presenta sigle o punteggiatura. Ad esempio Dr. Martens = dottor martens\n\nAl riavvio dei client le eventuali modifche effettuate saranno effettive", font=("Arial", 16, "italic"))
        label.grid(row=2, column=0)

        # Caricare i dati dal server
        self.load_brand()

    def load_brand(self):
        data = self.controller.get_brands()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for brand in data:
            self.tree.insert("", "end", values=(brand["name"], brand["normalized_name"], brand["language"]))

    def add_brand(self):
        """Apre una finestra per aggiungere un brand"""
        self.brand_form("Aggiungi Brand")

    def edit_brand(self):
        """Apre una finestra per modificare il brand selezionato."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un brand da modificare.")
            return

        values = self.tree.item(selected_item, "values")
        self.brand_form("Modifica Brand", values)

    def delete_brand(self):
        """Elimina il brand selezionato."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un brand da eliminare.")
            return

        values = self.tree.item(selected_item, "values")
        name = values[0]

        confirm = messagebox.askyesno("Conferma", f"Vuoi eliminare {values[1]}?")
        if confirm:
            if self.controller.delete_brand(name):
                self.load_brand()
            else:
                messagebox.showerror("Errore", "Impossibile completare l'operazione.")

    def brand_form(self, title, brand_data=None):
        """Apre una finestra per aggiungere o modificare un brand"""
        form = ctk.CTkToplevel(self)
        form.title(title)
        form.geometry("550x470")
        form.resizable(False, False)
        form.configure(fg_color=self.colors.get("background"))

        name_label = ctk.CTkLabel(master=form, text="nome:", font=("Inter Display Thin", 32))
        name_label.grid(row=0, column=0, pady=(25, 0), padx=40, sticky='w')

        name_entry = ctk.CTkEntry(master=form, font=("Inter", 20), width=500, height=52,corner_radius=15, placeholder_text="nome")
        name_entry.grid(row=1, column=0, padx=25)

        normalized_name_label = ctk.CTkLabel(master=form, text="nome normalizzato:", font=("Inter Display Thin", 32))
        normalized_name_label.grid(row=2, column=0, pady=(25, 0), padx=40, sticky='w')

        normalized_name_entry = ctk.CTkEntry(master=form, font=("Inter", 20), width=500, height=52,corner_radius=15, placeholder_text="nome normalizzato")
        normalized_name_entry.grid(row=3, column=0, padx=25)

        lang_label = ctk.CTkLabel(master=form, text="lingua:", font=("Inter Display Thin", 32))
        lang_label.grid(row=4, column=0, pady=(25, 0), padx=40, sticky='w')

        lang_list = ["italiano", "inglese", "francese", "spagnolo", "tedesco"]
        lang_entry = ctk.CTkComboBox(master=form, font=("Inter", 20), width=500, height=52, corner_radius=15, values=lang_list, dropdown_font=("Inter", 20))
        lang_entry.grid(row=5, column=0, padx=25, pady=(0, 25))

        if brand_data:
            name_entry.insert(0, brand_data[0])
            normalized_name_entry.insert(0, brand_data[1])
            lang_entry.set(brand_data[2])
            name_entry.configure(state="disabled", fg_color="#A3A3A3")  # Il nome non si può modificare

        def submit_brand():
            name = name_entry.get()
            normalized_name = normalized_name_entry.get()
            language = lang_entry.get()

            if not name:
                messagebox.showerror("Errore", "Nome obbligatorio.")
                return
            
            if language not in ["italiano", "inglese", "francese", "spagnolo", "tedesco"]:
                messagebox.showerror("Errore", "Lingua non valida.")
                return

            action = "update" if brand_data else "create"
            if self.controller.update_or_create_brand(action, name, normalized_name, language):
                self.load_brand()
                form.destroy()
            else:
                messagebox.showerror("Errore", "Operazione fallita.")

        submit_button = ctk.CTkButton(master=form, text="Salva", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=submit_brand)
        submit_button.grid(row=6, column=0)

    # Log
    def handle_log_page(self):
        self.clear_page_frame()

        back_img = ctk.CTkImage(light_image=Image.open("img/back.png"), size=(48, 48))
        back_button = ctk.CTkButton(master=self.header_frame, text="", image=back_img, fg_color="transparent", hover=False, command=self.home_page)
        back_button.grid(row=0, column=0, sticky="w")

        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure((0,1), weight=1)
        
        # Filtri
        filter_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0)

        ctk.CTkLabel(filter_frame, text="Codice Operatore:", font=("Inter", 24)).grid(row=0, column=0, padx=(0,5))
        self.operator_code_entry = ctk.CTkEntry(filter_frame, font=("Inter", 24), placeholder_text="codice")
        self.operator_code_entry.grid(row=0, column=1, padx=(0,30))

        ctk.CTkLabel(filter_frame, text="Data:", font=("Inter", 24)).grid(row=0, column=2, padx=(0,5))
        self.date_entry = DateEntry(filter_frame, date_pattern="yyyy-mm-dd", font=("Inter Display Thin", 18))
        self.date_entry.grid(row=0, column=3, padx=(0, 30))
        self.date_entry.delete(0, tk.END)

        self.filter_button = ctk.CTkButton(filter_frame, text="Filtra", text_color=self.colors.get("text_white"), font=("Inter", 24), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=self.apply_log_filters)
        self.filter_button.grid(row=0, column=4)

        # Tabella
        table_frame = ctk.CTkFrame(master=self.page_frame, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Scrollbar verticale
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.grid(row=0, column=1, sticky='ns')

        # Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", font=("Inter", 14, "bold"), background=self.colors.get("hover"), foreground="white")
        style.configure("Custom.Treeview", font=("Inter", 12), rowheight=30, fieldbackground="#f0f0f0")
        style.map("Custom.Treeview", background=[("selected", self.colors.get("button"))], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            master=table_frame,
            columns=("Id", "Operatore", "Brand", "Carrello", "Data"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Custom.Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.config(command=self.tree.yview)

        self.tree.heading("Id", text="Id")
        self.tree.heading("Operatore", text="Operatore")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Carrello", text="Carrello")
        self.tree.heading("Data", text="Data")

        # Caricare i dati dal server
        self.load_logs(code="", day="")

    def apply_log_filters(self):
        operator_code = self.operator_code_entry.get().strip()
        date = self.date_entry.get().strip()

        # Controllo se la data è nel formato corretto
        if date and not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            messagebox.showerror("Errore", "Formato data non valido! Usa YYYY-MM-DD.")
            return  # Blocca il filtraggio se la data non è valida
        
        self.load_logs(operator_code, date)

    def load_logs(self, code, day):
        data = self.controller.get_logs(code=code, day=day)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for log in data:
            self.tree.insert("", "end", values=(log["id"], log["operator_code"], log["brand_name"], log["cart"], log["timestamp"]))

    # Carrelli
    def change_cart_page(self):
        self.clear_page_frame()

        back_img = ctk.CTkImage(light_image=Image.open("img/back.png"), size=(48, 48))
        back_button = ctk.CTkButton(master=self.header_frame, text="", image=back_img, fg_color="transparent", hover=False, command=self.home_page)
        back_button.grid(row=0, column=0, sticky="w")

        self.page_frame.grid_columnconfigure(0, weight=1)
        self.page_frame.grid_rowconfigure((0,1), weight=1)

        num_cart = self.controller.get_num_carts()
        self.cart_str = tk.StringVar()
        self.cart_str.set(f"Numero di carrelli: {num_cart}")

        cart_label = ctk.CTkLabel(master=self.page_frame, textvariable=self.cart_str, font=("Inter", 64))
        cart_label.grid(row=0, column=0)

        frame = ctk.CTkFrame(master=self.page_frame, fg_color=self.colors.get("primary"), corner_radius=25)
        frame.grid(row=1, column=0)
        
        label = ctk.CTkLabel(master=frame, text="inserisci nuovo numero di carrelli:", font=("Inter Display Thin", 32))
        label.grid(row=0, column=0, pady=(25, 0), padx=25, sticky='w')

        self.cart_entry = ctk.CTkEntry(master=frame, font=("Inter", 20), width=500, height=52,corner_radius=15, placeholder_text="carrelli")
        self.cart_entry.grid(row=1, column=0, padx=25)

        self.error_str = tk.StringVar()
        self.error_str.set("")
        error_label = ctk.CTkLabel(master=frame, textvariable=self.error_str, font=("Display", 14), text_color=self.colors.get("error"))
        error_label.grid(row=2, column=0, pady=(0, 30))

        submit_button = ctk.CTkButton(master=frame, text="  Cambia  ", text_color=self.colors.get("text_white"), border_spacing=10, font=("Inter", 32), fg_color=self.colors.get("button"), hover_color=self.colors.get("hover"), corner_radius=15, command=self.change_page)
        submit_button.grid(row=6, column=0, pady=(0, 25))

    def change_page(self):
        input = self.cart_entry.get()

        self.cart_entry.configure(border_color=ctk.ThemeManager.theme["CTkEntry"]["border_color"])
        self.error_str.set("")

        if input:
            try:
                number = int(input)
            except Exception:
                self.cart_entry.configure(border_color="red")
                self.error_str.set("Numero di carrelli non valido, riprovare")
                return
            if number > 0:
                res = self.controller.set_num_carts(number)
                if res == "SUCCESS":
                    self.cart_str.set(f"Numero di carrelli: {number}")
                    self.cart_entry.delete(0, "end")
                elif res == "ERROR":
                    self.cart_entry.configure(border_color="red")
                    self.error_str.set("Errore server")
                elif res == "OP CONN":
                    self.cart_entry.configure(border_color="red")
                    self.error_str.set("Non è possibile cambiare il numeor di carrelli finchè ci sono degli operatori connessi")
            else:
                self.cart_entry.configure(border_color="red")
                self.error_str.set("Numero di carrelli non valido, riprovare")
        else:
            self.cart_entry.configure(border_color="red")
            self.error_str.set("Inserire numero carrelli")


    def logout(self):
        self.controller.send_msg("logout")
        self.login_page()

    def exit(self):
        if self.conn:
            self.controller.send_msg("exit")
        self.destroy()


    def clear_screen(self):
        for widget in self.winfo_children()[:]:
            widget.destroy()

    def clear_page_frame(self):
        for widget in self.page_frame.winfo_children():
            widget.destroy()



if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()