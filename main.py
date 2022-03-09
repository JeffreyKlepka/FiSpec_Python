import tkinter as tk
from tkinter import DISABLED
from tkinter import NORMAL
import FiSpec_GUI as fsG
import serial.tools.list_ports
import threading
import matplotlib as plt
plt.use ('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib import style
import time

LARGE_FONT=("Verdana, 12")
style.use("ggplot")

root=tk.Tk()
root.configure(background="white")
root.title("FiSens - FiSpec. Coded with Python. Version 0.0.0")
root.geometry("1000x1000")

measIsOn=False # Flag which indicates if measurement is running.
specIsOn=False # Flag which indicates if spectrum is running
internalMode0 = False # Flag which indicates which kind of measurement data will be provided
oldPort=""

xWll = [] # stores wavelength list (x-axis) of the plot
ySpec = [] # stores amplitude liste (y-axis) of the plot

fsG1 = fsG.FiSpec_GUI(root) # creating an object of the FiSpec_GUI class
plotSize = (5, 3)
fig = Figure(plotSize)
fig.tight_layout()
ax = fig.add_subplot(111) # adding the plot to fig
ax.set_title('Spectrum', fontsize=10)
ax.set_facecolor('black')
# ax.set_xlim(left=770, right=910)
# ax.set_ylim(bottom=0, top=10000)
ax.set_xlabel('Wavelength [nm]', fontsize=8)
ax.set_ylabel('Amplitude', fontsize=8)
ax.grid(color='yellow')

canvas = FigureCanvasTkAgg(fig, fsG1.frame_Plot) # creating a canvas object and embedd fig which will contain the spectrum plot
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1) # 
canvas.draw()

fbg_count=4
fbg_wavelength=[8200000, 8300000, 8400000, 8500000]
fbg_halfwidth= 15000
# readBuf=1024
ser=serial.Serial()
# ser.close()

def sendrecv(command):
    try:
        ser.flushInput()
        ser.write(command.encode())
    except:
        print("Failed to send a message!")
        return ""
    try:
        response=ser.read_until("Ende")
        # response_dec=response.decode()
    except:
        print("No response received on COM-Port!")
        return ""

    # response = ""
    return response

def checkCOMs():
    global oldPort, measIsOn, specIsOn
    # thread t_checkCOMs 
    # repeatedly check for available COM-Ports and connections
    # disable Buttons if no connection can be established
    fsG1.checkCOMS()
    if fsG1.portObj.get()!=oldPort:
        try:
            ser.close()
        except:
            pass
        measIsOn=False
        specIsOn=False
        fsG1.toggleMeasMode_Bt.configure(state=DISABLED)
        fsG1.spec_Bt.configure(state=DISABLED, text='Start Spectrum')
        fsG1.meas_Bt.configure(state=DISABLED, text='Start Measurement')
        fsG1.intT_Bt.configure(state=DISABLED)
        fsG1.setCh_Bt.configure(state=DISABLED)
        fsG1.setAv_Bt.configure(state=DISABLED)
        fsG1.setAO_Bt.configure(state=DISABLED)
        fsG1.setZe_Bt.configure(state=DISABLED)
    elif ser.is_open:
        fsG1.toggleMeasMode_Bt.configure(state=NORMAL)
        fsG1.spec_Bt.configure(state=NORMAL)
        fsG1.meas_Bt.configure(state=NORMAL)
        fsG1.intT_Bt.configure(state=NORMAL)
        fsG1.setCh_Bt.configure(state=NORMAL)
        fsG1.setAv_Bt.configure(state=NORMAL)
        fsG1.setAO_Bt.configure(state=NORMAL)
        fsG1.setZe_Bt.configure(state=NORMAL)
    else:
        measIsOn=False
        specIsOn=False
        fsG1.toggleMeasMode_Bt.configure(state=DISABLED)
        fsG1.spec_Bt.configure(state=DISABLED, text='Start Spectrum')
        fsG1.meas_Bt.configure(state=DISABLED, text='Start Measurement')
        fsG1.intT_Bt.configure(state=DISABLED)
        fsG1.setCh_Bt.configure(state=DISABLED)
        fsG1.setAv_Bt.configure(state=DISABLED)
        fsG1.setAO_Bt.configure(state=DISABLED)
        fsG1.setZe_Bt.configure(state=DISABLED)
    oldPort=fsG1.portObj.get()
    root.after(2000, checkCOMs)

