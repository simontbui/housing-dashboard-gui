import tkinter as tk
import psycopg2
import pandas as pd
from Custom_Objects.customtable import CustomTable
from utils import Utils

LARGE_FONT = ("Verdana", 12)

class HeatCoolDetails(tk.Frame):

    def __init__(self, parent, controller):  
        #will have 4 subframes: header, AC, heaters, heatpump
        tk.Frame.__init__(self, parent)

        self.headerframe = tk.Frame(self)
        self.ACframe = tk.Frame(self)
        self.heaterframe = tk.Frame(self)
        self.heatpumpframe = tk.Frame(self)

        header = tk.Label(self.headerframe, text="Heating/Cooling Method Details", font=LARGE_FONT)
        header.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        self.headerframe.pack()

        self.display_AC()
        self.display_heater()
        self.display_heatpump()

        home_btn = tk.Button(self, text="Return To Reports Menu", command=lambda: controller.show_frame("ViewReports"))
        home_btn.pack(side="bottom", pady=50)

    def fetch_AC(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = """
                SELECT household_type, COUNT(*) AS NumACs, ROUND(AVG(btu_rating))::INTEGER AS
                AvgBTU, ROUND(CAST(AVG(eer) AS numeric),1)::DECIMAL(20,1) AS AvgEER
                FROM airconditioner AS ac
                JOIN airhandler AS ah
                ON ac.email = ah.email AND ac.entry_order_number = ah.entry_order_number
                JOIN household hh
                ON ac.email = hh.email
                GROUP BY household_type;
            """
        self.ACDF = pd.read_sql(sql, conn, coerce_float=False)
        conn.close()

    def fetch_heater(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = """
                SELECT household_type, COUNT(*) AS NumHeaters, ROUND(AVG(btu_rating))::INTEGER AS
                AvgBTU, MODE() WITHIN GROUP (ORDER BY energy_source) AS
                mostfrequentenergysource
                FROM heater AS h
                JOIN airhandler AS ah
                ON h.email = ah.email AND h.entry_order_number = ah.entry_order_number
                JOIN household hh
                ON h.email = hh.email
                GROUP BY household_type;
            """
        self.heaterDF = pd.read_sql(sql, conn)
        conn.close()

    def fetch_heatpump(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = """
                SELECT household_type, COUNT(*) AS numHP, ROUND(AVG(btu_rating))::INTEGER
                AS avgbtu,
                ROUND(CAST(AVG(seer) AS numeric),1)::DECIMAL(20,1) AS AvgSEER,
                ROUND(CAST(AVG(hspf) AS numeric),1)::DECIMAL(20,1) AS AvgHSPF
                FROM heatpump AS hp
                JOIN airhandler AS ah
                ON hp.email = ah.email AND hp.entry_order_number = ah.entry_order_number
                JOIN household hh
                ON hp.email = hh.email
                GROUP BY household_type;
            """
        self.heatpumpDF = pd.read_sql(sql, conn, coerce_float=False)
        conn.close()

    def display_AC(self):
        self.fetch_AC()
        
        ACTitleFrame = tk.Frame(self)
        ACtitle = tk.Label(ACTitleFrame, text="Air Conditioner Statistics", font=("Verdana", 10))
        ACtitle.grid()
        ACTitleFrame.pack(pady=(50,5))

        table = CustomTable(self.ACframe, dataframe=self.ACDF, height=50)
        table.show()
        self.ACframe.pack()

    def display_heater(self):
        self.fetch_heater()

        heaterTitleFrame = tk.Frame(self)
        heaterTitle = tk.Label(heaterTitleFrame, text="Heater Statistics", font=("Verdana", 10))
        heaterTitle.grid()
        heaterTitleFrame.pack(pady=(50,5))

        table = CustomTable(self.heaterframe, dataframe=self.heaterDF, height=50)
        table.show()
        self.heaterframe.pack()

    def display_heatpump(self):
        self.fetch_heatpump()

        HPTitleFrame = tk.Frame(self)
        HPTitle = tk.Label(HPTitleFrame, text="Heat Pump (HP) Statistics", font=("Verdana", 10))
        HPTitle.grid()
        HPTitleFrame.pack(pady=(50,5))

        table = CustomTable(self.heatpumpframe, dataframe=self.heatpumpDF, height=50)
        table.show()
        self.heatpumpframe.pack()