from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
import tkinter as tk
from PIL import Image
import RPi.GPIO as GPIO
from time import sleep
from tkinter import HORIZONTAL
from tkinter import IntVar
from tkinter import W
from tkinter import N
from tkinter import CENTER
from tkinter import LEFT
from tkinter import PhotoImage
from tkinter import LabelFrame
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import busio
import digitalio
import board
from time import strftime
import threading
import serial
import os
from signal import signal, SIGINT
import subprocess
from tkinter import messagebox as mbox
import socket
import logging
import glob
#import adafruit_python_mcp300 as MCP
#from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
#spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# create the cs (chip select)
#cs = digitalio.DigitalInOut(board.D5)
# create the mcp object
#mcp = MCP.MCP3008(spi, cs)
# create an analog input channel on pin 0
#chan = AnalogIn(mcp, MCP.P0)
#chan1 = AnalogIn(mcp, MCP.P1)
MIVLL=2
MIVLH=6
BPM=12
PIPL=40
PEEPL=5
PIPPEEPDif=20
ALARMONOFF=1
val1=0
val2=0
val3=0

GPIO21 = 21
GPIO20 = 20
screen_shot_cmd = 'scrot &'
screen_record_cmd = 'recordmydesktop myCapture.ogv --no-sound &'

check_screen_record = 0
pidfinal = 0

datetimestring = strftime('%D %H:%M:%S %p')

changeparcheck=0

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO21, GPIO.OUT)
GPIO.setup(GPIO20, GPIO.OUT)

GPIO21_state = False
GPIO20_State = False
connected = False
connected1 = False

logger = logging.getLogger('mylogger')
handler = logging.FileHandler('/home/pi/Desktop/programs/logs/SWASSlog.log')
logger.addHandler(handler)

logger.warning(datetimestring + " :: " + "starting program run")

def disptime():
    global datetimestring
    datetimestring = strftime('%D %H:%M:%S %p') 
    Datetimebutton.config(text = datetimestring) 
    Datetimebutton.after(1000, disptime) 

try:
    ard_addr = glob.glob("/dev/ttyACM*")[0]
    logger.warning(datetimestring + " :: " + "connecting to " + ard_addr)
    ser = serial.Serial(port=str(ard_addr), baudrate = 9600)
    logger.warning(datetimestring + " :: " + "Serial variable created")
except Exception as e:
    #print("Serial declare exception")
    logger.error(datetimestring + " :: " + "Serial declare exception")
    ComErrorAlarmlabel['text']="Serial Comm Error"
    
def read_from_port(serial_obj):
    global connected
    global val1
    global val2
    global val3
    global changeparcheck
    #print("here")
#     while not connected:
#         #print("here")
#         #print("serial thread parent loop running")
#         connected = True
    while True:
        #print("here")
        #print("serial thread child loop running")
        try:
            readstring = serial_obj.readline().decode("utf-8")
        except serial.SerialException as e:
            #There is no new data from serial port
            logger.error(datetimestring + " :: " + "Serial data read exception")
            ComErrorAlarmlabel['text']="Serial Comm Error"
            val1=0
            val2=0
            val3=0
            return None
        except TypeError as e:
            #Disconnect of USB->UART occured
            #print("Serial data read exception")
            logger.error(datetimestring + " :: " + "Serial data read exception")
            ComErrorAlarmlabel['text']="Serial Comm Error"
            serial_obj.port.close()
            return None
        #readstring = serial_obj.readline().decode("utf-8")
        catcode=readstring.split("*")[0]
        #print(catcode)
        if catcode == "cur":
           try: 
               val1=float(readstring.split("*")[1])
               val3=float(readstring.split("*")[2])
               val2=float(readstring.split("*")[3])
           except Exception as e:
               #print("Serial cur data read interpret exception")
               logger.error(datetimestring + " :: " + "Serial cur data read interpret exception")
               val1=0
               val2=0
               val3=0
               ComErrorAlarmlabel['text']="Serial Comm Error"
#                print(val1)
#                print(val2)
#                print(val3)
        if catcode == "end":
           if changeparcheck == 1:
               sendstringtest=str(BPMSlider.get())+"*"+str(TiVSlider.get())+"*"+str(IERSlider.get()*10)+"*"+str(PIPLSlider.get())+"*"+str(PEEPLSlider.get())+"*"+str(FIOLSlider.get())+"*1*"+str(ALARMONOFF)
               try:
                   ser.write(sendstringtest.encode("utf-8"))
               except Exception as e:
                   #print("Serial data write exception")
                   logger.error(datetimestring + " :: " + "Serial data write exception")
                   ComErrorAlarmlabel['text']="Serial Comm Error"
               changeparcheck=0
           else:
               changeparcheck=0
           try:
               PIPvallabel['text']=readstring.split("*")[1]
               PEEPvallabel['text']=readstring.split("*")[2]
               Tivvallabel['text']=readstring.split("*")[3]
               RRvallabel['text']=readstring.split("*")[4]
               FIO2vallabel['text']=readstring.split("*")[5]
               MinVvallabel['text']=(int(readstring.split("*")[3])*int(readstring.split("*")[4]))/1000
               if int(float(readstring.split("*")[6])*10) == 5:
                   IERvallabel['text']="2:1"
               if int(float(readstring.split("*")[6])*10) == 10:
                   IERvallabel['text']="1:1"
               if int(float(readstring.split("*")[6])*10) == 20:
                   IERvallabel['text']="1:2"
               alarmcode=readstring.split("*")[7]
               PIPAlarmlabel['text']=""
               PEEPAlarmlabel['text']=""
               LeakAlarmlabel['text']=""
               MinVolhighAlarmlabel['text']=""
               MinVollowAlarmlabel['text']=""
               #ComErrorAlarmlabel['text']=""
               #print(alarmcode)
               if "I" in alarmcode:
                   PIPAlarmlabel['text']="PIP High"
               if "E" in alarmcode:
                   PEEPAlarmlabel['text']="PEEP Low"
               if "L" in alarmcode:
                   LeakAlarmlabel['text']="Leak"
               if "H" in alarmcode:
                   MinVolhighAlarmlabel['text']="Min Vol High"
               if "O" in alarmcode:
                   MinVollowAlarmlabel['text']="Min Vol Low"
               ComErrorAlarmlabel['text']="" 
           except Exception as e:
               #print("Serial data cycle end values read interpret exception")
               logger.error(datetimestring + " :: " + "Serial data cycle end values read interpret exception")
               ComErrorAlarmlabel['text']="Serial Comm Error"    
           
   