def connectCOM():
    # Try to connect to selected COM Port and execute configurations
    global ser
    dev_available=0
    ser.port = fsG1.portObj.get() # Get selection from Optionsmenu
    ser.baudrate = 3000000 # Configure COM-Port
    ser.bytesize = 8
    ser.parity = "N"
    ser.stopbits = 1
    ser.timeout = 0.5
    try:
        ser.open()
    except:
        print("Failed to open COM-Port!")
        return
    if ser.is_open:
        print("Successfully opened COM-Port: " + ser.port)
        dev_dec = sendrecv("?>")
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
        return
    
    # Configure device after establishing a connection - for further information on commands check FiSens FiSpec Programmer's manual
    wlconfig() # "Ke,x,y,z>"
    ledON() # "LED,x>"
    checkWL() # "WLL>"
    integration() # "iz,x>"
    setAveraging() # "m,x>"
    startInternal() # "a>"
    setInternalMode() # "OBB,x>"

fsG1.connect_COM_Bt.configure(command=connectCOM)

def wlconfig():
    # Set peak detection channel details. Use default values first
    # Can be configured by typing user specific wavelength numbers in entry fields
    global fsG1
    fbg_wavelength[0] = fsG1.setwl_1.get()
    fbg_wavelength[1] = fsG1.setwl_2.get()
    fbg_wavelength[2] = fsG1.setwl_3.get()
    fbg_wavelength[3] = fsG1.setwl_4.get()

    for x in range(len(fbg_wavelength)):
        ma1=int(fbg_wavelength[x])-fbg_halfwidth
        ma2=int(fbg_wavelength[x])+fbg_halfwidth
        conf_msg="Ke," + str(x) + "," + str(ma1) + "," + str(ma2) + ">"
        ser.flushInput()
        ser.write(conf_msg.encode())
        print("Device configured: " + conf_msg) 
        time.sleep(0.5)

fsG1.setwl_Bt.configure(command=wlconfig)

def ledON():
    # Switches internal light source (0=off, 1= on)
    try:
        ser.flushInput()
        ser.write("LED,1>".encode())
        print("Turn on internal LED")
    except:
        print("Error: LED")
        return
    time.sleep(0.5)

def checkWL():
    # Get wavelength of pixel list - x-axis of spectrum
    global xWll
    try:   
        wll_data=sendrecv("WLL>")
    except:
        print("Error: WLL>")
        return

    wll_data_len = len(wll_data)
    wll_data_len4=int(wll_data_len/4)
    
    for j in range(wll_data_len4-1):
        try:
            xWll.append((wll_data[4*j] + 256*wll_data[4*j+1] + 65536*wll_data[4*j+2] + 16777216*wll_data[4*j+3])/10000)
        except:
            pass
    
def setInternalMode():
    global internalMode0
    if internalMode0 == False:
        try:
            ser.write("OBB,0>".encode())
            internalMode0 = True
            fsG1.toggleMeasMode_Bt.configure(text="Temperature / Strain")
        except:
            print("Error: Set internal Measurement Mode")
            return
        time.sleep(0.5)
    else:
        try:
            ser.write("OBB,1>".encode())
            internalMode0 = False
            fsG1.toggleMeasMode_Bt.configure(text="Peak / Amplitude")
        except:
            print("Error: Set internal Measurement Mode")
            pass
        time.sleep(0.5)

fsG1.toggleMeasMode_Bt.configure(command=setInternalMode)

def startInternal():
    # Globally start measurement
    try:
        ser.write("a>".encode())
    except:
        print("Error: a> - Globally start measurement")
        return
    time.sleep(0.5)

def integration():
    # Set integration time
    integration_time=fsG1.intT_In.get()
    try:
        intT_Value=int(integration_time)
    except:
        print("Not a number!")
        return
    if type(intT_Value) == int:
        setIt_msg="iz," + str(integration_time) + ">"
        try:
            ser.write(setIt_msg.encode())
        except:
            print("Error: Set integration time")
            pass

