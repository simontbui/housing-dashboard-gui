import tkinter as tk
import psycopg2
from utils import Utils

LARGE_FONT = ("Verdana", 16)
TABLE_TITLE_FONT = ("Verdana", 13)
TABLE_FONT = ("Verdana", 12)

class OffTheGridDashboard(tk.Frame):

    def __init__(self, parent, controller):        
        tk.Frame.__init__(self, parent)

        self.headerframe = tk.Frame(self)
        self.statewithmostframe = tk.Frame(self)
        self.avgcapacityframe = tk.Frame(self)
        self.powergenpercentagesframe = tk.Frame(self)
        self.onoffgridavgcapacityframe = tk.Frame(self)
        self.minavgmaxBTUbyapptypeframe = tk.Frame(self)

        header = tk.Label(self.headerframe, text="Off-the-grid Household Dashboard", font=LARGE_FONT)
        header.grid(row=0, column=1, sticky=tk.W)
        self.headerframe.pack()       

        self.display_statewithmostoffgrid()
        self.display_avgcapacity()
        self.display_powergenpercentages()
        self.display_onoffgridavgcapacity()
        self.display_minavgmaxBTUbyapptype()

        home_btn = tk.Button(self, text="Return To Reports Menu", command=lambda: controller.show_frame("ViewReports"))
        home_btn.pack(side="bottom", pady=(1, 50))

    def fetch_statewithmostoffgrid(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        cur = conn.cursor()
        sql = """
                SELECT pc.state, COUNT(*) AS numhouseholds
                FROM household AS hh, postalcode AS pc
                WHERE hh.code = pc.code
                AND email NOT IN (SELECT email FROM publicutilities)
                GROUP BY pc.state
                ORDER BY COUNT(*) desc
                LIMIT 1;
              """
        cur.execute(sql)
        self.statewithmostoffgrid_data = cur.fetchall()
        cur.close()
        conn.close()

    def fetch_avgcapacity(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        cur = conn.cursor()
        sql = """
                SELECT ROUND(AVG(storage_capacity)) AS avgstoragecapacity FROM
                powergeneration WHERE email NOT IN (SELECT email FROM publicutilities);
              """
        cur.execute(sql)
        self.avgcapacity_data = cur.fetchall()
        cur.close()
        conn.close()

    def fetch_powergenpercentages(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        cur = conn.cursor()
        sql = """
                select  
                case when powergentypes in ('solar-electric', 'wind') then powergentypes else 'mixed' end,
                round(count(*) * 100.0 / sum(count(*)) over(), 1)
                from
                (
                    select hh.email, string_agg(distinct power_generation_type, ',') powergentypes 
                    from household hh, powergeneration pg
                    where hh.email = pg.email
                    and hh.email not in (select email from publicutilities)
                    group by hh.email
                ) q
                group by case when powergentypes in ('solar-electric', 'wind') then powergentypes else 'mixed' end;
              """
        cur.execute(sql)
        self.powergenpercentages_data = cur.fetchall()
        cur.close()
        conn.close()

    def fetch_onoffgridavgcapacity(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        cur = conn.cursor()
        sql = """
                SELECT
                (
                SELECT round(CAST(AVG(capacity) AS numeric), 1) AS avgcapactiy
                FROM waterheater
                WHERE email IN (SELECT email FROM publicutilities)
                ) AS onthegridavgcapacity,
                (
                SELECT ROUND(CAST(AVG(capacity) AS numeric), 1) AS avgcapactiy
                FROM waterheater
                WHERE email NOT IN (SELECT email FROM publicutilities)
                ) AS offthegridavgcapacity;
              """
        cur.execute(sql)
        self.onoffgridavgcapacity_data = cur.fetchall()
        cur.close()
        conn.close()

    def fetch_minavgmaxBTUbyapptype(self):
        conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
        cur = conn.cursor()
        sql = """
            SELECT 'airhandler' AS ApplianceType, 
            CASE WHEN ROUND(MIN(btu_rating)) is not null THEN ROUND(MIN(btu_rating))::INTEGER ELSE 0 END AS minbtu,
            CASE WHEN ROUND(AVG(btu_rating)) is not null THEN ROUND(AVG(btu_rating))::INTEGER ELSE 0 END AS avgbtu,
            CASE WHEN ROUND(MAX(btu_rating)) is not null THEN ROUND(MAX(btu_rating))::INTEGER ELSE 0 END AS maxbtu
            FROM airhandler
            WHERE email NOT IN (SELECT email from publicutilities)
            UNION
            SELECT 'waterheater' AS ApplianceType, 
            CASE WHEN ROUND(MIN(btu_rating)) is not null THEN ROUND(MIN(btu_rating))::INTEGER ELSE 0 END AS minbtu,
            CASE WHEN ROUND(AVG(btu_rating)) is not null THEN ROUND(AVG(btu_rating))::INTEGER ELSE 0 END AS avgbtu,
            CASE WHEN ROUND(MAX(btu_rating)) is not null THEN ROUND(MAX(btu_rating))::INTEGER ELSE 0 END AS maxbtu
            FROM waterheater
            WHERE email NOT IN (SELECT email FROM publicutilities)
            UNION
            SELECT 'airconditioner' AS ApplianceType,
            CASE WHEN ROUND(MIN(btu_rating)) is not null THEN ROUND(MIN(btu_rating))::INTEGER ELSE 0 END AS minbtu,
            CASE WHEN ROUND(AVG(btu_rating)) is not null THEN ROUND(AVG(btu_rating))::INTEGER ELSE 0 END AS avgbtu,
            CASE WHEN ROUND(MAX(btu_rating)) is not null THEN ROUND(MAX(btu_rating))::INTEGER ELSE 0 END AS maxbtu
            FROM airconditioner ac, airhandler ah 
            WHERE ac.email = ah.email AND ac.entry_order_number = ah.entry_order_number
            AND ah.email NOT IN (SELECT email FROM publicutilities)
            UNION
            SELECT 'heater' AS ApplianceType,
            CASE WHEN ROUND(MIN(btu_rating)) is not null THEN ROUND(MIN(btu_rating))::INTEGER ELSE 0 END AS minbtu,
            CASE WHEN ROUND(AVG(btu_rating)) is not null THEN ROUND(AVG(btu_rating))::INTEGER ELSE 0 END AS avgbtu,
            CASE WHEN ROUND(MAX(btu_rating)) is not null THEN ROUND(MAX(btu_rating))::INTEGER ELSE 0 END AS maxbtu
            FROM heater h, airhandler ah 
            WHERE h.email = ah.email AND h.entry_order_number = ah.entry_order_number
            AND ah.email NOT IN (SELECT email FROM publicutilities)
            UNION
            SELECT 'heatpump' AS ApplianceType,
            CASE WHEN ROUND(MIN(btu_rating)) is not null THEN ROUND(MIN(btu_rating))::INTEGER ELSE 0 END AS minbtu,
            CASE WHEN ROUND(AVG(btu_rating)) is not null THEN ROUND(AVG(btu_rating))::INTEGER ELSE 0 END AS avgbtu,
            CASE WHEN ROUND(MAX(btu_rating)) is not null THEN ROUND(MAX(btu_rating))::INTEGER ELSE 0 END AS maxbtu
            FROM heatpump hp, airhandler ah 
            WHERE hp.email = ah.email AND hp.entry_order_number = ah.entry_order_number
            AND ah.email NOT IN (SELECT email FROM publicutilities);
              """
        cur.execute(sql)
        self.minavgmaxBTU_data = cur.fetchall()
        cur.close()
        conn.close()

    def display_statewithmostoffgrid(self):
        self.fetch_statewithmostoffgrid()

        nrows = len(self.statewithmostoffgrid_data)
        ncols = len(self.statewithmostoffgrid_data[0])

        table_title = tk.Label(self.statewithmostframe, text="State with the most off-the-grid households",
                               justify="center")
        table_title.configure(font=TABLE_TITLE_FONT)
        table_title.grid(row=0, column=0, columnspan=6)

        self.e = tk.Entry(self.statewithmostframe, width=5, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=2, sticky=tk.E)
        self.e.insert(0, "State")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.statewithmostframe, width=5, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=3, sticky=tk.W)
        self.e.insert(0, "Count")
        self.e.configure(state="disabled", disabledforeground="black")

        for i in range(nrows):
            for j in range(ncols):
                self.e = tk.Entry(self.statewithmostframe, width=5, font=TABLE_FONT, justify=tk.CENTER)
                if j % 2 == 0:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.E)
                else:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.W)
                self.e.insert(0, self.statewithmostoffgrid_data[i][j])
                self.e.configure(state="disabled")
        self.statewithmostframe.pack(padx=10, pady=5)

    def display_avgcapacity(self):
        self.fetch_avgcapacity()

        table_title = tk.Label(self.avgcapacityframe, text="Average battery storage capacity for off-the-grid households", justify="center")
        table_title.configure(font=TABLE_TITLE_FONT)
        table_title.grid(row=0, column=0, columnspan=21)

        self.e = tk.Entry(self.avgcapacityframe, width=10, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=10)
        self.e.insert(0, "AvgCapacity")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.avgcapacityframe, width=10, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=2, column=10)
        self.e.insert(0, self.avgcapacity_data[0][0])
        self.e.configure(state="disabled")

        self.avgcapacityframe.pack(padx=10, pady=5)

    def display_powergenpercentages(self):
        self.fetch_powergenpercentages()

        nrows = len(self.powergenpercentages_data)
        ncols = len(self.powergenpercentages_data[0])

        table_title = tk.Label(self.powergenpercentagesframe, text="Percentage of each power generation type across off-the-grid households", justify="center")
        table_title.configure(font=TABLE_TITLE_FONT)
        table_title.grid(row=0, column=0, columnspan=6)

        self.e = tk.Entry(self.powergenpercentagesframe, width=15, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=2, sticky=tk.E)
        self.e.insert(0, "PowerGenType")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.powergenpercentagesframe, width=15, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=3, sticky=tk.W)
        self.e.insert(0, "Percentage")
        self.e.configure(state="disabled", disabledforeground="black")

        for i in range(nrows):
            for j in range(ncols):
                self.e = tk.Entry(self.powergenpercentagesframe, width=15, font=TABLE_FONT, justify=tk.CENTER)
                if j % 2 == 0:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.E)
                else:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.W)
                self.e.insert(0, self.powergenpercentages_data[i][j])
                self.e.configure(state="disabled")
        self.powergenpercentagesframe.pack(padx=10, pady=5)

    def display_onoffgridavgcapacity(self):
        self.fetch_onoffgridavgcapacity()

        nrows = len(self.onoffgridavgcapacity_data)
        ncols = len(self.onoffgridavgcapacity_data[0])

        table_title = tk.Label(self.onoffgridavgcapacityframe, text="Average water heater gallon capacity for off-the-grid and on-the-grid households", justify="center")
        table_title.configure(font=TABLE_TITLE_FONT)
        table_title.grid(row=0, column=0, columnspan=6)

        self.e = tk.Entry(self.onoffgridavgcapacityframe, width=10, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=2, sticky=tk.E)
        self.e.insert(0, "OffGridAvg")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.onoffgridavgcapacityframe, width=10, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=3, sticky=tk.W)
        self.e.insert(0, "OnGridAvg")
        self.e.configure(state="disabled", disabledforeground="black")

        for i in range(nrows):
            for j in range(ncols):
                self.e = tk.Entry(self.onoffgridavgcapacityframe, width=10, font=TABLE_FONT, justify=tk.CENTER)
                if j % 2 == 0:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.E)
                else:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.W)

                if self.onoffgridavgcapacity_data[i][j] == None:
                    self.e.insert(0, "N/A")
                else:
                    self.e.insert(0, self.onoffgridavgcapacity_data[i][j])
                self.e.configure(state="disabled")
        self.onoffgridavgcapacityframe.pack(padx=10, pady=5)

    def display_minavgmaxBTUbyapptype(self):
        self.fetch_minavgmaxBTUbyapptype()

        nrows = len(self.minavgmaxBTU_data)
        ncols = len(self.minavgmaxBTU_data[0])

        table_title = tk.Label(self.minavgmaxBTUbyapptypeframe, text="Min, Avg, Max BTU ratings for off-the-grid households", justify="center")
        table_title.configure(font=TABLE_TITLE_FONT)
        table_title.grid(row=0, column=0, columnspan=6)

        self.e = tk.Entry(self.minavgmaxBTUbyapptypeframe, width=13, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=2)
        self.e.insert(0, "ApplianceType")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.minavgmaxBTUbyapptypeframe, width=13, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=3)
        self.e.insert(0, "MinBTU")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.minavgmaxBTUbyapptypeframe, width=13, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=4)
        self.e.insert(0, "AvgBTU")
        self.e.configure(state="disabled", disabledforeground="black")

        self.e = tk.Entry(self.minavgmaxBTUbyapptypeframe, width=13, font=TABLE_FONT, justify=tk.CENTER)
        self.e.grid(row=1, column=5)
        self.e.insert(0, "MaxBTU")
        self.e.configure(state="disabled", disabledforeground="black")

        for i in range(nrows):
            for j in range(ncols):
                self.e = tk.Entry(self.minavgmaxBTUbyapptypeframe, width=13, font=TABLE_FONT, justify=tk.CENTER)
                if j % 2 == 0:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.E)
                else:
                    self.e.grid(row=i+2, column=j+2, sticky=tk.W)

                if self.minavgmaxBTU_data[i][j] == None:
                    self.e.insert(0, "N/A")
                else:
                    self.e.insert(0, self.minavgmaxBTU_data[i][j])
                self.e.configure(state="disabled")
        self.minavgmaxBTUbyapptypeframe.pack(padx=10, pady=5)