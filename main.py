
import tkinter as tk
from tkinter import Button
# from tkinter import Label
from tkinter import Entry
from tkinter import OptionMenu
from tkinter import StringVar
# from turtle import color
import FiSpec_GUI as fsG
import serial.tools.list_ports
import threading
import matplotlib as plt
plt.use ('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from functools import partial
import time
import numpy as np

LARGE_FONT=("Verdana, 12")
style.use("ggplot")


root=tk.Tk()
root.title("FiSens - FiSpec. Coded with Python. Version 0.0.0")
root.geometry("1000x1000")

measIsOn=False
specIsOn=False

xWll = []
ySpec = []
xLWL = []

fsG1 = fsG.FiSpec_GUI(root)
plotSize = (4, 3)
fig = Figure(plotSize)
fig.tight_layout()
ax = fig.add_subplot(111)
ax.set_title('Spectrum', fontsize=10)
ax.set_facecolor('black')
# ax.set_xlim(left=770, right=910)
ax.set_ylim(bottom=0, top=10000)
ax.set_xlabel('Wavelength [nm]', fontsize=8)
ax.set_ylabel('Amplitude', fontsize=8)
ax.grid(color='yellow')

canvas = FigureCanvasTkAgg(fig, fsG1.frame_Plot)
# canvas.show()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1) # display plot as a widget of tkinter
canvas.draw()
# toolbar = NavigationToolbar2Tk(canvas, fsG1.frame_Plot)
# toolbar.update()
# toolbar.pack(fill=tk.BOTH, expand=True)

fbg_count=4
fbg_wavelength=[8200000, 8300000, 8400000, 8500000]
fbg_halfwidth= 15000

readBuf=1024

ser=serial.Serial()

# portObj = StringVar()
'''
portList = []
ports=serial.tools.list_ports.comports()
    
for onePort in ports:
    portList.append(str(onePort)[0:4])
try:
    fsG1.portObj.set(portList[0])
except:
    # if len(portList) == 0:
    portList.append("No devices found!")
    fsG1.portObj.set(portList[0])
    print("No devices found!")

fsG1.drop_COM.configure(fsG1.portObj, *portList)

def checkCOMs():
    global portObj, portList, drop_COM
    
    # fsG1.drop_COM.destroy()
    portList.clear()
    ports=serial.tools.list_ports.comports()
    # serialInst = serial.Serial()
    
    for onePort in ports:
        portList.append(str(onePort)[0:4])
        # print(str(onePort))
    
    try:
        portObj.set(portList[0])
    except:
        # if len(portList) == 0:
        portList.append("No devices found!")
        portObj.set(portList[0])
        print("No devices found!")
    fsG1.drop_COM.configure(fsG1.portObj, *portList)
    
    root.after(2000, checkCOMs)
'''
def checkCOMs():
    fsG1.checkCOMS()
    root.after(2000, checkCOMs)

def connectCOM():
    global ser
    
    ser.port = fsG1.portObj.get()
    ser.baudrate = 3000000
    ser.bytesize = 8
    ser.parity = "N"
    ser.stopbits = 1
    ser.timeout = 0.25
    # ser.xonxoff = True
    try:
        ser.open()
    except:
        print("Failed to open COM-Port!")
    if ser.is_open:
        print("Successfully opened COM-Port: " + ser.port)
        
        try:
            ser.write("?>".encode())
        except:
            print("Failed to send a message!")
            print(ser)
    try:
        dev=ser.readline(15)
        dev_dec=dev.decode()
    except:
        print("No response received on COM-Port!")

    dev_available=0
    try:
        if dev_dec == "FiSpec FBG X100":
            dev_available=1
            print("Connected to device: " + dev_dec)
            
        elif dev_dec == "FiSpec FBG X150":
            dev_available=1
            print("Connected to device: " + dev_dec)
        else:
            dev_available=0
    except:
        dev_available=0
        print("Error: No device found!")
    configuration()
    ledON()
    checkWL()

fsG1.connect_COM_Bt.configure(command=connectCOM)

def configuration():
    for x in range(len(fbg_wavelength)):
        ma1=fbg_wavelength[x]-fbg_halfwidth
        ma2=fbg_wavelength[x]+fbg_halfwidth
        conf_msg="Ke," + str(x) + "," + str(ma1) + "," + str(ma2) + ">"
        try:
            ser.write(conf_msg.encode())
        except:
            print("Error: Configuration")
        print("Device configured: " + conf_msg)
        time.sleep(0.5)

def ledON():
    try:
        ser.write("LED,1>".encode())
        print("Turn on internal LED")
    except:
        print("Error: LED")
    time.sleep(0.5)

def checkWL():
    global xWll
    try:
        ser.flushInput()
        ser.write("WLL>".encode())
    except:
        print("Error: WLL>")
    
    wll_data=ser.read_until('Ende')
    wll_data_len = len(wll_data)
    wll_data_len4=int(wll_data_len/4)
    
    for j in range(wll_data_len4-1):
        try:
            xWll.append((wll_data[4*j] + 256*wll_data[4*j+1] + 65536*wll_data[4*j+2] + 16777216*wll_data[4*j+3])/10000)
        except:
            pass
    
def startInternal():
    try:
        ser.write("a>".encode())
    except:
        print("Error: Start internal Measurement")
    time.sleep(0.5)

def integration():
    integration_time=fsG1.intT_In.get() #Eingabefeld, mit Button übernehmen
    try:
        intT_Value=int(integration_time)
    except:
        print("Not a number!")
        return
    if type(intT_Value) == int:

        setIt_msg="iz," + str(integration_time) + ">"
        setIt_enc=setIt_msg.encode()
        try:
            ser.write(setIt_enc)
        except:
            print("Error: Integration time")

fsG1.intT_Bt.configure(command=integration)

def setChannel():
    # Set number of active Channels
    fbg_count=fsG1.setCh_In.get()
    try:
        fbg_count_value=int(fbg_count)
    except:
        print("Not a number!")
    if type(fbg_count_value)==int:
    
        setCh_msg="KA," + str(fbg_count_value) + ">"
        setCh_enc=setCh_msg.encode()
        try:
            ser.write(setCh_enc)
        except:
            print("Error: Channel")

fsG1.setCh_Bt.configure(command=setChannel)

def setAveraging():

    aver=fsG1.setAv_In.get()
    try:
        aver_value=int(aver)
    except:
        print("Not a number!")
    if type(aver)==int:
    
        setAv_msg="m," + str(aver_value) + ">"
        setAv_enc=setAv_msg.encode()
        try:
            ser.write(setAv_enc)
        except:
            print("Error: Averaging")

fsG1.setAv_Bt.configure(command=setAveraging)

def setZero():
    zVal=fsG1.setZe_In.get()
    try:
        zVal_=int(zVal)
    except:
        print("Not a number!")
    if type(zVal_)==int:
    
        setZe_msg="OBN," + str(zVal_) + ">"
        setZe_enc=setZe_msg.encode()
        try:
            ser.write(setZe_enc)
        except:
            print("Error: Set Zero Values")

fsG1.setZe_Bt.configure(command=setZero)

def setAutoOpt():
    vAO=fsG1.setZe_In.get()
    try:
        vAO_=int(vAO)
    except:
        print("Not a number!")
    if type(vAO_)==int:
    
        vAO_msg="OBN," + str(vAO_) + ">"
        vAO_enc=vAO_msg.encode()
        try:
            ser.write(vAO_enc)
        except:
            print("Error: Set Zero Values")

fsG1.setAO_Bt.configure(command=setAutoOpt)

def measurement():
    global ser, t_Spec_Controller, t_Spec_Plot
    fbg_peak=[8200000, 8300000, 8400000, 8500000]
    fbg_ampl=[0, 0, 0, 0]
    
    if measIsOn == False:
        return

    if ser.is_open:
        ser.flushInput()
        try:
            ser.write("P>".encode())
            print("Send P>")
        except:
            print("Error: Measurement Request")
    else:
        print("COM-Port is closed. Try again!")
        return
    
    rcv_data=ser.read_until('Ende')

    for i in range(fbg_count):
        try:
            fbg_peak[i] = (rcv_data[8*i] + 256*rcv_data[8*i+1] + 65536*rcv_data[8*i+2] + 16777216*rcv_data[8*i+3])/10000
            fbg_ampl[i] = (rcv_data[8*i+4] + 256*rcv_data[8*i+5] + 65536*rcv_data[8*i+6] + 16777216*rcv_data[8*i+7])/10000
            print("Messwerte " + str(i+1) + ": " + str(fbg_peak[i]) + ", " + str(fbg_ampl[i]))
        except:
            print("Error: No Data")

    fsG1.label_Peak1.configure(text="Peak 1: " + str(fbg_peak[0]))
    fsG1.label_Peak2.configure(text="Peak 2: " + str(fbg_peak[1]))
    fsG1.label_Peak3.configure(text="Peak 3: " + str(fbg_peak[2]))
    fsG1.label_Peak4.configure(text="Peak 4: " + str(fbg_peak[3]))
    fsG1.label_Ampl1.configure(text="Amplitude 1: " + str(fbg_ampl[0]))
    fsG1.label_Ampl2.configure(text="Amplitude 2: " + str(fbg_ampl[1]))
    fsG1.label_Ampl3.configure(text="Amplitude 3: " + str(fbg_ampl[2]))
    fsG1.label_Ampl4.configure(text="Amplitude 4: " + str(fbg_ampl[3]))
    root.after(10000, measurement)

def ctrlMeas():
    global specIsOn, measIsOn

    if measIsOn:
        fsG1.meas_Bt.config(text='Start Measurement')
        measIsOn=False
    else:
        fsG1.meas_Bt.config(text='Stop Measurement')
        measIsOn=True
        measurement()

fsG1.meas_Bt.configure(command=ctrlMeas)

def getSpecData():
    global ySpec, specIsOn, ser
    
    ySpec.clear() #Delete old y-List
    # Send 's>'-command
    if specIsOn==False:
            return
    elif ser.is_open:
        try:
            ser.write("s>".encode())
        except:
            print("Error: Spectrum Data Request")
    else:
        print("COM-Port is closed. Try again!")
        return
    
    spec_data=ser.read_until('Ende') # Read incoming data
    spec_data_len=len(spec_data)
    spec_data_len2=int(spec_data_len/2)
    
    for i in range(spec_data_len2):
        try:
            ySpec.append(spec_data[2*i]+256*spec_data[2*i+1])
        except:
            pass
        
def createSpectrum(interval):
    global fig, ax, specIsOn, ySpec, xWll

    if specIsOn==False:
        return
    elif specIsOn == True:
        
        getSpecData()
        ax.clear()
        try:
            ax.set_ylim(bottom=0, top=10000)
            # if len(xWll) < 2000:
            #     checkWL()
            if len(xWll) > len(ySpec):
                # y and x List have to have same dimension
                while(len(xWll) > len(ySpec)):
                    xWll.pop()
                ax.plot(xWll, ySpec, c='green')
            elif len(xWll) < len(ySpec):
                while(len(xWll) < len(ySpec)):
                    ySpec.pop()
                ax.plot(xWll, ySpec, c='green')
            else:
                ax.plot(xWll, ySpec, c='green')
        except:
            pass
    
def ctrlSpec():
    global specIsOn

    if specIsOn:
        fsG1.spec_Bt.config(text='Start Spectrum')
        specIsOn=False
    else:
        fsG1.spec_Bt.config(text='Stop Spectrum')
        specIsOn=True

fsG1.spec_Bt.configure(command=ctrlSpec)
  
t_Controller = threading.Thread(target=checkCOMs).start()
t_Meas_Controller = threading.Thread(target=measurement)
t_Spec_Controller = threading.Thread(target=getSpecData)
# t_Spec_Controller.daemon = True
t_Spec_Plot = threading.Thread(target=createSpectrum)

ani = animation.FuncAnimation(fig, createSpectrum, interval=1000)
root.mainloop()
