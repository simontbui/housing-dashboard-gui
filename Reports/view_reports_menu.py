import tkinter as tk

LARGE_FONT = ("Verdana", 12)

class ViewReports(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.fields = {}

        pad_x = 5
        pad_y = 5
        b_width = 5
        width_var = 30

        frame_label = tk.Label(self, text='View Reports', font=LARGE_FONT, justify=tk.LEFT)
        frame_label.pack()

        self.fields['top25'] = tk.Button(self, width=width_var, text="Top 25 Popular Manufacturers",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('Top25'))
        self.fields['top25'].pack(padx=pad_x, pady=pad_y)


        self.fields['man/model_search'] = tk.Button(self, width=width_var, text="Manufacturer/Model Search",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('MfgSearch'))
        self.fields['man/model_search'].pack(padx=pad_x, pady=pad_y)


        self.fields['heat/cool_details'] = tk.Button(self, width=width_var, text="Heating/cooling Method Details",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('HeatCoolDetails'))
        self.fields['heat/cool_details'].pack(padx=pad_x, pady=pad_y)


        self.fields['waterHeaterStats'] = tk.Button(self, width=width_var, text="Water Heater Statistics by State",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('WaterHeaterStats'))
        self.fields['waterHeaterStats'].pack(padx=pad_x, pady=pad_y)


        self.fields['offTheGrid'] = tk.Button(self, width=width_var, text="Off-the-grid Household Dashboard",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('OffTheGridDashboard'))
        self.fields['offTheGrid'].pack(padx=pad_x, pady=pad_y)


        self.fields['offTheGrid'] = tk.Button(self, width=width_var, text="Household Averages by Radius",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('HouseholdByRadius'))
        self.fields['offTheGrid'].pack(padx=pad_x, pady=pad_y)


        self.fields['home_button'] = tk.Button(self, width=width_var, text="Return To Home Page",
                                               borderwidth=b_width,
                                               command=lambda: self.controller.show_frame('StartPage'))
        self.fields['home_button'].pack(padx=pad_x, pady=pad_y)