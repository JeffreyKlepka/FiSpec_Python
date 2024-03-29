# FiSens FiSpec - main
# Version 0.3 
# November, 2022
from tkinter import BOTH
import FiSpec_GUI as fsG
import serial.tools.list_ports
import threading
import matplotlib as plt
plt.use ('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib import style
import time

style.use("ggplot")

measIsOn=False # Flag which indicates if measurement is running.
specIsOn=False # Flag which indicates if spectrum is running.
pausedSpec=False # Flag which indicates if the spectrum is paused. While configuring the Spectrum should not run.
internalMode0 = False # Flag which indicates which kind of measurement data will be provided
oldPort=""
xWll = [] # stores wavelength list (x-axis) of the plot
ySpec = [] # stores amplitude liste (y-axis) of the plot

fbg_count=4
fbg_wavelength=[8200000, 8300000, 8400000, 8500000]
fbg_halfwidth= 15000
bufferSize = 4096

def buildSpectrum():
    global fig, ax, canvas
    plotSize = (5, 3)
    fig = Figure(plotSize) # creating a figure which will contain the spectrum
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
    # canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1) # 
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)
    canvas.draw()

def sendrecv(command):
    try:
        ser.flushInput()
        ser.write(command.encode())
    except:
        print("Failed to send a message!")
        return ""
    try:
        response=ser.read(size=bufferSize)
    except:
        print("No response received on COM-Port!")
        return ""
    
    return response

def checkCOMs():
    global oldPort, measIsOn, specIsOn
    # check for available COM-Ports
    fsG1.checkCOMs()
    if fsG1.portObj.get()!=oldPort:
        try:
            ser.close()
        except:
            pass
        measIsOn=False
        specIsOn=False
        fsG1.disableButtons()
    elif ser.is_open:
        fsG1.enableButtons()       
    else:
        measIsOn=False
        specIsOn=False
        fsG1.disableButtons()
    oldPort=fsG1.portObj.get()

def connectCOM():
    # Try to connect to selected COM Port and execute configurations
    global ser, oldPort
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
        print("Successfully connected to device on COM-Port: " + ser.port)
        dev_dec = sendrecv("?>")
        fsG1.enableButtons()
    try:
        print(dev_dec)
        if dev_dec == "FiSpec FBGX100":
            dev_available=1
            print("Connected to device: " + dev_dec)
            
        elif dev_dec == "FiSpec FBGX150":
            dev_available=1
            print("Connected to device: " + dev_dec)

        elif dev_dec == "FiSpec FBGX152":
            dev_available=1
            print("Connected to device: " + dev_dec)
        else:
            dev_available=0
            print("Error: No FiSens-device found!")
            # fsG1.disableButtons()
            # ser.close()
            # return
    except:
        dev_available=0
        print("Error: No device found!")
        return
    
    # Configure device after establishing a connection 
    # For further information on commands check FiSens FiSpec Programmer's manual
    wlconfig() # "Ke,x,y,z>"
    ledON() # "LED,x>"
    checkWL() # "WLL>"
    integration() # "iz,x>"
    setAveraging() # "m,x>"
    startInternal() # "a>"
    setInternalMode() # "OBB,x>"

def wlconfig():
    # Set peak detection channel details. Use default values first
    # Can be configured by typing user specific wavelength numbers in entry fields
    global fsG1, specIsOn, pausedSpec
    
    if specIsOn == True: # while configuring the device, the spectrum should not be running
        specIsOn == False # pause the spectrum ...
        pausedSpec=True 

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

    if pausedSpec == True:
        specIsOn == True # ... restart the spectrum
        pausedSpec=False # pause ends here

def ledON():
    # Switches internal light source (0=off, 1= on)
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True
    try:
        ser.flushInput()
        ser.write("LED,1>".encode())
        print("Turn on internal LED")
    except:
        print("Error: LED")
        return
    time.sleep(0.5)

    if pausedSpec == True:
        specIsOn == True 
        pausedSpec=False

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
    global internalMode0, specIsOn, pausedSpec

    if specIsOn == True:
        specIsOn == False
        pausedSpec=True
    
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
    
    if pausedSpec == True:
        specIsOn == True
        pausedSpec=False

def startInternal():
    # Globally start measurement
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True
    
    try:
        ser.write("a>".encode())
    except:
        print("Error: a> - Globally start measurement")
        return
    time.sleep(0.5)

    if pausedSpec == True:
        specIsOn == True # then start it again
        pausedSpec=False

def integration():
    # Set integration time
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True

    integration_time=fsG1.intT_In.get()
    try:
        intT_Value=int(integration_time)
    except:
        print("Error: Not a number!")
        return
    if type(intT_Value) == int:
        setIt_msg="iz," + str(integration_time) + ">"
        try:
            ser.write(setIt_msg.encode())
        except:
            print("Error: Set integration time")
            pass
    
    if pausedSpec == True:
        specIsOn == True # then start it again
        pausedSpec=False

