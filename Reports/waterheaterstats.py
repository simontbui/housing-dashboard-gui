import tkinter as tk
import psycopg2
import pandas as pd
from utils import Utils
from pandastable import Table
from Custom_Objects.customtable import CustomTable

LARGE_FONT = ("Verdana", 12)

class WaterHeaterStats(tk.Frame):
    def __init__(self, parent, controller):    
        tk.Frame.__init__(self, parent)  

        self.headerframe = tk.Frame(self)
        self.waterstatsframe = tk.Frame(self)
        self.drilldownframe = tk.Frame(self)
        self.drilldownTitleFrame = tk.Frame(self)
        
        header = tk.Label(self.headerframe, text="Water Heater Statistics by State", font=LARGE_FONT)
        header.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        self.headerframe.pack()

        self.display_WH_stats()

        home_btn = tk.Button(self, text="Return To Reports Menu", command=lambda: controller.show_frame("ViewReports"))
        home_btn.pack(side="bottom", pady=(1,50))
        
    def fetch_WH_stats(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = """
                SELECT tm.state AS state,
                (CASE WHEN AVG(capacity) IS NOT null THEN ROUND(AVG(capacity)) ELSE 0 END) AS
                AvgCapacity,
                (CASE WHEN AVG(btu_rating) IS NOT null THEN ROUND(AVG(btu_rating)) ELSE 0 END)
                AS AvgBTURating,
                (CASE WHEN AVG(temperature_setting) IS NOT null THEN
                round(AVG(temperature_setting), 1) ELSE 0 END) AS AvgTemp,
                SUM(CASE WHEN temperature_setting IS NOT null THEN 1 ELSE 0 end) AS
                numWHwithtemp,
                SUM(CASE WHEN temperature_setting IS null AND primaryemail IS NOT null THEN 1 ELSE 0 END) AS
                numWHwithouttemp
                FROM
                (
                (SELECT DISTINCT state FROM postalcode) AS tm
                LEFT JOIN
                (SELECT hh.email AS primaryemail, * FROM waterheater AS wh, household AS hh, postalcode AS pc WHERE
                wh.email = hh.email AND hh.code = pc.code) tk
                ON tm.state = tk.state
                )
                GROUP BY tm.state
                ORDER BY tm.state;
            """
        self.statsDF = pd.read_sql(sql, conn, coerce_float=False)
        conn.close()

    def fetch_drilldown(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        sql = f"""
                SELECT energy_source,
                ROUND(MIN(capacity))::INTEGER AS mincap, ROUND(AVG(capacity))::INTEGER AS avgcap,
                ROUND(MAX(capacity))::INTEGER AS maxcap,
                ROUND(MIN(temperature_setting),1)::DECIMAL(20,1) AS mintemp, ROUND(AVG(temperature_setting),1)::DECIMAL(20,1) AS
                avgtemp, ROUND(MAX(temperature_setting),1)::DECIMAL(20,1) AS maxtemp
                FROM waterheater AS wh, household AS hh, postalcode AS pc
                WHERE wh.email = hh.email AND hh.code = pc.code
                AND pc.state = '{self.drilldown_state}'
                GROUP BY energy_source
                ORDER BY energy_source;
            """
        self.drilldownDF = pd.read_sql(sql, conn, coerce_float=False)
        conn.close()

    def display_WH_stats(self):
        self.fetch_WH_stats()

        self.mainTable = Table(self.waterstatsframe, dataframe=self.statsDF, height=200, 
                               handle_left_click=self.handle_left_click)
        self.mainTable.cellwidth = 140
        self.mainTable.show()
        self.waterstatsframe.pack()

    def display_drilldown(self, row):
        self.drilldown_state = self.statsDF.iloc[row]["state"]
        self.fetch_drilldown()

        if self.drilldownDF.empty:
            self.drilldownTitleFrame.destroy()
            self.drilldownTitleFrame = tk.Frame(self)
            self.drilldownframe.destroy()
            self.drilldownframe = tk.Frame(self)

            errorLabel = tk.Label(self.drilldownframe, 
                                  text=f"No data for selected state: {self.drilldown_state}.", 
                                  foreground="red")
            errorLabel.grid(row=0, column=0)
            self.drilldownframe.pack(pady=(15, 0))
            return

        self.drilldownTitleFrame.destroy()
        self.drilldownTitleFrame = tk.Frame(self)
        self.drilldownTitle = tk.Label(self.drilldownTitleFrame, 
                                  text=f"Water Heater Energy Source Statistics for {self.drilldown_state}", 
                                  font=("Verdana", 10))
        self.drilldownTitle.grid()
        self.drilldownTitleFrame.pack(pady=(40,5))

        self.drilldownframe.destroy()
        self.drilldownframe = tk.Frame(self)

        drilldownTable = CustomTable(self.drilldownframe, dataframe=self.drilldownDF, height=135)
        drilldownTable.show()
        self.drilldownframe.pack()

    def handle_left_click(self, event):
        self.mainTable.clearSelected()
        self.mainTable.allrows = False
        rowclicked = self.mainTable.get_row_clicked(event)
        self.display_drilldown(rowclicked)