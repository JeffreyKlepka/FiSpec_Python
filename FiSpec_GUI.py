from tkinter import X, Frame

class FiSpec_GUI:
    def __init__(self, master):
        self.master=master
        self.frame_COM_select = Frame(master)
        self.frame_COM_select.place(x=5,y=5)