def setChannel():
    # Set number of active Channels
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True

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
    
    if pausedSpec == True:
        specIsOn == True # then start it again
        pausedSpec=False

def setAveraging():
    #Set averaging
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True
    
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

    if pausedSpec == True:
        specIsOn == True # then start it again
        pausedSpec=False

def setZero():
    # Set actual values as zero values
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True
    
    setZe_msg="OBN,x>"
    try:
        ser.write(setZe_msg.encode())
    except:
        print("Error: Set Zero Values")
        pass

    if pausedSpec == True:
        specIsOn == True # then start it again
        pausedSpec=False

def setAutoOpt():
    # Start auto-optimization of integration time / averages
    # If successful, values in entry fields will be overwritten
    global specIsOn, pausedSpec
    if specIsOn == True:
        specIsOn == False
        pausedSpec=True
    
    vAO=fsG1.setAO_In.get()
    try:
        vAO_=int(vAO)
    except:
        print("Error: Not a number!")
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

    if pausedSpec == True:
        specIsOn == True # then start it again
        pausedSpec=False

def measurement():
    # Requests data from device and displays the numeric values in form of labels - "P>"-Command
    global ser
    fbg_peak=[8200000, 8300000, 8400000, 8500000]
    fbg_ampl=[0, 0, 0, 0]
    fbg_strain=[-5000000, -50, -50, -50]
    fbg_temp=[-5000000, -50, -50, -50]
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
                        strain_4bytes=[rcv_data[8*i], rcv_data[8*i+1], rcv_data[8*i+2], rcv_data[8*i+3]]
                        fbg_strain[i]=int.from_bytes(strain_4bytes, byteorder="little", signed=True) / 10000 
                        temp_4bytes=[rcv_data[8*i+4], rcv_data[8*i+5], rcv_data[8*i+6], rcv_data[8*i+7]] 
                        fbg_temp[i] = int.from_bytes(temp_4bytes, byteorder="little", signed=True) / 100
                    except:
                        print("Error: No Data")
                        pass
                fsG1.label_Peak1.configure(text="Strain 1: " + str(fbg_strain[0]))
                fsG1.label_Peak2.configure(text="Strain 2: " + str(fbg_strain[1]))
                fsG1.label_Peak3.configure(text="Strain 3: " + str(fbg_strain[2]))
                fsG1.label_Peak4.configure(text="Strain 4: " + str(fbg_strain[3]))
                fsG1.label_Ampl1.configure(text="Temperature 1: " + str(fbg_temp[0]))
                fsG1.label_Ampl2.configure(text="Temperature 2: " + str(fbg_temp[1]))
                fsG1.label_Ampl3.configure(text="Temperature 3: " + str(fbg_temp[2]))
                fsG1.label_Ampl4.configure(text="Temperature 4: " + str(fbg_temp[3]))
                
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
              
def updateSpectrum():
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
                                ySpec.append(0)
                            ax.plot(xWll, ySpec, c='green')
                        elif len(xWll) < len(ySpec):
                            while(len(xWll) < len(ySpec)):
                                ySpec.pop()
                            ax.plot(xWll, ySpec, c='green')
                        else:
                            ax.plot(xWll, ySpec, c='green')    
                    except:
                        pass
                    canvas.get_tk_widget().pack(fill=BOTH, expand=1)
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

def assignButtons():
    fsG1.refreshCOM_Bt.configure(command=checkCOMs) # assign the function to the button
    fsG1.connect_COM_Bt.configure(command=connectCOM)
    fsG1.setwl_Bt.configure(command=wlconfig)
    fsG1.toggleMeasMode_Bt.configure(command=setInternalMode)
    fsG1.intT_Bt.configure(command=integration)
    fsG1.setCh_Bt.configure(command=setChannel)
    fsG1.setAv_Bt.configure(command=setAveraging)
    fsG1.setZe_Bt.configure(command=setZero)
    fsG1.setAO_Bt.configure(command=setAutoOpt)
    fsG1.meas_Bt.configure(command=ctrlMeas)
    fsG1.spec_Bt.configure(command=ctrlSpec)

if __name__ == '__main__':
    ser=serial.Serial(timeout=30)
    fsG1 = fsG.FiSpec_GUI() # creating an object of the FiSpec_GUI class
    assignButtons()
    fsG1.disableButtons() # Disable buttons on first launch
    buildSpectrum() # prepare Spectrum
    checkCOMs() # checking for available COM-Ports
    # Create 2 threads which will do work simultaneously
    t_measurement = threading.Thread(target=measurement, daemon=True)
    t_measurement.start()
    t_createSpectrum = threading.Thread(target=updateSpectrum, daemon=True)
    t_createSpectrum.start()    
    fsG1.master.mainloop()