import tkinter as tk
import psycopg2
import pandas as pd
from utils import Utils
from Custom_Objects.customtable import CustomTable

LARGE_FONT = ("Verdana", 12)

class MfgSearch(tk.Frame):
    #frame will consist of 2 subframes: topframe & bottomframe
    #topframe consists of the header, search box, search button, and label
    #bottomframe will display the data table upon clicking search

    def __init__(self, parent, controller):     
        tk.Frame.__init__(self, parent)

        topframe = tk.Frame(self)
        self.bottomframe = tk.Frame(self)

        header = tk.Label(topframe, text="Manufacturer/Model Search", font=LARGE_FONT)
        header.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        #-------------Search Form START----------------
        search_label= tk.Label(topframe, text="Enter Manufacturer/Model Name:", justify=tk.RIGHT)
        search_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

        self.search_string = tk.StringVar()
        search_entry = tk.Entry(topframe, textvariable=self.search_string, width=50)
        search_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        search_entry.focus()

        search_button = tk.Button(topframe, text="Search", command=lambda: self.display())
        search_button.grid(row=1, column=2, padx=10, pady=5)
        #-------------Search Form END----------------

        topframe.pack()

        home_btn = tk.Button(self, text="Return To Reports Menu", command=lambda: controller.show_frame("ViewReports"))
        home_btn.pack(side="bottom", pady=50)

    def fetch(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = f"""
                select distinct manufacturer, model_name from
                (
                    select manufacturer, model_name from airhandler
                    union 
                    select manufacturer, model_name from waterheater
                ) unioned
                where (lower(manufacturer) like '%{self.search_string.get().lower().strip()}%' or lower(model_name) like '%{self.search_string.get().lower().strip()}%')
                order by manufacturer, model_name
             """
        
        self.df = pd.read_sql(sql, conn)
        conn.close()

    def display(self):
        self.fetch()
            
        #deletes any existing displayed table 
        self.bottomframe.destroy()
        self.bottomframe = tk.Frame(self)

        table = CustomTable(self.bottomframe, dataframe=self.df, editable=False, width=500)

        mfg_mask = table.model.df["manufacturer"].astype(str).str.lower().str.contains(f"{self.search_string.get().lower().strip()}")

        model_mask = table.model.df["model_name"].astype(str).str.lower().str.contains(f"{self.search_string.get().lower().strip()}")

        table.setColorByMask("manufacturer", mfg_mask, "#90ee90")
        table.setColorByMask("model_name", model_mask, "#90ee90")
    
        table.show()
        self.bottomframe.pack()
