import psycopg2
import tkinter as tk
from tkinter import ttk
from utils import Utils

LARGE_FONT = ("Verdana", 12)

def query_db(query):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        cur =conn.cursor()
        cur.execute(query)
        try:
            result = cur.fetchall()
        except:
            result = 0
        conn.commit()
        cur.close()
        conn.close()
        return result

class PowerGenerationSummary(tk.Frame):
    def done_button_switch(self):
        public_utils = query_db(f"SELECT * FROM PublicUtilities where email='{Utils.user_email}';")
        power_gen = query_db(f"SELECT * FROM PowerGeneration where email='{Utils.user_email}';")
        if len(public_utils) == 0 and len(power_gen) == 0:
            self.fields['done_button']['state'] = "disabled"
        else:
            self.fields['done_button']['state'] = "active"

    def delete_row(self, row):
        entry_num = int(self.fields[f"entry_number{row}"].cget("text"))
        email = self.fields[f"email{row}"].cget("text")
        query_db(f"DELETE FROM PowerGeneration WHERE email='{email}' AND entry_order_number={entry_num};")
        self.fields[f"type{row}"].destroy()
        self.fields[f"storage{row}"].destroy()
        self.fields[f"monthly{row}"].destroy()
        self.fields[f"email{row}"].destroy()
        self.fields[f"entry_number{row}"].destroy()
        self.fields[f"delete_button{row}"].destroy()

        self.done_button_switch()
    
    def create_table(self):
        user_power_gen = query_db(f"SELECT * FROM PowerGeneration WHERE email='{Utils.user_email}' ORDER BY entry_order_number ASC;")

        r = 4
        for row in user_power_gen:
            self.fields[f"type{r}"] = tk.Label(self, text=row[0])
            self.fields[f"type{r}"].grid(row = r , column = 0, padx=0, sticky = tk.W)

            self.fields[f"storage{r}"] = tk.Label(self, text=row[1])
            self.fields[f"storage{r}"].grid(row = r , column = 1, padx=10, sticky = tk.W)

            self.fields[f"monthly{r}"] = tk.Label(self, text=row[2])
            self.fields[f"monthly{r}"].grid(row = r , column = 2, padx=10, sticky = tk.W)

            self.fields[f"email{r}"] = tk.Label(self, text=row[3])
            self.fields[f"email{r}"].grid(row = r , column = 3, padx=10, sticky = tk.W)

            self.fields[f"entry_number{r}"] = tk.Label(self, text=row[4])
            self.fields[f"entry_number{r}"].grid(row = r , column = 4, padx=10, sticky = tk.W)

            self.fields[f"delete_button{r}"] = ttk.Button(self, text="Delete",
                                                          command=lambda row = r: self.delete_row(row))
            self.fields[f"delete_button{r}"].grid(row = r, column = 5, padx=10, pady=5, sticky=tk.W)

            r += 1

            self.done_button_switch()
    
    def on_show_frame(self, event):
        self.delete_table()
        self.create_table()
    
    def delete_table(self):
        r = 0
        for child in self.winfo_children():
            if r >= 9:
                child.destroy()
            r += 1
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.fields = {}

        self.bind("<<ShowFrame>>", self.on_show_frame)

        title = tk.Label(self, text="Power Generation", font=LARGE_FONT)
        title.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)
        
        subtitle = tk.Label(self, text="You have added these to your household:")
        subtitle.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W)

        add_powerGen_button = ttk.Button(self, text="Add Another", command=lambda: self.controller.show_frame_2('AddPowerGeneration'))
        add_powerGen_button.grid(row = 2, column = 0, padx=5, pady=5, sticky=tk.W)

        self.fields['done_button'] = ttk.Button(self, text="Done", command=lambda: self.controller.show_frame_2('SubComp'))
        self.fields['done_button'].grid(row = 2, column = 1, padx=5, pady=5, sticky=tk.E)

        column_names = ['Type:', 'Storage Capacity:', 'Avg kWh Generated:', 'Email:', 'Entry Number:']
        col = 0
        for column in column_names:
            if column == "Type:":
                col_pad=0
            else:
                col_pad=10
            self.fields[column] = tk.Label(self, text=column, font=LARGE_FONT)
            self.fields[column].grid(row = 3, column = col, padx=col_pad, sticky=tk.W)
            col+=1
