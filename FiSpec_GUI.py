from tkinter import X, Frame

class FiSpec_GUI:
    def __init__(self, master):
        self.master=master
        self.frame_COM_select = Frame(master)
        self.frame_COM_select.place(x=5,y=5, width=400, height=400)

        self.frame_Measurements = Frame(master)
        self.frame_Measurements.place(x=5,y=405, width=400, height=400)