import tkinter as tk
from tkinter import ttk, messagebox
from Forms.power_gen_listing import query_db
from utils import Utils

LARGE_FONT = ("Verdana", 12)

class AddPowerGeneration(tk.Frame):
    def add(self):
        storage = self.fields['storage_kWh'].get("1.0", "end-1c")
        monthly = self.fields['monthly_kWh'].get("1.0", "end-1c")
        power_type = self.option_var.get()
        if power_type == "SELECT":
            messagebox.showerror("INVALID VALUE", "REQUIRED: Must select a Power Type!")
        elif not monthly.isdigit():
            messagebox.showerror("INVALID VALUE", "REQUIRED: Monthly kWh should be a whole number!")
        elif storage != '' and not storage.isdigit():
            messagebox.showerror("INVALID VALUE", "OPTIONAL: If adding Storage kWh it should be a whole number.")
        else:
            if storage == '':
                storage = "NULL"
            else:
                storage = int(storage)
            monthly = int(monthly)

            all_power_gen = query_db(f"SELECT * FROM PermanentPowerGeneration WHERE email='{Utils.user_email}';")
            entry_order_number = len(all_power_gen) + 1
            query_db(f"INSERT INTO PermanentPowerGeneration (email, entry_order_number) \
                        VALUES ('{Utils.user_email}', {entry_order_number});")
            query_db(f"INSERT INTO PowerGeneration (power_generation_type, storage_capacity, avg_kwh_generated, email, entry_order_number) \
                        VALUES ('{power_type}', {storage}, {monthly}, '{Utils.user_email}', {entry_order_number});")

            self.controller.show_frame_2('PowerGenerationSummary')
            self.fields['storage_kWh'].delete("1.0", "end")
            self.fields['monthly_kWh'].delete("1.0", "end")
            self.option_var.set("SELECT")

    def on_show_frame(self, event):
        self.skip_button_switch()

    def skip_button_switch(self):
        public_utils = query_db(f"SELECT * FROM PublicUtilities where email='{Utils.user_email}';")
        power_gen = query_db(f"SELECT * FROM PowerGeneration where email='{Utils.user_email}';")
        if len(public_utils) == 0 and len(power_gen) == 0:
            self.fields['skip_button']['state'] = "disabled"
        else:
            self.fields['skip_button']['state'] = "active"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.fields = {}

        self.bind("<<ShowFrame>>", self.on_show_frame)

        frame_label = tk.Label(self, text='Add Power Generation', font=LARGE_FONT, justify=tk.LEFT)
        frame_label.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)

        frame_sublabel = tk.Label(self, text='Please provide power generation details.', justify=tk.LEFT)
        frame_sublabel.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W)

        OPTIONS = ["solar-electric","wind"]
        self.option_var = tk.StringVar()
        self.option_var.set("SELECT")
        self.fields['power_gen_type_label'] = tk.Label(self, text='Power Generation Type:', justify=tk.LEFT)
        self.fields['power_gen_type_label'].grid(row = 2, column = 0, padx=10, pady=5, sticky=tk.E)
        self.fields['power_gen_type'] = tk.OptionMenu(self, self.option_var, *OPTIONS)
        self.fields['power_gen_type'].grid(row = 2, column = 1, padx=10, pady=5, sticky=tk.W)
        
        self.fields['monthly_kWh_label'] = tk.Label(self, text='Average Monthly kWh:', justify=tk.LEFT)
        self.fields['monthly_kWh_label'].grid(row = 3, column = 0, padx=10, pady=5, sticky=tk.E)
        self.fields['monthly_kWh'] = tk.Text(self, height=1, width=16, wrap=None)
        self.fields['monthly_kWh'].grid(row = 3, column = 1, padx=10, pady=5, sticky=tk.W)
        
        self.fields['storage_kWh_label'] = tk.Label(self, text='Battery Storage kWh:', justify=tk.LEFT)
        self.fields['storage_kWh_label'].grid(row = 4, column = 0, padx=10, pady=5, sticky=tk.E)
        self.fields['storage_kWh'] = tk.Text(self, height=1, width=16, wrap=None)
        self.fields['storage_kWh'].grid(row = 4, column = 1, padx=10, pady=5, sticky=tk.W)
      
        self.fields['add_button'] = ttk.Button(self, text="ADD",
                                command=self.add)
        self.fields['add_button'].grid(row = 5, column = 1, padx=5, pady=5)

        self.fields['skip_button'] = ttk.Button(self, text="SKIP",
                                                state="disabled",
                                                command=lambda: self.controller.show_frame_2('PowerGenerationSummary'))
        self.fields['skip_button'].grid(row = 5, column = 0, padx=5, pady=5, sticky=tk.N)