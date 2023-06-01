import tkinter as tk
from tkinter import StringVar
import psycopg2
from tkinter import ttk
from utils import Utils
from functools import partial


LARGE_FONT = ("Verdana", 12)

class ApplianceView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        
        frame_label = tk.Label(self, text='Household Appliance', font=LARGE_FONT, justify=tk.RIGHT)
        frame_label.grid(row = 0, column = 0, padx=10, pady=5, sticky=tk.W)

        frame_label = tk.Label(self, text='List for ' + Utils.user_email, font=LARGE_FONT, justify=tk.RIGHT)
        frame_label.grid(row = 0, column = 1, padx=10, pady=5, sticky=tk.W)
        self.initializeTable([])

    def initializeTable(self, args):
        #Headers
        print("focus in")
        self.row = "Appliance #"
        self.manu = "Manufacturer"
        self.model = "Model"
        self.type = "Type"
        self.button = "Action"
        r = 1
        c = 1
        self.fields = {}
        
        sql_ah = """SELECT entry_order_number, model_name, manufacturer, '%s' as type FROM AirHandler WHERE email='%s'""" % ('AirHandler', Utils.user_email)
        sql_wh = """SELECT entry_order_number, model_name, manufacturer, '%s' as type FROM WaterHeater WHERE email='%s'""" % ('WaterHeater', Utils.user_email)
        sql = sql_ah + " UNION " + sql_wh + " ORDER BY entry_order_number ASC"

        applianceList = self.selectSQL(sql)
        print("ApplianceList")
        print(applianceList)

        self.fields[self.row] = tk.Label(self, text=self.row, justify=tk.RIGHT)
        self.fields[self.type] = tk.Label(self, text=self.type, justify=tk.LEFT)
        self.fields[self.manu] = tk.Label(self, text=self.manu, justify=tk.LEFT)
        self.fields[self.model] = tk.Label(self, text=self.model, justify=tk.LEFT)
        self.fields[self.button] = tk.Label(self, text=self.button, justify=tk.LEFT)
        for app in applianceList:
            row = app[0]
            model = app[1]
            manu = app[2]
            type = app[3]
            self.fields[self.row + str(row)] = tk.Label(self, text=str(row), justify=tk.RIGHT)
            self.fields[self.type + str(row)] = tk.Label(self, text=str(type), justify=tk.LEFT)
            self.fields[self.manu + str(row)] = tk.Label(self, text=str(manu), justify=tk.LEFT)
            self.fields[self.model + str(row)] = tk.Label(self, text=str(model), justify=tk.LEFT)
            self.fields[self.button + str(row)] = ttk.Button(self, text="delete", command=partial(self.deleteAppliance, row))

        self.appliance_count = len(applianceList)
        rcount = 0
        r = r + 1
        c = 0
        for field in self.fields.values():
            if rcount == 5:
                r = r + 1
                rcount = 0
            if c == 1:
                field.grid(row = r, column = c, padx=10, pady=5, sticky=tk.W)
            else:
                field.grid(row = r, column = c, padx=10, pady=5, sticky=tk.E)
            c = c + 1
            rcount = rcount + 1
            if c == 5: 
                c = 0
        r = r + 1

        self.button1 = ttk.Button(self, text="<-- Add Another Appliance",
                             command=lambda: self.controller.show_frame('AddAppliance'))
        self.button1.grid(row = r, column = 0, padx=10, pady=5, sticky=tk.W)

        self.errors = StringVar()
        self.fields['form_requirements'] = tk.Label(self, text='Requirements:', justify=tk.RIGHT)
        self.fields['form_errors'] = tk.Label(self, textvariable=self.errors, justify=tk.LEFT)
        self.errors.set("")

        self.fields['form_requirements'].grid(row=r, column=1, padx=10, pady=5, sticky=tk.E)
        self.fields['form_errors'].grid(row=r, column=2, padx=10, pady=5, sticky=tk.W)
        
        # self.button2 = ttk.Button(self, text="Back to Home",
        #                      command=lambda: self.controller.show_frame('StartPage'))
        # self.button2.grid(row = r, column = 1, padx=10, pady=5, sticky=tk.N)

        self.button3 = ttk.Button(self, text="Next -->",
                             command=lambda: self.Submit())
        self.button3.grid(row = r, column = 3, padx=10, pady=5, sticky=tk.W)

    def deleteAppliance(self, row):
        #Delete the row in question and remove it from GUI. 
        print("The Row " + str(row))
        execution = ["WaterHeater", "AirHandler", "AirConditioner", "HeatPump", "Heater"]
        for e in execution:
            sql = """DELETE FROM %s WHERE email='%s' AND entry_order_number='%s'""" % (e, Utils.user_email, row)
            if self.executeSQL(sql):
                print("SQL execution succeeded for " + e)
            else:
                print("SQL execution failed for " + e)

        self.fields[self.row + str(row)].destroy()
        self.fields[self.type + str(row)].destroy()
        self.fields[self.manu + str(row)].destroy()
        self.fields[self.model + str(row)].destroy()
        self.fields[self.button + str(row)].destroy()
        self.appliance_count = self.appliance_count - 1
        
    def postErrorToForm(self, error):
        if self.errors.get() == "":
            self.errors.set(self.errors.get() + error)
        else:
            self.errors.set(self.errors.get() + "," + error)
    
    def clearErrors(self):
        self.errors.set("")

    def Submit(self):
        print("Submit Clicked")
        if self.appliance_count > 0:
            self.clearErrors()
            self.controller.show_frame_2('AddPowerGeneration')
        else:
            error = "1 or more appliances"
            self.postErrorToForm(error);
            print(error)

    def executeSQL(self, sql):
        try:
            conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
            conn.autocommit = True
            
            cursor =  conn.cursor()
            print("Executing: " + sql)
            cursor.execute(sql)

            conn.close()
            return True
  
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
        return False

    def selectSQL(self, sql):
        results = []
        try:
            conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
            conn.autocommit = True
            
            cursor =  conn.cursor()
            print("Executing: " + sql)
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.close()
            return results
  
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
        return results
    