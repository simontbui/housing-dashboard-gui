import tkinter as tk
import psycopg2
import pandas as pd
from utils import Utils
from Custom_Objects.customtable import CustomTable   

LARGE_FONT = ("Verdana", 12)

class HouseholdByRadius(tk.Frame):

    def __init__(self, parent, controller):        
        tk.Frame.__init__(self, parent)
        
        self.headerframe = tk.Frame(self)
        self.formframe = tk.Frame(self)
        self.tableframe = tk.Frame(self)

        header = tk.Label(self.headerframe, text="Household Averages by Radius", font=LARGE_FONT)
        header.grid(row=0, column=1, padx=10, pady=5)
        self.headerframe.pack()  

        self.display_form()

        home_btn = tk.Button(self, text="Return To Reports Menu", command=lambda: controller.show_frame("ViewReports"))
        home_btn.pack(side="bottom", pady=50)

    def query_postalcode_validation(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)        
        cur = conn.cursor()
        sql = f"""
                SELECT * FROM postalcode WHERE code = '{self.postalEntryVar.get().strip()}'
               """
        
        cur.execute(sql)
        self.postalcode_data = cur.fetchall()
        cur.close()
        conn.close()

    def query_housebyradius(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)        
        sql = f"""
                WITH haversine_cte AS 
                (
                        SELECT code FROM 
                    (
                        SELECT t1.*, 
                        lat2 - lat1 deltalat,
                        lon2 - lon1 deltalon,
                        SIN((lat2-lat1)/2) * SIN((lat2-lat1)/2) + COS(lat1) * COS(lat2) * SIN((lon2-lon1)/2) * SIN((lon2-lon1)/2) AS lower_a,
                        2 * ATAN2(SQRT(SIN((lat2-lat1)/2) * SIN((lat2-lat1)/2) + COS(lat1) * COS(lat2) * SIN((lon2-lon1)/2) * SIN((lon2-lon1)/2)),
                                SQRT(1 - SIN((lat2-lat1)/2) * SIN((lat2-lat1)/2) + COS(lat1) * COS(lat2) * SIN((lon2-lon1)/2) * SIN((lon2-lon1)/2))) AS lower_c,
                        6371000 * 2 * atan2(SQRT(SIN((lat2-lat1)/2) * SIN((lat2-lat1)/2) + COS(lat1) * COS(lat2) * SIN((lon2-lon1)/2) * SIN((lon2-lon1)/2)),
                                SQRT(1 - SIN((lat2-lat1)/2) * SIN((lat2-lat1)/2) + COS(lat1) * COS(lat2) * SIN((lon2-lon1)/2) * SIN((lon2-lon1)/2))) AS lower_d
                        FROM
                        (
                            SELECT pc.code, pc.latitude latitude1, pc.longitude longitude1, pc.longitude*3.14/180 lon1, pc.latitude*3.14/180 lat1,
                            userInput.code userpc,
                            userInput.latitude latitude2,
                            userInput.longitude longitude2,
                            userInput.latitude * 3.14/180 lat2,
                            userInput.longitude * 3.14/180 lon2
                            FROM 
                            (SELECT * FROM postalcode) pc, 
                            (SELECT * FROM postalcode WHERE code = '{self.postalEntryVar.get().strip()}') userInput
                        ) AS t1
                    ) AS haversine
                    WHERE lower_d <= {self.selectedRadius.get()}*1609.4
                )
                    SELECT '{self.postalEntryVar.get().strip()}' AS usercodeinput, {self.selectedRadius.get()} AS userradiusinput, * FROM
                    (
                        SELECT 
                        COUNT(*) AS numhouseholds,
                        SUM((CASE WHEN household_type = 'house' THEN 1 ELSE 0 END)) AS numhouses,
                        SUM((CASE WHEN household_type = 'apartment' THEN 1 ELSE 0 END)) AS numapartments,
                        SUM((CASE WHEN household_type = 'townhome' THEN 1 ELSE 0 END)) AS numtownhomes,
                        SUM((CASE WHEN household_type = 'condominium' THEN 1 ELSE 0 END)) AS numcondominiums,
                        SUM((CASE WHEN household_type = 'mobile home' THEN 1 ELSE 0 END)) AS nummobilehomes,
                        ROUND(AVG(square_footage)) AS avgsqfootage,
                        ROUND(CAST(AVG(heating_setting) AS numeric),1) AS avgheatingtemp,
                        ROUND(CAST(AVG(cooling_setting) AS numeric), 1) AS avgcoolingtemp
                        FROM household 
                        WHERE code IN (SELECT code from haversine_cte)
                    ) AS householdstats,
                    (
                        SELECT 
                        STRING_AGG(DISTINCT public_utility, ',') AS publicutilities,
                        COUNT(DISTINCT (CASE WHEN util.email IS null THEN hh.email END)) AS numoffthegrid
                        FROM household AS hh 
                        LEFT JOIN publicutilities util ON hh.email = util.email
                        WHERE code IN (SELECT code FROM haversine_cte)
                    ) AS publicutilstats,
                    (
                        SELECT 
                        COUNT(DISTINCT (CASE WHEN pg.email IS NOT null THEN hh.email END)) AS numhomewithpowergen,
                        MODE() WITHIN GROUP (ORDER BY power_generation_type) AS mostcommongenerationtype,
                        ROUND(AVG(avg_kwh_generated)) AS avgmonthlypowergen,
                        COUNT(DISTINCT (CASE WHEN pg.email IS NOT null AND pg.storage_capacity IS NOT NULL THEN hh.email END)) numhomeswithbatterystorage
                        FROM household AS hh
                        LEFT JOIN powergeneration AS pg ON hh.email = pg.email
                        WHERE code IN (SELECT code FROM haversine_cte)
                    ) AS powergenstats;
               """
        self.household_stats_df = pd.read_sql(sql, conn, coerce_float=False)
        self.household_stats_df = self.household_stats_df.T.reset_index()
        self.household_stats_df.columns = ["Attribute", "Value"]
        conn.close()

    def display_form(self):
        postalLabel = tk.Label(self.formframe, text="Enter Postal Code:")
        postalLabel.grid(row=0, column=0, sticky=tk.E)

        self.postalEntryVar = tk.StringVar()
        postalEntry = tk.Entry(self.formframe, textvariable=self.postalEntryVar, width=10)
        postalEntry.grid(row=0, column=1, sticky=tk.W)

        radiusOptions = [0, 5, 10, 25, 50, 100, 250]
        self.selectedRadius = tk.IntVar()
        self.selectedRadius.set(0)

        searchRadiusLabel = tk.Label(self.formframe, text="Search Radius (mi):")
        searchRadiusLabel.grid(row=1, column=0, sticky=tk.E)

        searchRadiusDropdown = tk.OptionMenu(self.formframe, self.selectedRadius, *radiusOptions)
        searchRadiusDropdown.configure(width=4, height=1)
        searchRadiusDropdown.grid(row=1, column=1, sticky=tk.W)

        search_btn = tk.Button(self.formframe, text="Search", command=lambda: self.display_housebyradius())
        search_btn.grid(row=1, column=2, padx=10)

        self.formframe.pack()


    def display_postalcode_invalid(self):
        errorLabel = tk.Label(self.tableframe, text="INVALID POSTAL CODE!", foreground="red")
        errorLabel.pack()
        self.tableframe.pack()

    def display_housebyradius(self):
        self.query_postalcode_validation()
        self.tableframe.destroy()
        self.tableframe = tk.Frame(self)

        if len(self.postalcode_data) == 0:
            self.display_postalcode_invalid()
            return

        self.query_housebyradius()
        table = CustomTable(self.tableframe, dataframe=self.household_stats_df,
                            editable=False, width=425, maxcellwidth=210)
        table.show()
        self.tableframe.pack(pady=40)