master = tk.Tk()
master.title("Ventilator")
master.configure(bg='black')
patientname=StringVar()

#master.minsize(1900, 1000)
#master.geometry("500x600")
windowWidth = master.winfo_reqwidth()
windowHeight = master.winfo_reqheight()

#positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
#positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
#alarmoffimage = Image.open("alarmoff.jpg")
#alarmoffpic = PhotoImage(alarmoffimage)
#alarmoffimage = Image.open("alarmoff.jpg")
def animate(i,ys,ys1,ys2):
    global val1
    global val2
    global val3
    # Add y to list
    ys.append(val1)
    ys1.append(val2)
    ys2.append(val3)
    # Limit y list to set number of items
    ys = ys[-x_len:]
    ys1 = ys1[-x_len:]
    ys2 = ys2[-x_len:]
    # Update line with new Y values
    line.set_ydata(ys)
    line1.set_ydata(ys1)
    line2.set_ydata(ys2)
    return line,line1,line2

positionRight = int(100)
positionDown = int(100)

#master.geometry("1900x1000".format(positionRight, positionDown))
master.attributes('-fullscreen', True)

def StartStandbybutton():
    global GPIO21_state
    if GPIO21_state == True:
        GPIO.output(GPIO21, GPIO21_state)
        GPIO21_state = False
        StartStandbybutton['text']="Start"
        sendstringtest=str(BPMSlider.get())+"*"+str(TiVSlider.get())+"*"+str(IERSlider.get()*10)+"*"+str(PIPLSlider.get())+"*"+str(PEEPLSlider.get())+"*"+str(FIOLSlider.get())+"*0*"+str(ALARMONOFF)
        #print(sendstringtest)
        #sendstring="12*400*5*40*5*50*1*1";
        ser.write(sendstringtest.encode("utf-8"))
        #ONlabel = tk.Label(master, text="        ", fg="green")
        #ONlabel = tk.Label(master, text="START", fg="green")
        #ONlabel.grid(row=0, column=1)
    else:
        GPIO.output(GPIO21, GPIO21_state)
        GPIO21_state = True
        StartStandbybutton['text']="Standby"
        sendstringtest=str(BPMSlider.get())+"*"+str(TiVSlider.get())+"*"+str(IERSlider.get()*10)+"*"+str(PIPLSlider.get())+"*"+str(PEEPLSlider.get())+"*"+str(FIOLSlider.get())+"*1*"+str(ALARMONOFF)
        #print(sendstringtest)
        #sendstring="12*400*5*40*5*50*1*0";
        ser.write(sendstringtest.encode("utf-8"))
        #ONlabel = tk.Label(master, text="       ", fg="green")
        #ONlabel = tk.Label(master, text="STANDBY", fg="red")
        #ONlabel.grid(row=0, column=1)


def AlarmOnOffbutton():
    global GPIO20_State
    global ALARMONOFF
    global changeparcheck
    changeparcheck=1
    if GPIO20_State == True:
        GPIO.output(GPIO20, GPIO20_State)
        ALARMONOFF=1
        GPIO20_State = False
        AlarmOnOffbutton['image']=alarmoffpic
        #os.system(screen_shot_cmd)
        #OFFlabel = tk.Label(master, text="ALARM ON", fg="green")
        #OFFlabel.grid(row=1, column=1)
    else:
        GPIO.output(GPIO20, GPIO20_State)
        GPIO20_State = True
        ALARMONOFF=0
        AlarmOnOffbutton['image']=alarmonpic
        #OFFlabel = tk.Label(master, text="ALARM OFF", fg="red")
        #OFFlabel.grid(row=1, column=1)
        
def setTivminmax():
    global changeparcheck
    changeparcheck=1
    global BPM
    global MIVLH
    global MIVLL
    TiVSlider['to']=round(int(MIVLH)*1000/int(BPM))
    TiVSlider['from']=round(int(MIVLL)*1000/int(BPM))
    if TiVSlider['to'] > 600:
        TiVSlider['to']=600
    if TiVSlider['from'] < 200:
        TiVSlider['from']=200

def updatePIPPEEP():
    global changeparcheck
    changeparcheck=1
    global PIPL
    global PEEPL
    global PIPPEEPDif
    PEEPLnew=int(PIPL)-int(PIPPEEPDif)
    if PEEPLnew > 20:
        PEEPLnew=20
    if PEEPLnew < 0:
        PEEPLnew=0
    if PIPPEEPLinkCheckvar.get() == 1:
        PIPPEEPDifSlider["state"] = NORMAL
        PEEPLSlider.set(PEEPLnew)
    else:
        PIPPEEPDifSlider["state"] = DISABLED

def PIPPEEPLinkCheckSelect():
    updatePIPPEEP()
    
def updatePIPPEEPDif(value):
    global PIPPEEPDif
    PIPPEEPDif=value
    updatePIPPEEP()

def updateTiV(value):
    global changeparcheck
    changeparcheck=1
    global TiV
    TiV=value

def updateBPM(value):
    global changeparcheck
    changeparcheck=1
    global BPM
    BPM=value
    setTivminmax()

def updateIER(value):
    global changeparcheck
    changeparcheck=1
    IER=value
     
def updatePIPL(value):
    global PIPL
    PIPL=value
    updatePIPPEEP()
     
def updatePEEPL(value):
    global PEEPL
    PEEPL=value
    updatePIPPEEP()
     
def updateMIVLH(value):
    global MIVLH
    MIVLH=value
    setTivminmax()
     
def updateMIVLL(value):
    global MIVLL
    MIVLL=value
    setTivminmax()
    
def updateFIOL(value):
    global changeparcheck
    changeparcheck=1
    FIOL=value
 
