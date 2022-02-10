# from socket import timeout
import tkinter as tk
from tkinter import *
import FiSpec_GUI as fsG
import serial.tools.list_ports
# import sys
import time
# import numpy
# import codecs
# import os
# from ast import literal_eval

root=tk.Tk()
root.title("FiSens - FiSpec. Coded with Python. Version 0.0.0")
root.geometry("500x500")

fsG1 = fsG.FiSpec_GUI(root)




ports=serial.tools.list_ports.comports()
serialInst = serial.Serial()
portList = []

readBuf=1024
for onePort in ports:
    portList.append(str(onePort)[0:4])
    # print(str(onePort))
portObj = StringVar()
portObj.set(portList[0])
drop_COM = OptionMenu(fsG1.frame_COM_select, portObj, *portList)
drop_COM.grid(column=0, row=0)

ser=serial.Serial(timeout=1)
ser.port = 'COM3'
ser.baudrate = 3000000
ser.bytesize = 8
ser.parity = "N"
ser.stopbits = 1
print(ser)

def connect_COM():
    ser.port = portObj.get()
    print(ser)

connect_COM_Bt = Button(fsG1.frame_COM_select, text="Connect COM-Port", command=connect_COM)
connect_COM_Bt.grid(column=1, row=0)

if len(portList) == 0:
    print("No COM-ports found!")


try:
    ser.open()
except:
    print("Failed to open COM-Port!")
if ser.is_open:
    print("Successfully opened COM-Port: " + ser.port)

dev_check="?>"
try:
    # print(dev_check.encode())
    ser.write(dev_check.encode())

except:
    print("Failed to send a message!")
# time.sleep(5)
try:
    rcv_msg=ser.readline(15)
    rcv_dec=rcv_msg.decode()
except:
    print("No response received on COM-Port!")

dev_available=0
if rcv_dec == "FiSpec FBG X100":
    dev_available=1
elif rcv_dec == "FiSpec FBG X150":
    dev_available=1
else:
    dev_available=0
print("Connected to: " + rcv_dec)

fbg_count=4
fbg_wavelength=[8200000, 8300000, 8400000, 8500000]
fbg_halfwidth= 15000
'''
for x in range(len(fbg_wavelength)):
    ma1=fbg_wavelength[x]-fbg_halfwidth
    ma2=fbg_wavelength[x]+fbg_halfwidth
    conf_msg="Ke," + str(x) + "," + str(ma1) + "," + str(ma2) + ">"
    conf_enc=conf_msg.encode()
    try:
        ser.write(conf_enc)
    except:
        print("fail...")
    time.sleep(2)  


setCh_msg="KA," + str(fbg_count) + ">"
setCh_enc=setCh_msg.encode()#
try:
    ser.write(setCh_enc)
except:
        print("fail2...")

time.sleep(2) 
integration_time=50000
setIt_msg="iz," + str(integration_time) + ">"
setIt_enc=setCh_msg.encode()
try:
    ser.write(setIt_enc)
except:
        print("fail3...")

try:
    ser.write("LED,1".encode())
except:
        print("fail4...")

try:
    ser.write("a>".encode())
except:
        print("fail4...")
'''
time.sleep(2)  
fbg_peak=[8200000, 8300000, 8400000, 8500000]
fbg_ampl=[0, 0, 0, 0]

if ser.is_open:
    try:
        ser.write("P>".encode())
        print("Sende P-Befehl")
    except:
        print("Fail 4 ...")
else:
    print("COM-Port is closed. Try again!")


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
        print("Missing data ...")
# time.sleep(10)
# data_enc=codecs.getencoder(rcv_data_dec)
# print(data_enc)


root.mainloop()
