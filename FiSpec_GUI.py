from tkinter import X, Frame

class FiSpec_GUI:
    def __init__(self, master):
        self.master=master
        self.frame_COM_select = Frame(master)
        self.frame_COM_select.place(x=5,y=5, width=495, height=45)

        self.frame_start_meas = Frame(master)
        self.frame_start_meas.place(x=5,y=50, width=495, height=45)

        self.frame_start_spec = Frame(master)
        self.frame_start_spec.place(x=5,y=105, width=495, height=45)
        
        self.frame_Plot = Frame(master)
        self.frame_Plot.place(x=5,y=500, width=990, height=495)

        self.frame_Display_Data = Frame(master)
        self.frame_Display_Data.place(x=500,y=5, width=495, height=495)