def updateFLOWTRIG(value):
    changeparcheck=1
    FLOWTRIG=value
    
def updatePRESTRIG(value):
    changeparcheck=1
    PRESTRIG=value

    
def VMmodeselect():
    changeparcheck=1
    CurrentMode=1
    #VMmodeButton.select()
    #PMmodeButton.deselect()

def PMmodeselect():
    changeparcheck=1
    CurrentMode=2
    #VMmodeButton.deselect()
    #PMmodeButton.select()

def CPAPmodeselect():
    changeparcheck=1
    CurrentMode=3
    #VMmodeButton.deselect()
    #PMmodeButton.select()
    
def PSmodeselect():
    changeparcheck=1
    CurrentMode=4
    #VMmodeButton.deselect()
    #PMmodeButton.select()

def exitbutton():
    GPIO.output(GPIO21, False)
    GPIO.output(GPIO20, False)
    try:
        ser.flushInput()
        ser.flushOutput()
        ser.close()
    except Exception as e:
         #print("Serial close exception")
         logger.error(datetimestring + " :: " + "Serial close exception")
    ani.event_source.stop()
    try:
        thread.exit()
#         print("Closing serial thread")
    except Exception as e:
        #print("Closing serial thread exception")
        logger.error(datetimestring + " :: " + "Closing serial thread exception")
    try:
        #master.destroy()
        #print("Closing program")
        logger.error(datetimestring + " :: " + "Closing program")
        sys.exit()
#         print("Closing program after")
    except Exception as e:
        #print("Closing program exception")
        logger.error(datetimestring + " :: " + "Closing program exception")
        

def snapshotbutton():
    try:
        os.system(screen_shot_cmd)
        #print("screen shot taken")
        logger.warning(datetimestring + " :: " + "screen shot taken")
    except Exception as e:
        #print("Screenshot exception")
        logger.error(datetimestring + " :: " + "Screenshot exception")
        return None
   
def patientnamebutton():
    global patientname
    #print("patient name button clicked")
    Patientnamebutton = tk.Entry(AlarmDisplayGroup, font=('Helvetica', 12, 'bold'), textvariable=patientname,width=25)
    Patientnamebutton.grid(row=0, column=7)
    
