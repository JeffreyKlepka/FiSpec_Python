# FiSens FiSpec, GUI Class - Coded with Python. March, 2022

from tkinter import Frame, StringVar, Label, Entry, Button, OptionMenu
from tkinter import DISABLED
from tkinter import NORMAL
import serial.tools.list_ports
# The GUI class. All tkinter widgets (Frames, Buttons, Labels, etc.) are defined as attributes.
# Also, positioning of those widgets is specified in this class
class FiSpec_GUI:
    def __init__(self, master):
        self.master=master
        # ----------
        self.frame_COM_select = Frame(master)
        self.frame_COM_select.place(x=5,y=5, width=490, height=40)

        self.portObj = StringVar(master)
        self.portList = ["COM-Ports"]
        self.portObj.set(self.portList[0])
        self.drop_COM = OptionMenu(self.frame_COM_select, self.portObj, *self.portList)
        self.drop_COM.grid(row=0, column=0)

        self.refreshCOM_Bt = Button(self.frame_COM_select, text="Refresh List")
        self.refreshCOM_Bt.place(x=150, y=2, width=120)

        self.connect_COM_Bt = Button(self.frame_COM_select, text="Connect Port")
        self.connect_COM_Bt.place(x=300, y=2, width=120)
        # ----------
        self.frame_start_meas = Frame(master)
        self.frame_start_meas.place(x=5,y=50, width=490, height=45)

        self.toggleMeasMode_Bt = Button(self.frame_start_meas, text="Peak / Amplitude")
        self.toggleMeasMode_Bt.place(x=300, y=2, width=120)

        self.meas_Bt = Button(self.frame_start_meas, text="Start Measurement")
        self.meas_Bt.place(x=150, y=2, width=120)
        # ----------
        self.frame_start_spec = Frame(master)
        self.frame_start_spec.place(x=5,y=100, width=490, height=45)

        self.spec_Bt = Button(self.frame_start_spec, text="Start Spectrum")
        self.spec_Bt.place(x=150, y=2, width=120)  

        # ----------
        self.frame_intgt = Frame(master)
        self.frame_intgt.place(x=5,y=150, width=490, height=45)
        
        self.intT_In = Entry(self.frame_intgt, width=20)
        self.intT_In.place(x=15, y=2)
        self.intT_In.insert(0, "50000")

        self.intT_Bt = Button(self.frame_intgt, text="Set Integration Time")
        self.intT_Bt.place(x=150, y=0, width=120)
        # ----------
        self.frame_setCh = Frame(master)
        self.frame_setCh.place(x=5,y=200, width=490, height=45)
        
        self.setCh_In = Entry(self.frame_setCh, width=20)
        self.setCh_In.place(x=15, y=2)
        self.setCh_In.insert(0, "4")

        self.setCh_Bt = Button(self.frame_setCh, text="Active Channels")
        self.setCh_Bt.place(x=150, y=0, width=120)
        # ----------
        self.frame_setAv = Frame(master)
        self.frame_setAv.place(x=5,y=250, width=490, height=45)

        self.setAv_In = Entry(self.frame_setAv, width=20)
        self.setAv_In.place(x=15, y=2)
        self.setAv_In.insert(0, "2")

        self.setAv_Bt = Button(self.frame_setAv, text="Set Averaging")
        self.setAv_Bt.place(x=150, y=0, width=120)
        # ----------
        self.frame_setZe = Frame(master)
        self.frame_setZe.place(x=5,y=300, width=490, height=45)

        self.setZe_Bt = Button(self.frame_setZe, text="Set Zero Values")
        self.setZe_Bt.place(x=150, y=0, width=120)
        # ----------
        self.frame_autoO = Frame(master)
        self.frame_autoO.place(x=5,y=350, width=490, height=45)

        self.setAO_In = Entry(self.frame_autoO, width=20)
        self.setAO_In.place(x=15, y=2)
        self.setAO_In.insert(0, "2")

        self.setAO_Bt = Button(self.frame_autoO, text="Auto-optimize")
        self.setAO_Bt.place(x=150, y=0, width=120)
        # ----------
        self.frame_Plot = Frame(master)
        self.frame_Plot.place(x=5,y=500, width=990, height=495)

        self.frame_Display_Data = Frame(master)
        self.frame_Display_Data.place(x=500,y=5, width=495, height=90)

        self.label_Peak1 = Label(self.frame_Display_Data, text="Peak 1: ")
        self.label_Peak1.place(x=10, y=5)
        self.label_Peak2 = Label(self.frame_Display_Data, text="Peak 2: ")
        self.label_Peak2.place(x=10, y=25)
        self.label_Peak3 = Label(self.frame_Display_Data, text="Peak 3: ")
        self.label_Peak3.place(x=10, y=45)
        self.label_Peak4 = Label(self.frame_Display_Data, text="Peak 4: ")
        self.label_Peak4.place(x=10, y=65)

        self.label_Ampl1 = Label(self.frame_Display_Data, text="Amplitude 1: ")
        self.label_Ampl1.place(x=200, y=5)
        self.label_Ampl2 = Label(self.frame_Display_Data, text="Amplitude 2: ")
        self.label_Ampl2.place(x=200, y=25)
        self.label_Ampl3 = Label(self.frame_Display_Data, text="Amplitude 3: ")
        self.label_Ampl3.place(x=200, y=45)
        self.label_Ampl4 = Label(self.frame_Display_Data, text="Amplitude 4: ")
        self.label_Ampl4.place(x=200, y=65)
        # ----------
        self.frame_wl = Frame(master)
        self.frame_wl.place(x=500, y=100, width=180, height=195)

        self.label_wl_1 = Label(self.frame_wl, text="Wavelength 1: ")
        self.label_wl_1.place(x=10, y=25)

        self.setwl_1 = Entry(self.frame_wl, width=10)
        self.setwl_1.place(x=100, y=25)
        self.setwl_1.insert(0, "8200000")

        self.label_wl_2 = Label(self.frame_wl, text="Wavelength 2: ")
        self.label_wl_2.place(x=10, y=50)

        self.setwl_2 = Entry(self.frame_wl, width=10)
        self.setwl_2.place(x=100, y=50)
        self.setwl_2.insert(0, "8300000")

        self.label_wl_3 = Label(self.frame_wl, text="Wavelength 3: ")
        self.label_wl_3.place(x=10, y=75)

        self.setwl_3 = Entry(self.frame_wl, width=10)
        self.setwl_3.place(x=100, y=75)
        self.setwl_3.insert(0, "8400000")

        self.label_wl_4 = Label(self.frame_wl, text="Wavelength 1: ")
        self.label_wl_4.place(x=10, y=100)

        self.setwl_4 = Entry(self.frame_wl, width=10)
        self.setwl_4.place(x=100, y=100)
        self.setwl_4.insert(0, "8500000")

        self.setwl_Bt = Button(self.frame_wl, text="Set Wavelengths")
        self.setwl_Bt.place(x=20, y=135, width=120)

    def checkCOMs(self): 
        # will be called from thread t_checkCOMs every 2 seconds. Updates the list of COM-Ports shown in the optionsmenu of the GUI
        # first destroy old widget and clear old list
        self.drop_COM.destroy()
        self.portList.clear()
        
        ports=serial.tools.list_ports.comports() #get available COM-Ports
        # and add them to the list
        for onePort in ports:
            self.portList.append(str(onePort)[0:4])
            # self.portObj.set(self.portList[0])
        # if no devices are found
        if len(self.portList) == 0:
            self.portList.append("No devices found!")
            self.portObj.set(self.portList[0])
            print(self.portList)
        # create new optionsmenu and place it in the GUI
        self.drop_COM = OptionMenu(self.frame_COM_select, self.portObj, *self.portList)
        self.drop_COM.grid(row=0, column=0)

    def enableButtons(self):
        self.toggleMeasMode_Bt.configure(state=NORMAL)
        self.spec_Bt.configure(state=NORMAL)
        self.meas_Bt.configure(state=NORMAL)
        self.intT_Bt.configure(state=NORMAL)
        self.setCh_Bt.configure(state=NORMAL)
        self.setAv_Bt.configure(state=NORMAL)
        self.setAO_Bt.configure(state=NORMAL)
        self.setZe_Bt.configure(state=NORMAL)

    def disableButtons(self):
        self.toggleMeasMode_Bt.configure(state=DISABLED)
        self.spec_Bt.configure(state=DISABLED, text='Start Spectrum')
        self.meas_Bt.configure(state=DISABLED, text='Start Measurement')
        self.intT_Bt.configure(state=DISABLED)
        self.setCh_Bt.configure(state=DISABLED)
        self.setAv_Bt.configure(state=DISABLED)
        self.setAO_Bt.configure(state=DISABLED)
        self.setZe_Bt.configure(state=DISABLED)