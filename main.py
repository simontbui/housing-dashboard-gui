import tkinter as tk
from Forms.household import HouseHold
from Forms.addAppliance import AddAppliance
from Forms.applianceView import ApplianceView
from Forms.submissionComplete import SubComp
from Forms.add_power_gen import AddPowerGeneration
from Forms.power_gen_listing import PowerGenerationSummary
from Reports.mfgsearch import MfgSearch
from Reports.heatcooldetails import HeatCoolDetails
from Reports.waterheaterstats import WaterHeaterStats
from Reports.offthegriddashboard import OffTheGridDashboard
from Reports.householdbyradius import HouseholdByRadius
from Reports.top25 import Top25
from Reports.view_reports_menu import ViewReports

LARGE_FONT = ("Verdana", 12)

class Dashboard(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Dashboard")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, ViewReports, Top25, HouseHold, AddAppliance, ApplianceView, AddPowerGeneration,
                  PowerGenerationSummary, SubComp, MfgSearch, HeatCoolDetails, WaterHeaterStats, OffTheGridDashboard,
                  HouseholdByRadius):
            frame = F(self.container, self)
            self.frames[frame.__class__.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame('StartPage')

    def show_frame(self, cont):
        frame = self.frames[cont]
        if frame:
            cl = frame.__class__
            frame.destroy()
            frame = cl(self.container, self)
            self.frames[frame.__class__.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_frame_2(self, cont):
        frame = self.frames[cont]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self,
                         text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = tk.Button(self,
                           width=30,
                           borderwidth=5,
                           text="Enter House Hold Information",
                           command=lambda: controller.show_frame('HouseHold'))
        button.pack(pady=10, padx=10)

        reports_button = tk.Button(self,
                                   width=30,
                                   borderwidth=5,
                                   text="View Reports",
                                   command=lambda: controller.show_frame('ViewReports'))
        reports_button.pack(pady=10, padx=10)


if __name__ == '__main__':
    app = Dashboard()
    app.mainloop()