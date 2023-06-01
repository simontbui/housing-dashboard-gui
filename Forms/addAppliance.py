import tkinter as tk
from tkinter import StringVar
from tkinter import IntVar
import psycopg2
from tkinter import ttk
from utils import Utils


LARGE_FONT = ("Verdana", 12)

class AddAppliance(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        r = 0
        c = 1
        self.fields = {}

        frame_label = tk.Label(self, text='Add Appliance Information', font=LARGE_FONT, justify=tk.RIGHT)
        frame_label.grid(row = r, column = c, padx=10, pady=5, sticky=tk.W)

        manufacturer_List = self.pullSelectorList("""SELECT DISTINCT name FROM Manufacturer""")

        self.manu_selected = StringVar()
        self.manu_selected.set("SELECT")
        self.fields['manu_label'] = tk.Label(self, text='Manufacturer:', justify=tk.RIGHT)
        self.fields['manu'] = ttk.Combobox(self, textvariable=self.manu_selected, values=manufacturer_List, height=5, width=50)

        self.fields['model_label'] = ttk.Label(self, text='Model Name:', justify=tk.RIGHT)
        self.fields['model'] = tk.Text(self, height=1, width=50, wrap=None)

        self.fields['btu_label'] = ttk.Label(self, text='BTU Rating:', justify=tk.RIGHT)
        self.fields['btu'] = tk.Text(self, height=1, width=50, wrap=None)

        self.water_heater = IntVar()
        self.fields['water_heater_label'] = tk.Label(self, text='Appliance is Water Heater:', justify=tk.RIGHT)
        self.fields['water_heater'] = tk.Checkbutton(self, variable=self.water_heater, command=self.toggleWaterHeater)

        types = ["electric", "gas","thermosolar","heat pump"]
        self.es_selected = StringVar()
        self.es_selected.set("electric")
        self.fields['es_label'] = tk.Label(self, text='Water Heater Energy Source:', justify=tk.RIGHT)
        self.fields['es'] = ttk.Combobox(self, textvariable=self.es_selected, values=types, height=5, width=50)

        self.fields['capacity_label'] = ttk.Label(self, text='Water Heater Capacity:', justify=tk.RIGHT)
        self.fields['capacity'] = tk.Text(self, height=1, width=50, wrap=None)

        self.fields['temp_label'] = ttk.Label(self, text='Water Heater Current Temperature:', justify=tk.RIGHT)
        self.fields['temp'] = tk.Text(self, height=1, width=50, wrap=None)

        self.air_handler = IntVar()
        self.fields['air_handler_label'] = tk.Label(self, text='Appliance is Air Handler:', justify=tk.RIGHT)
        self.fields['air_handler'] = tk.Checkbutton(self, variable=self.air_handler, command=self.toggleAirHandler)

        self.ac = IntVar()
        self.fields['ac_label'] = tk.Label(self, text='Air Conditioner:', justify=tk.RIGHT)
        self.fields['ac'] = tk.Checkbutton(self, variable=self.ac, command=self.toggleAC)

        self.fields['eer_label'] = ttk.Label(self, text='Energy Efficiency Ratio:', justify=tk.RIGHT)
        self.fields['eer'] = tk.Text(self, height=1, width=50, wrap=None)
        
        self.heater = IntVar()
        self.fields['heat_label'] = tk.Label(self, text='Heater:', justify=tk.RIGHT)
        self.fields['heat'] = tk.Checkbutton(self, variable=self.heater, command=self.toggleH)

        heat_types = ["electric", "gas","fuel oil"]
        self.src_selected = StringVar()
        self.src_selected.set("electric")
        self.fields['src_label'] = tk.Label(self, text='Air Handler Heater Energy Source:', justify=tk.RIGHT)
        self.fields['src'] = ttk.Combobox(self, textvariable=self.src_selected, values=heat_types, height=5, width=50)

        self.hp = IntVar()
        self.fields['hp_label'] = tk.Label(self, text='Heat Pump:', justify=tk.RIGHT)
        self.fields['hp'] = tk.Checkbutton(self, variable=self.hp, command=self.toggleHP)

        self.fields['seer_label'] = ttk.Label(self, text='Seasonal Energy Efficiency Ratio:', justify=tk.RIGHT)
        self.fields['seer'] = tk.Text(self, height=1, width=50, wrap=None)

        self.fields['hspf_label'] = ttk.Label(self, text='Heating Seasonal Performance Factor:', justify=tk.RIGHT)
        self.fields['hspf'] = tk.Text(self, height=1, width=50, wrap=None)

        self.errors = StringVar()
        self.fields['form_requirements'] = tk.Label(self, text='Required', justify=tk.LEFT)
        self.fields['form_errors'] = tk.Label(self, textvariable=self.errors, justify=tk.LEFT)
        self.errors.set("")

        rcount = 0
        r = r + 1
        c = 0
        for field in self.fields.values():
            if rcount == 2:
                r = r + 1
                rcount = 0
            if c % 2 == 0:
                field.grid(row = r, column = c, padx=10, pady=5, sticky=tk.E)
            else:
                field.grid(row = r, column = c, padx=10, pady=5, sticky=tk.W)
            c = c + 1
            rcount = rcount + 1
            if c > 1: 
                c = 0
        r = r + 1

        button3 = ttk.Button(self, text="Next -->",
                             command=lambda: self.Submit())
        button3.grid(row = r, column = 2, padx=10, pady=5, sticky=tk.W)

        #Nothing is chosen initially
        self.disableWaterHeater()
        self.disableAirHandler()
    
    def enableAC(self):
        self.fields['eer'].config(state=tk.NORMAL)
    
    def enableHeater(self):
        self.fields['src'].config(state=tk.NORMAL)
    
    def enableHeatPump(self):
        self.fields['seer'].config(state=tk.NORMAL)
        self.fields['hspf'].config(state=tk.NORMAL)
    
    def disableAC(self):
        self.ac.set(0)
        self.fields['eer'].delete("1.0", "end")
        self.fields['eer'].config(state=tk.DISABLED)
    
    def disableHeater(self):
        self.heater.set(0)
        self.fields['src'].config(state=tk.DISABLED)
    
    def disableHeatPump(self):
        self.hp.set(0)
        self.fields['seer'].delete("1.0", "end")
        self.fields['seer'].config(state=tk.DISABLED)
        self.fields['hspf'].delete("1.0", "end")
        self.fields['hspf'].config(state=tk.DISABLED)
    
    def disableAirHandler(self):
        self.air_handler.set(0)
        self.disableAC()
        self.fields['ac'].config(state=tk.DISABLED)
        self.disableHeater()
        self.fields['heat'].config(state=tk.DISABLED)
        self.disableHeatPump()
        self.fields['hp'].config(state=tk.DISABLED)

    def enableAirHandler(self):
        self.fields['ac'].config(state=tk.NORMAL)
        self.fields['heat'].config(state=tk.NORMAL)
        self.fields['hp'].config(state=tk.NORMAL)
    
    def disableWaterHeater(self):
        self.water_heater.set(0)
        self.fields['es'].config(state=tk.DISABLED)
        self.fields['capacity'].delete("1.0", "end")
        self.fields['capacity'].config(state=tk.DISABLED)
        self.fields['temp'].delete("1.0", "end")
        self.fields['temp'].config(state=tk.DISABLED)
        
    def enableWaterHeater(self):
        self.fields['es'].config(state=tk.NORMAL)
        self.fields['capacity'].config(state=tk.NORMAL)
        self.fields['temp'].config(state=tk.NORMAL)
    
    def toggleAC(self):
        if self.ac.get():
            self.enableAC()
        else:
            self.disableAC()
    def toggleH(self):
        if self.heater.get():
            self.enableHeater()
        else:
            self.disableHeater()
    def toggleHP(self):
        if self.hp.get():
            self.enableHeatPump()
        else:
            self.disableHeatPump()
            
    def toggleAirHandler(self):
        if self.air_handler.get():
            self.enableAirHandler()
            self.disableWaterHeater()
            print("AH Toggled On")
        else:
            self.disableAirHandler()
            print("AH Toggle Off")

    
    def toggleWaterHeater(self):
        if self.water_heater.get():
            self.enableWaterHeater()
            self.disableAirHandler()
            print("WH Toggled On")
        else:
            self.disableWaterHeater()
            print("WH Toggle Off")

    def Submit(self):
        print("Submit Clicked")
        self.clearErrors()
        if self.validForm():
            if self.insert():
                print("Inserted into tables")
                self.controller.show_frame('ApplianceView')
            else:
                print("Appliance failed to insert into the database")

    def validForm(self):
        btu = self.fields['btu'].get("1.0", 'end-1c')
        eer = self.fields['eer'].get("1.0", 'end-1c')
        seer = self.fields['seer'].get("1.0", 'end-1c')
        hspf = self.fields['hspf'].get("1.0", 'end-1c')
        cap = self.fields['capacity'].get("1.0", 'end-1c')
        temp = self.fields['temp'].get("1.0", 'end-1c')

        if not self.water_heater.get() and not self.air_handler.get():
            self.postErrorToForm("Air Handler or Water Heater must be selected")
        elif btu == "" or not btu.isdigit():
            self.postErrorToForm("Please enter a whole number for BTU")
        elif self.ac.get() and (eer == "" or not Utils.is_tenth(eer)):
            self.postErrorToForm("Please enter a number for Energy Efficiency Ratio")
        elif self.hp.get() and (seer == "" or not Utils.is_tenth(seer)):
            self.postErrorToForm("Please enter a number to tenth decimal place for Seasonal Energy Efficiency Rating")
        elif self.hp.get() and (hspf == "" or not Utils.is_tenth(hspf)):
            self.postErrorToForm("Please enter a number to tenth decimal place for Heating Seasonal Performance Factor")
        elif self.water_heater.get() and (cap == "" or not Utils.is_tenth(cap)):
            self.postErrorToForm("Please enter a number rounded to the tenth decimal place for Water Heater Capacity")
        elif temp != "" and not temp.isdigit():
            self.postErrorToForm("Water Heater Current Temperature must be nothing or a whole number")
        elif self.manu_selected.get() == "SELECT":
            self.postErrorToForm("Please select a Manufacturer")
        elif self.air_handler.get():
            if not self.ac.get() and not self.hp.get() and not self.heater.get():
                self.postErrorToForm("Air Handler must have at least 1 heating/cooling method selected")
        
        if self.errors.get() == "":
            return True
        return False
    
    def pullSelectorList(self, sql):
        results = []
        try:
            conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
            
            cursor =  conn.cursor()
            print("Executing: " + sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            print("Manufacturers")
            print(result)
            results = [r[0] for r in result]
            results.append("SELECT")
            print(results)
            conn.close()
            
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            results.append("")
        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")

        return results

    def postErrorToForm(self, error):
        if self.errors.get() == "":
            self.errors.set(self.errors.get() + error)
        else:
            self.errors.set(self.errors.get() + "," + error)
    
    def clearErrors(self):
        self.errors.set("")
    
    def insert(self):
        if Utils.user_email == "":
            print('ERROR, email has not been set')
        results = True
        appliance_number = 0
        #Get count of appliances table and add 1 for the #
        appliance_number = self.getNextApplianceNumber()
        print("Appliance number is " + str(appliance_number))
        if appliance_number == 0:
            print("Failed to get next appliance number")
            return False
        
        if self.air_handler.get():
            #Insert into the appliances table with the email and number
            self.insertAppliance(appliance_number)
            #Insert into the airhandler table 
            self.insertAirHandler(appliance_number)

            #If AC Insert into AirConditioner Table
            if self.ac.get():
                self.insertAC(appliance_number)
            #If HP Insert into the HeatPump Table
            if self.hp.get():
                self.insertHP(appliance_number)
            #If Heater insert into the Heater Table
            if self.heater.get():
                self.insertHeater(appliance_number)
            results =True

        elif self.water_heater.get():
            #Insert into the appliances table with the email and number
            self.insertAppliance(appliance_number)
            #Insert into the WaterHeater Table
            self.insertWaterHeater(appliance_number)
            results =True
        else:
            print("Not a waterheater or an airhandler, ERROR!")
        
        return results
    def insertWrapper(self, sql, name):
        if self.insertSQL(sql):
            print("Insert Succeeded for " + name)
        else:
            print("Insert Failed for " + name)
    def getNextApplianceNumber(self):
        sql = """SELECT COUNT(*) FROM Appliance WHERE email='%s'""" % Utils.user_email
        results = self.selectSQL(sql)
        count = results[0]
        return int(count) + 1
    def insertAppliance(self, app_num):
        sql = """INSERT INTO Appliance (Email, Entry_Order_Number) VALUES ('%s','%s')""" % (Utils.user_email, app_num)
        self.insertWrapper(sql, "Appliance")
    def insertAirHandler(self, app_num):
        btu = self.fields['btu'].get("1.0", 'end-1c')
        model = self.fields['model'].get("1.0", 'end-1c')
        manufacturer = self.manu_selected.get()
        if(model == ""):
            model = 'null'
            sql = """INSERT INTO AirHandler (Email, Entry_Order_Number, BTU_Rating, Model_Name, Manufacturer) VALUES ('%s','%s','%s',%s,'%s')""" % (Utils.user_email, app_num, btu, model, manufacturer)
        else:
            sql = """INSERT INTO AirHandler (Email, Entry_Order_Number, BTU_Rating, Model_Name, Manufacturer) VALUES ('%s','%s','%s','%s','%s')""" % (Utils.user_email, app_num, btu, model, manufacturer)

        self.insertWrapper(sql, "AirHandler")

    def insertAC(self, app_num):
        eer = self.fields['eer'].get("1.0", 'end-1c')
        sql = """INSERT INTO AirConditioner (Email, Entry_Order_Number, EER) VALUES ('%s','%s',%s)""" % (Utils.user_email, app_num, eer)
        self.insertWrapper(sql, "AirConditioner")

    def insertHP(self, app_num):
        seer = self.fields['seer'].get("1.0", 'end-1c')
        hspf = self.fields['hspf'].get("1.0", 'end-1c')
        sql = """INSERT INTO HeatPump (Email, Entry_Order_Number, SEER, HSPF) VALUES ('%s','%s','%s','%s')""" % (Utils.user_email, app_num, seer, hspf)
        self.insertWrapper(sql, "HeatPump")

    def insertHeater(self, app_num):
        es = self.src_selected.get();
        sql = """INSERT INTO Heater (Email, Entry_Order_Number, Energy_Source) VALUES ('%s','%s','%s')""" % (Utils.user_email, app_num, es)
        self.insertWrapper(sql, "Heater")

    def insertWaterHeater(self, app_num):
        cap = self.fields['capacity'].get("1.0", 'end-1c')
        temp = '\''+ self.fields['temp'].get("1.0", 'end-1c') + '\''
        btu = self.fields['btu'].get("1.0", 'end-1c')
        model = '\''+ self.fields['model'].get("1.0", 'end-1c') + '\''
        es = self.es_selected.get()
        manufacturer = self.manu_selected.get()
        if(model == "''"):
            model = 'null'
        if(temp == "''"):
            temp = 'null'
        sql = """INSERT INTO WaterHeater (Email, entry_order_number, BTU_Rating, Model_Name, Manufacturer, Capacity, Temperature_Setting, Energy_Source) VALUES ('%s','%s','%s',%s,'%s','%s',%s,'%s')""" % (Utils.user_email,app_num,btu,model,manufacturer,cap,temp,es)

        self.insertWrapper(sql, "WaterHeater")

    def insertSQL(self, sql):
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
            results = cursor.fetchone()
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
    