def settingsbutton():
    #print("settings button clicked")
    settingsWindow = Toplevel(master) 
    settingsWindow.title("Settings")
    settingsWindowWidth=800
    settingsWindowHeight=500
    settingsWindow.geometry('{}x{}+{}+{}'.format(settingsWindowWidth, settingsWindowHeight, int(master.winfo_screenwidth()/2)-int(settingsWindowWidth/2), int(master.winfo_screenheight()/2)-int(settingsWindowHeight/2)))
    # Create a Tkinter variable
    res_choice_sel = StringVar(master)
    baud_rate_sel = StringVar(master)
    pwm_freq_sel = StringVar(master)
    # Dictionary with options
    res_choices = ["1ms","10ms","20ms","50ms"]
    baud_rate_choices = ["2400", "4800", "9600","19200","38400"]
    pwm_freq_choices = ["64kHz", "8kHz", "1kHz","500hz"]
    
    res_choice_sel.set(res_choices[0]) # set the default option
    baud_rate_sel.set(baud_rate_choices[2])
    pwm_freq_sel.set(pwm_freq_choices[1])

    res_choice_sel_popupMenu = tk.OptionMenu(settingsWindow, res_choice_sel, *res_choices)
    res_choice_sel_popupMenu['width']=5
    res_choice_sel_Label = tk.Label(settingsWindow, text="Set Resolution:", anchor='w', justify=LEFT)
    res_choice_sel_Label['width']=18
    res_choice_sel_Label.grid(row = 0, column = 0)
    res_choice_sel_popupMenu.grid(row = 0, column =1)
    
    
    baud_rate_sel_popupMenu = tk.OptionMenu(settingsWindow, baud_rate_sel, *baud_rate_choices)
    baud_rate_sel_popupMenu['width']=5
    baud_rate_sel_Label = tk.Label(settingsWindow, text="Set Baud Rate:", anchor='w', justify=LEFT)
    baud_rate_sel_Label['width']=18
    baud_rate_sel_Label.grid(row = 1, column = 0)
    baud_rate_sel_popupMenu.grid(row = 1, column =1)
    
    pwm_freq_sel_popupMenu = tk.OptionMenu(settingsWindow, pwm_freq_sel, *pwm_freq_choices)
    pwm_freq_sel_popupMenu['width']=5
    pwm_freq_sel_Label = tk.Label(settingsWindow, text="Set PWM freq:", anchor='w', justify=LEFT)
    pwm_freq_sel_Label['width']=18
    pwm_freq_sel_Label.grid(row = 2, column = 0)
    pwm_freq_sel_popupMenu.grid(row = 2, column =1)
    
    screenshot_folder_sel_Label = tk.Label(settingsWindow, text="Select folder for\nstoring screenshot:", anchor='w', justify=LEFT)
    screenshot_folder_sel_Label['width']=18
    screenshot_folder_sel_Label['height']=2
    screenshot_folder_sel_Label.grid(row = 3, column = 0)
    
    screenrec_folder_sel_Label = tk.Label(settingsWindow, text="Select folder for\nstoring screen record:", anchor='w', justify=LEFT)
    screenrec_folder_sel_Label['width']=18
    screenrec_folder_sel_Label['height']=2
    screenrec_folder_sel_Label.grid(row = 4, column = 0)
    
    def screenshot_folder_sel_browse_button(*args):
        folder_path = StringVar()
        filename = filedialog.askdirectory()
        folder_path.set(filename)
        if str(filename) == "":
            screenshot_folder_sel_browse_button['text']="Browse"
        else:
            screenshot_folder_sel_browse_button['text']=str(filename)
        #print(filename)
        
    def screenrec_folder_sel_browse_button(*args):
        folder_path = StringVar()
        filename = filedialog.askdirectory()
        folder_path.set(filename)
        if str(filename) == "":
            screenrec_folder_sel_browse_button['text']="Browse"
        else:
            screenrec_folder_sel_browse_button['text']=str(filename)
        #print(filename)
        
    def check_ip_add(*args):
        #print("check ip address button clicked")
        # getting IP Address
        address = subprocess.check_output(['hostname', '-s', '-I']).decode('utf-8')[:-1]
        #print(address.split(" ")[0])
        hostname = socket.gethostname() 
        IPAddr = socket.gethostbyname(hostname)
        try:
            ipaddrstr=str(address.split(" ")[0])
            if ipaddrstr == "" or len(ipaddrstr) > 20:
                check_ip_address_Button['text']="Check"
                logger.error(datetimestring + " :: " + "No connections found")
                #print("No connections found")
            else:
                check_ip_address_Button['text']=ipaddrstr
        except Exception as e:
            check_ip_address_Button['text']="Check"
            logger.error(datetimestring + " :: " + "IP addr retrieval error")
            #print("IP addr retrieval error")
        try:
            ipaddrstr=str(address.split(" ")[1])
            if ipaddrstr == "" or len(ipaddrstr) > 20:
                check_ip_address2_Button['text']=""
                check_ip_address2_Button['bd']=0
                logger.error(datetimestring + " :: " + "No additional connections found")
                #print("No connections found")
            else:
                check_ip_address2_Button['text']=ipaddrstr
                check_ip_address2_Button['bd']=1
        except Exception as e:
            check_ip_address2_Button['text']=""
            check_ip_address2_Button['bd']=0
            logger.error(datetimestring + " :: " + "Secondary IP addr retrieval error")
            #print("Secondary IP addr retrieval error")
            
    def check_hostname(*args):
        hostname = socket.gethostname() 
        check_hostname_Button['text']=hostname
        
    def show_logs_button(*args):
        logsWindow = Toplevel(master) 
        logsWindow.title("Log Window")
        logsWindowWidth=800
        logsWindowHeight=500
        logsWindow.geometry('{}x{}+{}+{}'.format(logsWindowWidth, logsWindowHeight, int(master.winfo_screenwidth()/2)-int(logsWindowWidth/2), int(master.winfo_screenheight()/2)-int(logsWindowHeight/2)))
        horizontalscrollbar = tk.Scrollbar(logsWindow, orient = 'horizontal') 
        # attach Scrollbar to root window at the bootom 
        horizontalscrollbar.pack(side = BOTTOM, fill = X) 
        # create a vertical scrollbar-no need to write orient as it is by default vertical 
        verticalscrollbar = tk.Scrollbar(logsWindow) 
        # attach Scrollbar to root window on the side 
        verticalscrollbar.pack(side = RIGHT, fill = Y)
        rd = open ("/home/pi/Desktop/programs/logs/SWASSlog.log", "r")
        texthold = tk.Text(logsWindow, wrap = NONE, xscrollcommand = horizontalscrollbar.set,  yscrollcommand = verticalscrollbar.set, state='normal', width=80, height=50)
        while True:
            # Read next line
            line = rd.readline()
            # If line is blank, then you struck the EOF
            if not line :
                break;
            texthold.insert(END,line.strip())
            texthold.insert(END,"\n")
        # Close file 
        rd.close()
        texthold.pack(side=TOP, fill=X)
        texthold["state"] = DISABLED
        # here command represents the method to be executed xview is executed on object 't' Here t may represent any widget 
        horizontalscrollbar.config(command=texthold.xview) 
        # here command represents the method to be executed yview is executed on object 't' Here t may represent any widget 
        verticalscrollbar.config(command=texthold.yview)
        
    def clear_logs_button(*args):
        os.system("rm /home/pi/Desktop/programs/logs/SWASSlog.log")
        os.system("touch /home/pi/Desktop/programs/logs/SWASSlog.log")
        handler = logging.FileHandler('/home/pi/Desktop/programs/logs/SWASSlog.log')
        logger.addHandler(handler)
        
    def start_prog_onboot_button(*args):
        rd = open ("/etc/profile", "r")
        chkboot = 0
        while True:
            # Read next line
            line = rd.readline()
            # If line is blank, then you struck the EOF
            if not line :
                break;
            #print(line.strip())
            if "python3 /home/pi/Desktop/programs/Ventilator.py" in line:
                chkboot = 1
                break;
        # Close file 
        rd.close()
        if chkboot == 0:
            os.system("sudo sh -c \"echo python3 /home/pi/Desktop/programs/Ventilator.py >> /etc/profile\"")
            start_prog_onboot_button['text']="Enabled"
        else:
            #start_prog_onboot_button['text']="Enabled"
            os.system("sudo sed -i.bak '$d' /etc/profile")
            start_prog_onboot_button['text']="Disabled"
            
    def reboot_button(*args):
        sendstringtest=str(BPMSlider.get())+"*"+str(TiVSlider.get())+"*"+str(IERSlider.get()*10)+"*"+str(PIPLSlider.get())+"*"+str(PEEPLSlider.get())+"*"+str(FIOLSlider.get())+"*0*"+str(ALARMONOFF)
        ser.write(sendstringtest.encode("utf-8"))
        os.system("sudo reboot")
        
                    
    screenshot_folder_sel_browse_button = tk.Button(settingsWindow, text="Browse", command=screenshot_folder_sel_browse_button, width=10, height=2, wraplength=100)
    screenshot_folder_sel_browse_button.grid(row=3, column=1)
    
    screenrec_folder_sel_browse_button = tk.Button(settingsWindow, text="Browse", command=screenrec_folder_sel_browse_button, width=10, height=2, wraplength=100)
    screenrec_folder_sel_browse_button.grid(row=4, column=1)
    
    check_ip_Label = tk.Label(settingsWindow, text="IP address:", width=18, height=1, anchor='w', justify=LEFT)
    check_ip_Label.grid(row=5, column=0)
    
    check_ip_address_Button = tk.Button(settingsWindow, text="Check", justify=CENTER, command=check_ip_add)
    check_ip_address_Button['width']=12
    check_ip_address_Button.grid(row = 5, column = 1)
    
    check_ip_address2_Button = tk.Button(settingsWindow, text="", justify=CENTER, bd=0)
    check_ip_address2_Button['width']=12
    check_ip_address2_Button.grid(row = 5, column = 2)
    
    check_hostname_Label = tk.Label(settingsWindow, text="Hostname:", width=18, height=1, anchor='w', justify=LEFT)
    check_hostname_Label.grid(row=6, column=0)
    
    check_hostname_Button = tk.Button(settingsWindow, text="Check", justify=CENTER, command=check_hostname)
    check_hostname_Button['width']=12
    check_hostname_Button.grid(row = 6, column = 1)
    
    check_cwd_Label = tk.Label(settingsWindow, text="Current working directory:", width=20, height=1, anchor='w', justify=LEFT)
    check_cwd_Label.grid(row=7, column=0)
        
    dirpath = os.getcwd()
    cwd_Label = tk.Label(settingsWindow, text=dirpath, width=25, height=1, anchor='w', justify=LEFT)
    cwd_Label.grid(row=7, column=1)
    
    check_USB_dev_Label = tk.Label(settingsWindow, text="Current MC unit addr:", width=20, height=1, anchor='w', justify=LEFT)
    check_USB_dev_Label.grid(row=8, column=0)
    
    ard_addr = glob.glob("/dev/ttyACM*")[0]
    USB_dev_Label = tk.Label(settingsWindow, text=ard_addr, width=25, height=1, anchor='w', justify=LEFT)
    USB_dev_Label.grid(row=8, column=1)
    #foldername = os.path.basename(dirpath)
    #print("Directory name is : " + foldername)
    
    show_logs_button = tk.Button(settingsWindow, text="Open logs", command=show_logs_button, width=18, height=1)
    show_logs_button.grid(row=9, column=0)
    
    clear_logs_button = tk.Button(settingsWindow, text="Clear logs", command=clear_logs_button, width=18, height=1)
    clear_logs_button.grid(row=9, column=1)
    
    start_prog_onboot_label = tk.Label(settingsWindow, text="Start program on boot:", width=20, height=1, anchor='w', justify=LEFT)
    start_prog_onboot_label.grid(row=10, column=0)
    
    start_prog_onboot_button = tk.Button(settingsWindow, command=start_prog_onboot_button, width=18, height=1)
    rd = open ("/etc/profile", "r")
    chkboot = 0
    while True:
        # Read next line
        line = rd.readline()
        # If line is blank, then you struck the EOF
        if not line :
            break;
        #print(line.strip())
        if "python3 /home/pi/Desktop/programs/Ventilator.py" in line:
            chkboot = 1
            break;
    # Close file 
    rd.close()
    if chkboot == 0:
        start_prog_onboot_button['text']="Disabled"
    else:
        start_prog_onboot_button['text']="Enabled"
    start_prog_onboot_button.grid(row=10, column=1)
    
    reboot_button = tk.Button(settingsWindow, text="Reboot", command=reboot_button, width=18, height=1)
    reboot_button.grid(row=11, column=0)
            
    # on change dropdown value
    def change_dropdown_res(*args):
        print( res_choice_sel.get() )
        
    def change_dropdown_bdr(*args):
        print( baud_rate_sel.get() )
        
    def change_dropdown_pwm(*args):
        print( pwm_freq_sel.get() )

    # link function to change dropdown
    res_choice_sel.trace('w', change_dropdown_res)
    baud_rate_sel.trace('w', change_dropdown_bdr)
    pwm_freq_sel.trace('w', change_dropdown_pwm)
    
