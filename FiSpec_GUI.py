from tkinter import Frame
from tkinter import Label

class FiSpec_GUI:
    def __init__(self, master):
        self.master=master
        self.frame_COM_select = Frame(master)
        self.frame_COM_select.place(x=5,y=5, width=495, height=45)

        self.frame_start_meas = Frame(master)
        self.frame_start_meas.place(x=5,y=50, width=495, height=45)

        self.frame_start_spec = Frame(master)
        self.frame_start_spec.place(x=5,y=100, width=495, height=45)

        self.frame_intgt = Frame(master)
        self.frame_intgt.place(x=5,y=150, width=495, height=45)
        
        self.frame_Plot = Frame(master)
        self.frame_Plot.place(x=5,y=500, width=990, height=495)

        self.frame_Display_Data = Frame(master)
        self.frame_Display_Data.place(x=500,y=5, width=495, height=495)

        self.label_Peak1 = Label(self.frame_Display_Data, text="Peak 1: ")
        self.label_Peak1.place(x=10, y=10)
        self.label_Peak2 = Label(self.frame_Display_Data, text="Peak 2: ")
        self.label_Peak2.place(x=10, y=30)
        self.label_Peak3 = Label(self.frame_Display_Data, text="Peak 3: ")
        self.label_Peak3.place(x=10, y=50)
        self.label_Peak4 = Label(self.frame_Display_Data, text="Peak 4: ")
        self.label_Peak4.place(x=10, y=70)

        self.label_Ampl1 = Label(self.frame_Display_Data, text="Amplitude 1: ")
        self.label_Ampl1.place(x=200, y=10)
        self.label_Ampl2 = Label(self.frame_Display_Data, text="Amplitude 2: ")
        self.label_Ampl2.place(x=200, y=30)
        self.label_Ampl3 = Label(self.frame_Display_Data, text="Amplitude 3: ")
        self.label_Ampl3.place(x=200, y=50)
        self.label_Ampl4 = Label(self.frame_Display_Data, text="Amplitude 4: ")
        self.label_Ampl4.place(x=200, y=70)