fsG1.intT_Bt.configure(command=integration)

def setChannel():
    # Set number of active Channels
    fbg_count=fsG1.setCh_In.get()
    try:
        fbg_count_value=int(fbg_count)
    except:
        print("Not a number!")
        return
    if type(fbg_count_value)==int:
        setCh_msg="KA," + str(fbg_count_value) + ">"
        try:
            ser.write(setCh_msg.encode())
        except:
            print("Error: KA,x> - Set number of active channels")
            pass

fsG1.setCh_Bt.configure(command=setChannel)

def setAveraging():
    #Set averaging
    aver=fsG1.setAv_In.get()
    try:
        aver_value=int(aver)
    except:
        print("Not a number!")
        return
    if type(aver)==int:
        setAv_msg="m," + str(aver_value) + ">"
        try:
            ser.write(setAv_msg.encode())
        except:
            print("Error: Averaging")
            pass

fsG1.setAv_Bt.configure(command=setAveraging)

def setZero():
    # Set actual values as zero values
    setZe_msg="OBN,x>"
    try:
        ser.write(setZe_msg.encode())
    except:
        print("Error: Set Zero Values")
        pass

fsG1.setZe_Bt.configure(command=setZero)

def setAutoOpt():
    # Start auto-optimization of integration time / averages
    # If successful, values in entry fields will be overwritten
    vAO=fsG1.setAO_In.get()
    try:
        vAO_=int(vAO)
    except:
        print("Not a number!")
        return
    if type(vAO_)==int:
        vAO_msg="AO," + str(vAO_) + ">"
        rcv_data=sendrecv(vAO_msg)
    try:
        intT_ao = rcv_data[0]
        aver_ao = rcv_data[1]
        intT_ao_str = str(intT_ao)
        aver_ao_str = str(aver_ao)
        
        print("Integration time optimized" +intT_ao_str)
        print("Average optimized" + aver_ao_str)
    except:
        print("Error: Auto-optimization")
        return
    val_intT_ao = "".join([i for i in intT_ao_str if i.isdigit()])
    val_aver_ao = "".join([i for i in aver_ao_str if i.isdigit()])
    intT_ao_ = int(val_intT_ao)*1000
    print(str(val_intT_ao))
    print(str(val_aver_ao))
    fsG1.intT_In.delete(0, 6)
    fsG1.intT_In.insert(0, str(intT_ao_))
    fsG1.setAv_In.delete(0, 6)
    fsG1.setAv_In.insert(0, val_aver_ao)

fsG1.setAO_Bt.configure(command=setAutoOpt)