def patientnameentry(event):
    #print("enter pressed")
    global patientname
    if patientname.get() == "":
        Patientnamebutton = tk.Button(AlarmDisplayGroup, text="Enter Patient name", font=('Helvetica', 12, 'bold'), bd=1, command=patientnamebutton, width=25, height=2, fg="white", bg="black")
    else:
        Patientnamebutton = tk.Button(AlarmDisplayGroup, text=patientname.get(), font=('Helvetica', 12, 'bold'), bd=1, command=patientnamebutton, width=25, height=2, fg="white", bg="black")
    Patientnamebutton.grid(row=0, column=7)
     
def screenrecordbutton():
    global check_screen_record
    global pidfinal
    if check_screen_record == 0:
        try:
            os.system(screen_record_cmd)
            sleep( 0.5)
            #pid_rmd=os.system("pidof recordmydesktop").stdout
            cmd = [ 'pidof', 'recordmydesktop' ]
            pid_rmd0 = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0].rstrip()
            #pid_rmd = subprocess.Popen( cmd, stdout=subprocess.PIPE ).stdout()
            pid_rmd1=str(pid_rmd0).strip('b')
            pid_rmd2=str(pid_rmd1).strip('\'')
            pidfinal=int(pid_rmd2)
            print(pidfinal)
            #print("screen record start")
            logger.warning(datetimestring + " :: " + "screen record start")
            Screenrecordbutton['image']=screenrecordonpic
            check_screen_record=1
        except Exception as e:
            #print("Screen record start exception")
            logger.error(datetimestring + " :: " + "Screen record start exception")
            return None
    elif check_screen_record == 1:
        try:
            #print("screen record stop try")
            logger.warning(datetimestring + " :: " + "screen record stop try")
            #os.system("fg")
            os.system("sudo kill -SIGINT "+str(pidfinal))
            Screenrecordbutton['image']=screenrecordbusypic
            check_screen_record=2
            Screenrecordbutton.after(1000, screenrecordbutton)
        except Exception as e:
            #print("Screen record stop exception")
            logger.error(datetimestring + " :: " + "Screen record stop exception")
            return None
    elif check_screen_record == 2:
        try:
            #print("screen record check try")
            logger.warning(datetimestring + " :: " + "screen record check try")
            cmd = [ 'pidof', 'recordmydesktop' ]
            pid_rmd0 = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0].rstrip()
            #pid_rmd = subprocess.Popen( cmd, stdout=subprocess.PIPE ).stdout()
            pid_rmd1=str(pid_rmd0).strip('b')
            pid_rmd2=str(pid_rmd1).strip('\'')
            print(pid_rmd2)
            if pid_rmd2 == "":
                Screenrecordbutton['image']=screenrecordoffpic
                check_screen_record=0
                logger.warning(datetimestring + " :: " + "screen record render complete")
            else:
                Screenrecordbutton.after(1000, screenrecordbutton)
        except Exception as e:
            logger.error(datetimestring + " :: " + "Screen record check exception")
            #print("Screen record check exception")
            return None
        
