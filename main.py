# from socket import timeout
import tkinter as tk
from tkinter import *
from turtle import color
import FiSpec_GUI as fsG
import serial.tools.list_ports
import threading
import matplotlib as plt
plt.use ('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

# import sys
import time
import numpy as np
# import codecs
# import os
# from ast import literal_eval

root=tk.Tk()
root.title("FiSens - FiSpec. Coded with Python. Version 0.0.0")
root.geometry("1000x1000")

measIsOn=False
specIsOn=False

xWL = []
xLWL = []

yAmpl = []

fsG1 = fsG.FiSpec_GUI(root)
plotSize = (4, 3)
fig = Figure(plotSize)
canvas = FigureCanvasTkAgg(fig, fsG1.frame_Plot)
toolbar = NavigationToolbar2Tk(canvas, fsG1.frame_Plot)
toolbar.pack(fill=tk.BOTH, expand=1)
toolbar.update()

fbg_count=4
fbg_wavelength=[8200000, 8300000, 8400000, 8500000]
fbg_halfwidth= 15000

readBuf=1024

ser=serial.Serial(timeout=1)

portObj = StringVar()
portList = []
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

connect_COM_Bt = Button(fsG1.frame_COM_select, text="Connect Port", command=connectCOM)
connect_COM_Bt.place(x=150, y=2, width=120)

def configuration():
    for x in range(len(fbg_wavelength)):
        ma1=fbg_wavelength[x]-fbg_halfwidth
        ma2=fbg_wavelength[x]+fbg_halfwidth
        conf_msg="Ke," + str(x) + "," + str(ma1) + "," + str(ma2) + ">"
        conf_enc=conf_msg.encode()
        try:
            ser.write(conf_enc)
        except:
            print("Error: Configuration")

def setChannel():
    setCh_msg="KA," + str(fbg_count) + ">"
    setCh_enc=setCh_msg.encode()
    try:
        ser.write(setCh_enc)
    except:
        print("Error: Channel")

def ledON():
    try:
        ser.write("LED,1".encode())
    except:
        print("Error: LED")

def startInternal():
    try:
        ser.write("a>".encode())
    except:
        print("Error: Start internal Measurement")

def integration():
    integration_time=50000
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

    if ser.is_open:
        try:
            ser.write("P>".encode())
            print("Send P>")
        except:
            print("Error: Measurement Request")
    else:
        print("COM-Port is closed. Try again!")
        return
    # Decode and process data

    rcv_data=ser.read_until('Ende')
    # rcv_data_dec=str(rcv_data)
    # meas_val=rcv_data_dec.split('\\x') #separate HEX-Values in String
    '''
    for v in range(0, rcv_data)):
        # x = meas_val[v].strip("'\\n\\r") #remove unwanted symbols
        # meas_val[v]=x
        # y = meas_val[v][0:2] #only store HEX-Value and ignore other characters
        # meas_val[v]=y
        if v > 0:
            z = int(meas_val[v], 16) #convert HEX to DEC
            meas_val[v]=z
    del meas_val[0] #remove "b'" (first list-item)
    '''
    print(rcv_data)
    # print(meas_val)

    for i in range(fbg_count):
        try:
            fbg_peak[i] = rcv_data[8*i] + 256*rcv_data[8*i+1] + 65536*rcv_data[8*i+2] + 16777216*rcv_data[8*i+3]
            fbg_ampl[i] = rcv_data[8*i+4] + 256*rcv_data[8*i+5] + 65536*rcv_data[8*i+6] + 16777216*rcv_data[8*i+7]
            print("Messwerte " + str(i+1) + ": " + str(fbg_peak[i]) + ", " + str(fbg_ampl[i]))
        except:
            print("Error: Data incomplete")
    root.after(10000, measurement)

meas_Bt = Button(fsG1.frame_start_meas, text="Start Measurement", command=measurement)
meas_Bt.place(x=150, y=0, width=120)

def createSpectrum():
    global fig, ax, xWL, yAmpl, specIsOn

    if specIsOn==False:
        return
    
    xLWL.clear() # Delete old lists and canvas
    yAmpl.clear()
    fig.clear()
    canvas.get_tk_widget().forget()
    # Send 's>'-command
    if ser.is_open:
        try:
            ser.write("s>".encode())
            print("Send s>")
        except:
            print("Error: Spectrum Request")
    else:
        print("COM-Port is closed. Try again!")
        return
    
    spec_data=ser.read_until('Ende') # Read incoming data
    spec_data_len = len(spec_data)
    
    xWL = np.arange(780, 900, 120/spec_data_len) # x-list has to have the same length as y-list
    for wl in xWL:
        xLWL.append(wl)
    
    for ampl in spec_data:
        yAmpl.append(spec_data[ampl]) # Save incoming array as a list
    fig.tight_layout()
    ax = fig.add_subplot() # Configure and create plot
    ax.plot(xWL, yAmpl, c='green')
    ax.set_title('Spectrum', fontsize=10)
    ax.set_facecolor('black')
    # ax.set_xticks(np.arange(780, 900, step=20))
    ax.set_xlabel('Wavelength [nm]', fontsize=8)
    ax.set_ylabel('Amplitude', fontsize=8)
    ax.grid(color='yellow')
    
    
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1) # display plot as a widget of tkinter
    canvas.draw()
    
    root.after(2000, createSpectrum)

def ctrlSpec():
    global specIsOn

    if specIsOn:
        spec_Bt.config(text='Start Spectrum')
        specIsOn=False
    else:
        spec_Bt.config(text='Stop Spectrum')
        specIsOn=True
        createSpectrum()

spec_Bt = Button(fsG1.frame_start_spec, text="Start Spectrum", command=ctrlSpec)
spec_Bt.place(x=150, y=0, width=120)   

t_Controller = threading.Thread(target=checkCOMs).start()
t_Meas_Controller = threading.Thread(target=measurement)
t_Spec_Controller = threading.Thread(target=createSpectrum).start()
root.mainloop()
