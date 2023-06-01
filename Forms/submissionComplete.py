import tkinter as tk
import tkinter as tk
from tkinter import ttk

LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)

class SubComp(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Submission Complete!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        label2 = tk.Label(self, text="Thank you for providing your information!", font=MEDIUM_FONT)
        label2.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame('StartPage'))
        button1.pack()