master.bind('<Return>', patientnameentry)

MasterGroup = LabelFrame(master, text = "", bg="black")
MasterGroup.grid(row=0, column=0)

Datetimebutton = tk.Button(MasterGroup, text="Exit", width=20, height=2, bd=1, bg="black", fg="white")
Datetimebutton.pack()

radioGroup = LabelFrame(MasterGroup, text = "Select Mode", fg="white", bg="black")
radioGroup.pack()

CurrentMode=IntVar()
VMmodeButton=tk.Radiobutton(radioGroup, text="Volume Mode", variable=CurrentMode, value=1, command=VMmodeselect, fg="white", bg="black")
VMmodeButton.pack(anchor=W)
#VMmodeButton.grid(row=9, column=0)
#VMmodeButton.pack(anchor=W)

PMmodeButton=tk.Radiobutton(radioGroup, text="Pressure Mode", variable=CurrentMode, value=2, command=PMmodeselect, fg="white", bg="black")
PMmodeButton.pack(anchor=W)
#PMmodeButton.grid(row=10, column=0)

CPAPmodeButton=tk.Radiobutton(radioGroup, text="CPAP Mode", variable=CurrentMode, value=3, command=CPAPmodeselect, fg="white", bg="black")
CPAPmodeButton.pack(anchor=W)
#CPAPmodeButton.grid(row=11, column=0)

PSmodeButton=tk.Radiobutton(radioGroup, text="Pressure Support Mode", variable=CurrentMode, value=4, command=PSmodeselect, fg="white", bg="black")
PSmodeButton.pack(anchor=W)
CurrentMode.set(1)
#PSmodeButton.grid(row=12, column=0)

#ServoC= Scale(master, from_=0, to=180, orient=HORIZONTAL, command=update, background = "#C06C84",width =80, label = "ServoMotorAngleController",length = 500,  activebackground = "#C06C84",font = "Arial 16 bold")
BPMSlider= tk.Scale(MasterGroup, from_=5, to=30, command=updateBPM, width =20, label = "Breaths per minute",length = 200, orient=HORIZONTAL, fg="white", bg="black")
BPMSlider.set(12)
BPMSlider.pack(anchor=N)

