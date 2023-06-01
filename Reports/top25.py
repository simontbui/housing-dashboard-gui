import tkinter as tk
import psycopg2
import pandas as pd
from Custom_Objects.customtable import CustomTable
from utils import Utils

LARGE_FONT = ("Verdana", 12)

class Top25(tk.Frame):

    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)       
        #frame will consist of 3 subframes
            #headerframe
            #top25frame 
            #drilldownframe (generates after user selects a row in top25frame)

        self.headerframe = tk.Frame(self)
        self.top25frame = tk.Frame(self)
        self.drilldownframe = tk.Frame(self)
        self.drilldownTitleFrame = tk.Frame(self)

        header = tk.Label(self.headerframe, text="Top 25 Popular Manufacturers", font=LARGE_FONT)
        header.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        self.headerframe.pack()

        self.display_top25()

        home_btn = tk.Button(self, text="Return To Reports Menu", command=lambda: controller.show_frame("ViewReports"))
        home_btn.pack(side="bottom", pady=50)

    def fetch(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = """SELECT manufacturer, SUM(COUNT)::INTEGER AS count FROM
                (
                SELECT manufacturer, COUNT(*) FROM airhandler GROUP BY manufacturer
                UNION ALL
                SELECT manufacturer, COUNT(*) FROM waterheater GROUP BY manufacturer
                ) AS unioned
                GROUP BY manufacturer
                ORDER BY count DESC
                LIMIT 25"""
        
        self.top25df = pd.read_sql(sql, conn)
        conn.close()

    def display_top25(self):
        self.fetch()
        self.mainTable = CustomTable(self.top25frame, dataframe=self.top25df, 
                                     height=180, width=360, pady=25,
                                     handle_left_click=self.handle_left_click)
        self.mainTable.show()
        self.top25frame.pack()

    def fetch_drilldown(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = f"""
                SELECT 'WaterHeater' AS ApplianceType, SUM(CASE WHEN manufacturer = '{self.drilldown_mfg}' THEN 1 ELSE 0 END) AS count FROM waterheater 
                UNION
                SELECT 'AirHandler' AS ApplianceType, SUM(CASE WHEN manufacturer = '{self.drilldown_mfg}' THEN 1 ELSE 0 END) AS count FROM airhandler 
                UNION
                SELECT 'AirConditioner' AS ApplianceType, SUM(CASE WHEN manufacturer = '{self.drilldown_mfg}' THEN 1 ELSE 0 END) AS count FROM airconditioner ac, airhandler ah WHERE ac.email = ah.email AND ac.entry_order_number = ah.entry_order_number 
                UNION
                SELECT 'HeatPump' AS ApplianceType, SUM(CASE WHEN manufacturer = '{self.drilldown_mfg}' THEN 1 ELSE 0 END) AS count FROM heatpump hp, airhandler ah WHERE hp.email = ah.email AND hp.entry_order_number = ah.entry_order_number
                UNION
                SELECT 'Heater' AS ApplianceType, SUM(CASE WHEN manufacturer = '{self.drilldown_mfg}' THEN 1 ELSE 0 END) AS count FROM heater h, airhandler ah WHERE h.email = ah.email AND h.entry_order_number = ah.entry_order_number
                ORDER BY ApplianceType
            """
        
        self.drilldowndf = pd.read_sql(sql, conn)
        conn.close()

    def display_drilldown(self, row):
        self.drilldown_mfg = self.top25df.iloc[row]["manufacturer"]
        self.fetch_drilldown()

        self.drilldownTitleFrame.destroy()
        self.drilldownTitleFrame = tk.Frame(self)
        drilldownTitle = tk.Label(self.drilldownTitleFrame, text=f"Appliance Breakdown for {self.drilldown_mfg}",
                                  font=LARGE_FONT)
        drilldownTitle.grid(row=0, column=0)
        self.drilldownTitleFrame.pack(pady=(50, 5))

        self.drilldownframe.destroy()
        self.drilldownframe = tk.Frame(self)
        drilldownTable = CustomTable(self.drilldownframe, dataframe=self.drilldowndf, height=140, width=230)
        drilldownTable.show()
        self.drilldownframe.pack()

    def handle_left_click(self, event):
        self.mainTable.clearSelected()
        self.mainTable.allrows = False
        rowclicked = self.mainTable.get_row_clicked(event)
        self.display_drilldown(rowclicked)

