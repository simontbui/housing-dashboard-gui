import tkinter as tk
from tkinter import StringVar
from tkinter import IntVar
import psycopg2
from tkinter import ttk
import re
from utils import Utils

LARGE_FONT = ("Verdana", 12)

class HouseHold(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        r = 0
        c = 1
        self.fields = {}

        frame_label = tk.Label(self, text='Please Enter Your Household\'s Information', font=LARGE_FONT, justify=tk.RIGHT)
        frame_label.grid(row = r, column = c, padx=10, pady=5, sticky=tk.W)
    
        self.fields['email_label'] = tk.Label(self, text="Email:", justify=tk.RIGHT)
        self.fields['email'] = tk.Text(self, height=1, width=50, wrap=None)
        
        self.fields['postal_label'] = tk.Label(self, text='Postal Code:', justify=tk.RIGHT)
        self.fields['postal'] = tk.Text(self, height=1, width=50, wrap=None)

        self.fields['sqft_label'] = tk.Label(self, text='Square Footage:', justify=tk.RIGHT)
        self.fields['sqft'] = tk.Text(self, height=1, width=50, wrap=None)

        types = ["house", "apartment","townhome","condomimum", "mobile home"]
        self.selected = StringVar()
        self.selected.set("house")
        self.fields['type_label'] = tk.Label(self, text='Home Type:', justify=tk.RIGHT)
        self.fields['type'] = tk.OptionMenu(self, self.selected, *types)

        self.fields['heat_label'] = ttk.Label(self, text='Thermostat heating setting:', justify=tk.RIGHT)
        self.fields['heat'] = tk.Text(self, height=1, width=50, wrap=None)

        self.fields['cool_label'] = ttk.Label(self, text='Thermostat cooling setting:', justify=tk.RIGHT)
        self.fields['cool'] = tk.Text(self, height=1, width=50, wrap=None)

        self.no_heat = IntVar()
        self.fields['no_heat_label'] = tk.Label(self, text='No Heating:', justify=tk.RIGHT)
        self.fields['no_heat'] = tk.Checkbutton(self, variable=self.no_heat, command=self.clearHeat)

        self.no_cooling = IntVar()
        self.fields['no_cooling_label'] = tk.Label(self, text='No Cooling:', justify=tk.RIGHT)
        self.fields['no_cooling'] = tk.Checkbutton(self, variable=self.no_cooling, command=self.clearCool)

        self.electric = IntVar()
        self.fields['electric_label'] = tk.Label(self, text='Public Utility Electric:', justify=tk.RIGHT)
        self.fields['electric'] = tk.Checkbutton(self, variable=self.electric)

        self.gas = IntVar()
        self.fields['gas_label'] = tk.Label(self, text='Public Utility Gas:', justify=tk.RIGHT)
        self.fields['gas'] = tk.Checkbutton(self, variable=self.gas)

        self.steam = IntVar()
        self.fields['steam_label'] = tk.Label(self, text='Public Utility Steam:', justify=tk.RIGHT)
        self.fields['steam'] = tk.Checkbutton(self, variable=self.steam)

        self.fuel_oil = IntVar()
        self.fields['fuel_oil_label'] = tk.Label(self, text='Public Utility Fuel/Oil:', justify=tk.RIGHT)
        self.fields['fuel_oil'] = tk.Checkbutton(self, variable=self.fuel_oil)

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

        button2 = ttk.Button(self, text="Back to Home",
                             command=self.BackHome)
        button2.grid(row = r, column = 1, padx=10, pady=5, sticky=tk.N)

        button3 = ttk.Button(self, text="Next -->",
                             command=lambda: self.Submit())
        button3.grid(row = r, column = 2, padx=10, pady=5, sticky=tk.W)

    def clearCool(self):
        if self.no_cooling.get():
            print("No Cooling")
            self.fields['cool'].delete("1.0", "end")
            self.fields['cool'].config(state=tk.DISABLED)
        else:
            print("Cooling Normal")
            self.fields['cool'].config(state=tk.NORMAL)
    def clearHeat(self):
        if self.no_heat.get():
            print("No Heating")
            self.fields['heat'].delete("1.0", "end")
            self.fields['heat'].config(state=tk.DISABLED)
        else:
            print("Heating Normal")
            self.fields['heat'].config(state=tk.NORMAL)
    
    def Submit(self):
        #This is where all of the error checking will happen
        print("Submit Clicked")
        self.clearErrors()
        if self.validForm():
            if self.insert():
                self.clearPage()
                self.controller.show_frame('AddAppliance')
            else:
                print("Household failed to insert into the database")

    def BackHome(self):
        self.clearPage()
        self.controller.show_frame('StartPage')

    def clearPage(self):
        self.fields['email'].delete("1.0", "end")
        self.fields['email'].insert(tk.END, Utils.user_email)

    def validForm(self):
        if self.validEmail() and self.validPostalCode() and self.validSQFT() and self.validThermostatConfigs():
            return True
        else:
            return False
    
    def validEmail(self):
        input = self.fields['email'].get("1.0", 'end-1c')
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if input == "":
            self.postErrorToForm("Empty Email")
            return False
        elif not re.match(pattern, input):
            self.postErrorToForm("Invalid Email Format")
            return False
        try:
            conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
            sql = """SELECT DISTINCT email FROM HouseHold WHERE email='%s'""" %  (input)
            cursor =  conn.cursor()
            print("Executing: " + sql)
            cursor.execute(sql)
            results = cursor.fetchone()

            if results is None:
                print("Email does not exist " + input)
                return True
            else:
                self.postErrorToForm("Email Already Exists")
                return False
            
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
    
    def validPostalCode(self):
        input = self.fields['postal'].get("1.0", 'end-1c')
        if input == "":
            self.postErrorToForm("Empty Postal Code")
            return False
        elif not input.isdigit():
            self.postErrorToForm("Invalid Postal Code Format")
            return False
        try:
            conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
            
            sql = """SELECT DISTINCT code FROM PostalCode WHERE code='%s'""" %  (input)
            cursor =  conn.cursor()
            print("Executing: " + sql)
            cursor.execute(sql)
            results = cursor.fetchone()
            
            conn.close()

            if results is None:
                self.postErrorToForm("Postal Code Does Not Exist")
                return False
            else:
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
    
    def validSQFT(self):
        input = self.fields['sqft'].get("1.0", 'end-1c')
        if input == "":
            self.postErrorToForm("Empty Square Footage")
            return False
        elif not input.isdigit():
            self.postErrorToForm("Square Footage: Whole numbers only")
            return False
        else:
            return True
    
    def validThermostatConfigs(self):
        tempHeat = self.fields['heat'].get("1.0", 'end-1c')
        tempCool = self.fields['cool'].get("1.0", 'end-1c')
        if not self.no_heat.get() and (tempHeat == "" or not tempHeat.isdigit()):
            self.postErrorToForm("Select \'No Heating\' or enter whole number in \'Thermostat heating setting\'")
            return False
        elif self.no_heat.get() and (tempHeat != "" and tempHeat.isdigit()):
            self.no_heat.set(0)
        if not self.no_cooling.get() and (tempCool == "" or not tempCool.isdigit()):
            self.postErrorToForm("Select \'No Cooling\' or enter whole number in \'Thermostat cooling setting\'")
            return False
        elif self.no_cooling.get() and (tempCool != "" and tempCool.isdigit()):
            self.no_cooling.set(0)
        return True
    
    def postErrorToForm(self, error):
        if self.errors.get() == "":
            self.errors.set(self.errors.get() + error)
        else:
            self.errors.set(self.errors.get() + "," + error)
    
    def clearErrors(self):
        self.errors.set("")
    
    def insert(self):
        email = self.fields['email'].get("1.0", 'end-1c')
        #We inserted so the email is now set
        Utils.user_email = email
        home_type = self.selected.get()
        sqft = int(self.fields['sqft'].get("1.0", 'end-1c'))
        utilities = []
        #Thermostat
        if not self.no_heat.get():
            heating = int(self.fields['heat'].get("1.0", 'end-1c'))
        else:
            heating = "null"
        if not self.no_cooling.get():
            cooling = int(self.fields['cool'].get("1.0", 'end-1c'))
        else:
            cooling = "null"
        
        code = self.fields['postal'].get("1.0", 'end-1c')

        if self.electric.get():
            utilities.append('electric')
        if self.gas.get():
            utilities.append('gas')
        if self.steam.get():
            utilities.append('steam')
        if self.fuel_oil.get():
            utilities.append('fuel oil')
        
        try:
            conn = psycopg2.connect(dbname=Utils.database, user=Utils.user_name, password=Utils.password)
            conn.autocommit = True
            sql = """INSERT INTO Household VALUES ('%s','%s',%s,%s,%s,'%s')""" % (email,home_type,sqft,heating,cooling,code)
            
            cursor =  conn.cursor()
            print("Executing: " + sql)
            cursor.execute(sql)

            for ut in utilities:
                sql = """INSERT INTO PublicUtilities VALUES ('%s','%s')""" % (email, ut)
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