MIVLHSlider= tk.Scale(MasterGroup, from_=4, to=8, resolution=1, command=updateMIVLH, width =20, label = "MIV Upper Limit (in Lpm)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
MIVLHSlider.set(6)
MIVLHSlider.pack(anchor=CENTER)

MIVLLSlider= tk.Scale(MasterGroup, from_=2, to=4, resolution=1, command=updateMIVLL, width =20, label = "MIV Lower Limit (in Lpm)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
MIVLLSlider.set(2)
MIVLLSlider.pack(anchor=CENTER)

TiVSlider= tk.Scale(MasterGroup, from_=round(int(MIVLL)*1000/int(BPM)), to=round(int(MIVLH)*1000/int(BPM)), resolution=25, command=updateTiV, width =20, label = "Tidal Volume (in mL)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
TiVSlider.set(300)
TiVSlider.pack(anchor=CENTER)

IERSlider= tk.Scale(MasterGroup, from_=0.5, to=2.0, resolution=0.5, command=updateIER, width =20, label = "Insp to Exp time ratio",length = 200, orient=HORIZONTAL, fg="white", bg="black")
IERSlider.set(0.5)
IERSlider.pack(anchor=CENTER)

PIPLSlider= tk.Scale(MasterGroup, from_=20, to=60, command=updatePIPL, width =20, label = "PIP Limit (in cmofH20)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
PIPLSlider.set(40)
PIPLSlider.pack(anchor=CENTER)

PEEPLSlider= tk.Scale(MasterGroup, from_=0, to=20, command=updatePEEPL, width =20, label = "PEEP Limit (in cmofH20)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
PEEPLSlider.set(5)
PEEPLSlider.pack(anchor=CENTER)

PIPPEEPLinkCheckvar=IntVar()

PIPPEEPLinkCheck = tk.Checkbutton(MasterGroup, text='Link PIP & PEEP', variable=PIPPEEPLinkCheckvar, command=PIPPEEPLinkCheckSelect, fg="white", bg="black")
PIPPEEPLinkCheck.pack(anchor=W)

PIPPEEPDifSlider= tk.Scale(MasterGroup, from_=5, to=30, command=updatePIPPEEPDif, width =20, label = "PIP PEEP Dif (in cm of H20)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
PIPPEEPDifSlider.set(20)
PIPPEEPDifSlider.pack(anchor=CENTER)

FIOLSlider= tk.Scale(MasterGroup, from_=21, to=100, resolution=1, command=updateFIOL, width =20, label = "FiO2 limit in %",length = 200, orient=HORIZONTAL, fg="white", bg="black")
FIOLSlider.set(50)
FIOLSlider.pack(anchor=CENTER)

FLOWTRIGSlider= tk.Scale(MasterGroup, from_=1, to=10, resolution=1, command=updateFLOWTRIG, width =20, label = "Flow trigger (in lpm)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
FLOWTRIGSlider.set(5)
FLOWTRIGSlider.pack(anchor=CENTER)

PRESTRIGSlider= tk.Scale(MasterGroup, from_=1, to=10, resolution=1, command=updatePRESTRIG, width =20, label = "Press trigger (in cmofH20)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
PRESTRIGSlider.set(3)
PRESTRIGSlider.pack(anchor=CENTER)

INSPPAUSESlider= tk.Scale(MasterGroup, from_=0, to=20, resolution=1, command=updatePRESTRIG, width =20, label = "Insp pause time (in %)",length = 200, orient=HORIZONTAL, fg="white", bg="black")
INSPPAUSESlider.set(10)
INSPPAUSESlider.pack(anchor=CENTER)

#OFFbutton = tk.Button(master, text="GPIO 20",bg="blue" , command=GPIO20button)
#ONbutton = tk.Button(master, text="GPIO 21", bg="blue", command=GPIO21button)
StartStandbybutton = tk.Button(master, text="Start", width=8, height=2, bd=1, font=('Helvetica', 30, 'bold'), command=StartStandbybutton, fg="white", bg="black")        
StartStandbybutton.grid(row=1, column=0)

ParDisGroup = LabelFrame(master, text = "", bg="black")
ParDisGroup.grid(row=1, column=1)

PIPDisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
PIPDisGroup.grid(row=0, column=0)

PIPnamelabel = tk.Label(PIPDisGroup, text="Peak insp pressure", width=20, height=1, bd=0, fg="yellow", bg="black")
PIPnamelabel.grid(row=0, column=0)

PIPvallabel = tk.Label(PIPDisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
PIPvallabel.grid(row=1, column=0)

PIPunitlabel = tk.Label(PIPDisGroup, text="cm of H20", width=20, height=1, bd=0, fg="yellow", bg="black")
PIPunitlabel.grid(row=2, column=0)

PEEPDisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
PEEPDisGroup.grid(row=0, column=1)

PEEPnamelabel = tk.Label(PEEPDisGroup, text="Peak end exp pressure", width=20, height=1, bd=0, fg="yellow", bg="black")
PEEPnamelabel.grid(row=0, column=0)

PEEPvallabel = tk.Label(PEEPDisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
PEEPvallabel.grid(row=1, column=0)

PEEPunitlabel = tk.Label(PEEPDisGroup, text="cm of H20", width=20, height=1, bd=0, fg="yellow", bg="black")
PEEPunitlabel.grid(row=2, column=0)

TivDisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
TivDisGroup.grid(row=0, column=2)

Tivnamelabel = tk.Label(TivDisGroup, text="Tidal Volume", width=20, height=1, bd=0, fg="yellow", bg="black")
Tivnamelabel.grid(row=0, column=0)

Tivvallabel = tk.Label(TivDisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
Tivvallabel.grid(row=1, column=0)

Tivunitlabel = tk.Label(TivDisGroup, text="ml", width=20, height=1, bd=0, fg="yellow", bg="black")
Tivunitlabel.grid(row=2, column=0)

RRDisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
RRDisGroup.grid(row=0, column=3)

RRnamelabel = tk.Label(RRDisGroup, text="Respiratory rate", width=20, height=1, bd=0, fg="yellow", bg="black")
RRnamelabel.grid(row=0, column=0)

RRvallabel = tk.Label(RRDisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
RRvallabel.grid(row=1, column=0)

RRunitlabel = tk.Label(RRDisGroup, text="breaths per minute", width=20, height=1, bd=0, fg="yellow", bg="black")
RRunitlabel.grid(row=2, column=0)

FIO2DisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
FIO2DisGroup.grid(row=0, column=4)

FIO2namelabel = tk.Label(FIO2DisGroup, text="FiO2", width=20, height=1, bd=0, fg="yellow", bg="black")
FIO2namelabel.grid(row=0, column=0)

FIO2vallabel = tk.Label(FIO2DisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
FIO2vallabel.grid(row=1, column=0)

FIO2unitlabel = tk.Label(FIO2DisGroup, text="percentage", width=20, height=1, bd=0, fg="yellow", bg="black")
FIO2unitlabel.grid(row=2, column=0)

MinVDisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
MinVDisGroup.grid(row=0, column=5)

MinVnamelabel = tk.Label(MinVDisGroup, text="Minute Volume", width=20, height=1, bd=0, fg="yellow", bg="black")
MinVnamelabel.grid(row=0, column=0)

MinVvallabel = tk.Label(MinVDisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
MinVvallabel.grid(row=1, column=0)

MinVunitlabel = tk.Label(MinVDisGroup, text="litres per min", width=20, height=1, bd=0, fg="yellow", bg="black")
MinVunitlabel.grid(row=2, column=0)

IERDisGroup = LabelFrame(ParDisGroup, text = "", bd=1, bg="black")
IERDisGroup.grid(row=0, column=6)

IERnamelabel = tk.Label(IERDisGroup, text="Insp to Exp ratio", width=20, height=1, bd=0, fg="yellow", bg="black")
IERnamelabel.grid(row=0, column=0)

IERvallabel = tk.Label(IERDisGroup, text="--", font=('Helvetica', 38, 'bold'), width=8, height=1, bd=0, fg="yellow", bg="black")
IERvallabel.grid(row=1, column=0)

IERunitlabel = tk.Label(IERDisGroup, text="ratio", width=20, height=1, bd=0, fg="yellow", bg="black")
IERunitlabel.grid(row=2, column=0)

# Creating a photoimage object to use image 
alarmoffpic = PhotoImage(file = "/home/pi/Desktop/programs/images/alarmoff.pgm")
alarmonpic = PhotoImage(file = "/home/pi/Desktop/programs/images/alarmon.pgm")
snapshotpic = PhotoImage(file = "/home/pi/Desktop/programs/images/screen_shot.pgm")
screenrecordoffpic = PhotoImage(file = "/home/pi/Desktop/programs/images/screen_record_off.png")
screenrecordonpic = PhotoImage(file = "/home/pi/Desktop/programs/images/screen_record_on.png")
screenrecordbusypic = PhotoImage(file = "/home/pi/Desktop/programs/images/screen_record_process.png")
settingsiconpic = PhotoImage(file = "/home/pi/Desktop/programs/images/settings_icon.png")

#Exitbutton = tk.Button(master, text="Exit",bg="red", command=master.destroy)
AlarmOnOffbutton = tk.Button(ParDisGroup, text="", bd=0, image=alarmoffpic, command=AlarmOnOffbutton, fg="white", bg="black")
AlarmOnOffbutton.grid(row=0, column=7)

disptime()

DisplayGroup = LabelFrame(master, text = "", bg="black")
DisplayGroup.grid(row=0, column=1)

AlarmDisplayGroup = LabelFrame(DisplayGroup, text = "", width=150, height=2, fg="white", bg="black")
AlarmDisplayGroup.grid(row=0, column=0)

PIPAlarmlabel = tk.Label(AlarmDisplayGroup, text="", font=('Helvetica', 18, 'bold'), width=9, height=2, bd=0, fg="red", bg="black")
PIPAlarmlabel.grid(row=0, column=0)

PEEPAlarmlabel = tk.Label(AlarmDisplayGroup, text="", font=('Helvetica', 18, 'bold'), width=9, height=2, bd=0, fg="red", bg="black")
PEEPAlarmlabel.grid(row=0, column=1)

LeakAlarmlabel = tk.Label(AlarmDisplayGroup, text="", font=('Helvetica', 18, 'bold'), width=6, height=2, bd=0, fg="red", bg="black")
LeakAlarmlabel.grid(row=0, column=2)

MinVolhighAlarmlabel = tk.Label(AlarmDisplayGroup, text="", font=('Helvetica', 18, 'bold'), width=12, height=2, bd=0, fg="red", bg="black")
MinVolhighAlarmlabel.grid(row=0, column=3)

MinVollowAlarmlabel = tk.Label(AlarmDisplayGroup, text="", font=('Helvetica', 18, 'bold'), width=12, height=2, bd=0, fg="red", bg="black")
MinVollowAlarmlabel.grid(row=0, column=4)

Titlelabel = tk.Label(AlarmDisplayGroup, text="SWAAS 3.0", font=('Helvetica', 22, 'bold'), width=20, height=2, bd=0, fg="white", bg="black")
Titlelabel.grid(row=0, column=5)

ComErrorAlarmlabel = tk.Label(AlarmDisplayGroup, text="", font=('Helvetica', 18, 'bold'), width=17, height=2, bd=0, fg="red", bg="black")
ComErrorAlarmlabel.grid(row=0, column=6)

Patientnamebutton = tk.Button(AlarmDisplayGroup, text="Enter Patient name", font=('Helvetica', 12, 'bold'), bd=1, command=patientnamebutton, width=25, height=2, fg="white", bg="black")
Patientnamebutton.grid(row=0, column=7)

Snapshotbutton = tk.Button(AlarmDisplayGroup, text="", bd=0, image=snapshotpic, command=snapshotbutton, width=70, height=50)
Snapshotbutton.grid(row=0, column=8)

Screenrecordbutton = tk.Button(AlarmDisplayGroup, text="", bd=0, image=screenrecordoffpic, command=screenrecordbutton, width=70, height=50)
Screenrecordbutton.grid(row=0, column=9)

Settingsbutton = tk.Button(AlarmDisplayGroup, text="", bd=0, image=settingsiconpic, command=settingsbutton, width=70, height=50)
Settingsbutton.grid(row=0, column=10)

Exitbutton = tk.Button(AlarmDisplayGroup, text="X", font=('Helvetica', 20, 'bold'), bd=0, command=exitbutton, fg="white", bg="black")
Exitbutton.grid(row=0, column=11)

try:
    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.daemon = True
#     print("serial thread declared")
except Exception as e:
    #print("Thread declaration exception")
    logger.error(datetimestring + " :: " + "Thread declaration exception")
    ComErrorAlarmlabel['text']="Serial Comm Error"
    
try:
    thread.start()
    #print("serial thread started")
    logger.error(datetimestring + " :: " + "serial thread started")
except Exception as e:
    #print("Thread start exception")
    logger.error(datetimestring + " :: " + "Thread start exception")
    ComErrorAlarmlabel['text']="Serial Comm Error"
    
 
#process = multiprocessing.Process(target=takesnapshot, args=()) 

x_len = 300         # Number of points to display
y_range = [0, 60]  # Range of possible Y values to display
y_range1 = [-40, 40]
y_range2 = [0, 600]
# Create figure for plotting
fig = plt.figure(figsize=(17, 9))
fig.patch.set_facecolor('xkcd:black')
#fig = plt.figure(figsize=(10, 9))
ax = fig.add_subplot(3, 1, 1)
ax.set_facecolor('xkcd:black')
#ax.spines['right'].set_color('red')
ax.spines['left'].set_color('cyan')
ax.tick_params(axis='x', colors='cyan')
ax.tick_params(axis='y', colors='cyan')
plt.xlabel("")
#ax.set_facecolor((1.0, 0.47, 0.42))
plt.xticks(visible = True)
ax1 = fig.add_subplot(3, 1, 2)
ax1.set_facecolor('xkcd:black')
ax1.spines['left'].set_color('cyan')
ax1.tick_params(axis='x', colors='cyan')
ax1.tick_params(axis='y', colors='cyan')
plt.xlabel("")
plt.xticks(visible = True)
ax2 = fig.add_subplot(3, 1, 3)
ax2.set_facecolor('xkcd:black')
ax2.spines['left'].set_color('cyan')
ax2.tick_params(axis='x', colors='cyan')
ax2.tick_params(axis='y', colors='cyan')
plt.xlabel("")
plt.xticks(visible = True)
plt.xlabel("\n Time (seconds)")
ax2.xaxis.label.set_color('cyan')
xs = list(range(0, x_len))
xs1 = list(range(0, x_len))
xs2 = list(range(0, x_len))
ys = [0] * x_len
ys1 = [0] * x_len
ys2 = [0] * x_len
ax.set_ylabel("Airway pressure (cm of H20)\n")
ax.yaxis.label.set_color('cyan')
ax1.set_ylabel("Flow (Lpm)")
ax1.yaxis.label.set_color('cyan')
ax2.set_ylabel("Volume (mL)")
ax2.yaxis.label.set_color('cyan')
ax.set_ylim(y_range)
ax1.set_ylim(y_range1)
ax2.set_ylim(y_range2)
# Create a blank line. We will update the line in animate
line, = ax.plot(xs, ys)
line1, = ax1.plot(xs1, ys1)
line2, = ax2.plot(xs2, ys2)
Canvas = FigureCanvasTkAgg(fig, master=DisplayGroup)
Canvas.get_tk_widget().grid(column=0,row=1)
ani = animation.FuncAnimation(fig, animate, fargs=(ys,ys1,ys2), interval=1, blit=True)

#plt.show()
master.mainloop()
print("Main loop")
