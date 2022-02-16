
import tkinter as tk
from tkinter import *
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
# import sys
import time
import numpy as np

LARGE_FONT=("Verdana, 12")
style.use("ggplot")

# import codecs
# import os

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

ser=serial.Serial(timeout=2)

portObj = StringVar()
portList = []
ports=serial.tools.list_ports.comports()
serialInst = serial.Serial()
    
for onePort in ports:
    portList.append(str(onePort)[0:4])
try:
    portObj.set(portList[0])
except:
    # if len(portList) == 0:
    portList.append("No devices found!")
    portObj.set(portList[0])
    print("No devices found!")
drop_COM = OptionMenu(fsG1.frame_COM_select, portObj, *portList)
drop_COM.grid(row=0, column=0)

def checkCOMs():
    global portObj, portList, drop_COM
    
    drop_COM.destroy()
    portList.clear()
    ports=serial.tools.list_ports.comports()
    serialInst = serial.Serial()
    
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
    drop_COM = OptionMenu(fsG1.frame_COM_select, portObj, *portList)
    drop_COM.grid(row=0, column=0)
    root.after(2000, checkCOMs)

def connectCOM():
    global ser
    
    ser.port = portObj.get()
    ser.baudrate = 3000000
    ser.bytesize = 8
    ser.parity = "N"
    ser.stopbits = 1
    # ser.timeout = None
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
    
    ledON()
    checkWL()

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

    # print(xWll)
connect_COM_Bt = Button(fsG1.frame_COM_select, text="Connect Port", command=connectCOM)
connect_COM_Bt.place(x=150, y=2, width=120)

def configuration():
    for x in range(len(fbg_wavelength)):
        ma1=fbg_wavelength[x]-fbg_halfwidth
        ma2=fbg_wavelength[x]+fbg_halfwidth
        conf_msg="Ke," + str(x) + "," + str(ma1) + "," + str(ma2) + ">"
        try:
            ser.write(conf_msg.encode())
        except:
            print("Error: Configuration")
        print(conf_msg)

conf_Bt = Button(fsG1.frame_config, text="Configure", command=configuration)
conf_Bt.place(x=150, y=2, width=120)

def setChannel():
    setCh_msg="KA," + str(fbg_count) + ">"
    setCh_enc=setCh_msg.encode()
    try:
        ser.write(setCh_enc)
    except:
        print("Error: Channel")

def ledON():
    try:
        ser.flushInput()
        ser.write("LED,1>".encode())
    except:
        print("Error: LED")
    time.sleep(2)

def startInternal():
    try:
        ser.write("a>".encode())
    except:
        print("Error: Start internal Measurement")

def integration():
    integration_time=50000 #Eingabefeld, mit Button übernehmen
    setIt_msg="iz," + str(integration_time) + ">"
    setIt_enc=setIt_msg.encode()
    try:
        ser.write(setIt_enc)
    except:
        print("Error: Integration time")

def measurement():
    global ser
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
            print("Error: Data incomplete")

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
        meas_Bt.config(text='Start Measurement')
        measIsOn=False
    else:
        meas_Bt.config(text='Stop Measurement')
        measIsOn=True
        measurement()

meas_Bt = Button(fsG1.frame_start_meas, text="Start Measurement", command=ctrlMeas)
meas_Bt.place(x=150, y=0, width=120)

def getSpecData():
    global ySpec, specIsOn, ser
    if specIsOn==False:
        return
    ySpec.clear() #Delete old y-List
        # Send 's>'-command
    if ser.is_open:
        ser.flushInput()
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
    root.after(1000, getSpecData)

def createSpectrum(interval):
    global fig, ax, ySpec, specIsOn, xWll

    try:
        ax.clear()
        ax.set_ylim(bottom=0, top=10000)
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
        spec_Bt.config(text='Start Spectrum')
        specIsOn=False
    else:
        spec_Bt.config(text='Stop Spectrum')
        specIsOn=True
        # createSpectrum()
        getSpecData()

spec_Bt = Button(fsG1.frame_start_spec, text="Start Spectrum", command=ctrlSpec)
spec_Bt.place(x=150, y=0, width=120)   

t_Controller = threading.Thread(target=checkCOMs).start()
t_Meas_Controller = threading.Thread(target=measurement).start()
t_Spec_Controller = threading.Thread(target=getSpecData).start()
t_Spec_Plot = threading.Thread(target=createSpectrum)

ani = animation.FuncAnimation(fig, createSpectrum, interval=2000)
root.mainloop()