def measurement():
    # Requests data from device and displays the numeric values in form of labels - "P>"-Command
    global ser
    fbg_peak=[8200000, 8300000, 8400000, 8500000]
    fbg_ampl=[0, 0, 0, 0]
    while 1:
        if measIsOn == True:
            if ser.is_open:
                rcv_data=sendrecv("P>")
            else:
                print("COM-Port is closed. Try again!")

            if internalMode0 == True:
                # Received data represents Wavelength and Amplitude
                for i in range(fbg_count):
                    try:
                        fbg_peak[i] = (rcv_data[8*i] + 256*rcv_data[8*i+1] + 65536*rcv_data[8*i+2] + 16777216*rcv_data[8*i+3])/10000
                        fbg_ampl[i] = (rcv_data[8*i+4] + 256*rcv_data[8*i+5] + 65536*rcv_data[8*i+6] + 16777216*rcv_data[8*i+7])/10000
                    except:
                        print("Error: Measurement - No Data")
                        pass

                fsG1.label_Peak1.configure(text="Peak 1: " + str(fbg_peak[0]))
                fsG1.label_Peak2.configure(text="Peak 2: " + str(fbg_peak[1]))
                fsG1.label_Peak3.configure(text="Peak 3: " + str(fbg_peak[2]))
                fsG1.label_Peak4.configure(text="Peak 4: " + str(fbg_peak[3]))
                fsG1.label_Ampl1.configure(text="Amplitude 1: " + str(fbg_ampl[0]))
                fsG1.label_Ampl2.configure(text="Amplitude 2: " + str(fbg_ampl[1]))
                fsG1.label_Ampl3.configure(text="Amplitude 3: " + str(fbg_ampl[2]))
                fsG1.label_Ampl4.configure(text="Amplitude 4: " + str(fbg_ampl[3]))
            else:
                # Received data represents Strain and Temperature
                for i in range(fbg_count):
                    try:
                        fbg_peak[i] = (rcv_data[8*i] + 256*rcv_data[8*i+1] + 65536*rcv_data[8*i+2] + 16777216*rcv_data[8*i+3])/10000 #  + 65536*rcv_data[8*i+2] + 16777216*rcv_data[8*i+3]
                        fbg_ampl[i] = (rcv_data[8*i+4] + 256*rcv_data[8*i+5] + 65536*rcv_data[8*i+6] + 16777216*rcv_data[8*i+7])/100 #  + 65536*rcv_data[8*i+6] + 16777216*rcv_data[8*i+7]
                    except:
                        print("Error: No Data")
                        pass
                fsG1.label_Peak1.configure(text="Strain 1: " + str(fbg_peak[0]))
                fsG1.label_Peak2.configure(text="Strain 2: " + str(fbg_peak[1]))
                fsG1.label_Peak3.configure(text="Strain 3: " + str(fbg_peak[2]))
                fsG1.label_Peak4.configure(text="Strain 4: " + str(fbg_peak[3]))
                fsG1.label_Ampl1.configure(text="Temperature 1: " + str(fbg_ampl[0]))
                fsG1.label_Ampl2.configure(text="Temperature 2: " + str(fbg_ampl[1]))
                fsG1.label_Ampl3.configure(text="Temperature 3: " + str(fbg_ampl[2]))
                fsG1.label_Ampl4.configure(text="Temperature 4: " + str(fbg_ampl[3]))
        # createSpectrum()
        time.sleep(1)
    
def ctrlMeas():
    # Toggles Button Start Measurement and sets Variable measIsOn which enables/disables the function
    global measIsOn
    if measIsOn:
        fsG1.meas_Bt.config(text='Start Measurement')
        measIsOn=False
    else:
        fsG1.meas_Bt.config(text='Stop Measurement')
        measIsOn=True
        
fsG1.meas_Bt.configure(command=ctrlMeas)
        
def createSpectrum():
    # Requests data from device and displays it as a spectrum - "s>"-Command
    global fig, ax, canvas, ySpec, xWll
    while 1:
        if specIsOn == True:
            if ser.is_open:
                try:
                    ySpec.clear()
                    spec_data=sendrecv("s>")
                    spec_data_len=len(spec_data)
                    spec_data_len2=int(spec_data_len/2)
                    for i in range(spec_data_len2):
                        try:
                            ySpec.append(spec_data[2*i]+256*spec_data[2*i+1])
                        except:
                            pass
                    fig.clear()
                    ax.clear()
                    ax = fig.add_subplot(111)
                    ax.set_title('Spectrum', fontsize=10)
                    ax.set_facecolor('black')
                    ax.set_xlabel('Wavelength [nm]', fontsize=8)
                    ax.set_ylabel('Amplitude', fontsize=8)
                    ax.grid(color='yellow')
                    try:
                        ax.set_ylim(bottom=0, top=30000)
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
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
                    canvas.draw()    
                except:
                    print("Error: Spectrum Data Request")
                    pass
            else:
                print("COM-Port is closed. Try again!")
        time.sleep(1)
    
def ctrlSpec():
    # Toggles Button Start Specrum and sets Variable specIsOn which enables/disables the function
    global specIsOn
    if specIsOn:
        fsG1.spec_Bt.config(text='Start Spectrum')
        specIsOn=False
    else:
        fsG1.spec_Bt.config(text='Stop Spectrum')
        specIsOn=True

fsG1.spec_Bt.configure(command=ctrlSpec)

# Create 3 threads which will do work simultaneously
t_checkCOMs = threading.Thread(target=checkCOMs).start()
t_measurement = threading.Thread(target=measurement, daemon=True).start()
t_createSpectrum = threading.Thread(target=createSpectrum, daemon=True).start()

root.mainloop()