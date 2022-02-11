# from socket import timeout
import tkinter as tk
from tkinter import *
import FiSpec_GUI as fsG
import serial.tools.list_ports
import threading
# import sys
import time
# import numpy
# import codecs
# import os
# from ast import literal_eval

root=tk.Tk()
root.title("FiSens - FiSpec. Coded with Python. Version 0.0.0")
root.geometry("1000x1000")

fsG1 = fsG.FiSpec_GUI(root)

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
connect_COM_Bt.place(x=150, y=2, width=80)

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
            print("Sende P-Befehl")
        except:
            print("Error: Measurement Request")
    else:
        print("COM-Port is closed. Try again!")
        return
    # Decode and process data

    rcv_data=ser.read_until('Ende')
    rcv_data_dec=str(rcv_data)
    meas_val=rcv_data_dec.split('\\x') #separate HEX-Values in String
    for v in range(len(meas_val)):
        x = meas_val[v].strip("'\\n\\r") #remove unwanted symbols
        meas_val[v]=x
        y = meas_val[v][0:2] #only store HEX-Value and ignore other characters
        meas_val[v]=y
        if v > 0:
            z = int(meas_val[v], 16) #convert HEX to DEC
            meas_val[v]=z
    del meas_val[0] #remove "b'" (first list-item)

    print(rcv_data)
    print(meas_val)

    for i in range(fbg_count):
        try:
            fbg_peak[i] = meas_val[8*i] + 256*meas_val[8*i+1] + 65536*meas_val[8*i+2] + 16777216*meas_val[8*i+3]
            fbg_ampl[i] = meas_val[8*i+4] + 256*meas_val[8*i+5] + 65536*meas_val[8*i+6] + 16777216*meas_val[8*i+7]
            print("Messwerte " + str(i+1) + ": " + str(fbg_peak[i]) + ", " + str(fbg_ampl[i]))
        except:
            print("Error: Data incomplete")
    root.after(10000, measurement)

meas_Bt = Button(fsG1.frame_Measurements, text="Start Measurement", command=measurement)
meas_Bt.pack()
t_COM_Controller = threading.Thread(target=checkCOMs).start()
t_Meas_Controller = threading.Thread(target=measurement)
root.mainloop()
