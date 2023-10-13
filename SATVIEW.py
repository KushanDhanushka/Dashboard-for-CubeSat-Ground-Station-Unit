#_importing necessary packages and libraries.
import sys
import time
import serial
import serial.tools.list_ports
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QComboBox, QHBoxLayout
from PySide6.QtGui import QPalette, QColor
import binascii
import cv2
import os
from datetime import datetime

# This is for creating Setup and exe version of this program
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#_main class for serialmonitor
class SerialMonitor(QMainWindow):
    def __init__(self):
        
        self.imcount = 0 # To upcount the image names
        
        # This code snippet creates a seperate folder for each time the program runs to store data at one place
        current_datetime = datetime.now() 
        formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
        
        self.folder_path = formatted_datetime
        
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
            
        # To store recieved gyro data.    
        self.file_path = os.path.join(self.folder_path, "RECEIVED GYRO DATA.txt")  
          
        #Superinitializing
        super().__init__()
        self.mode = "light"  # Initial mode is light

        central_widget = QWidget() #_main widegt
        self.setCentralWidget(central_widget)

        # Horizontal layout for connetion controls (Pushbuttons-> Code gives their meanings no comments needed)
        h0_layout = QHBoxLayout() 

        self.cp_button = QPushButton("Update COM_Port List")
        h0_layout.addWidget(self.cp_button)
        self.cp_button.clicked.connect(self.update_port_list)

        self.connect_button = QPushButton("Connect")
        h0_layout.addWidget(self.connect_button)
        self.connect_button.clicked.connect(self.connect_serial)

        self.disconnect_button = QPushButton("Disconnect")
        h0_layout.addWidget(self.disconnect_button)
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        self.disconnect_button.setEnabled(True)
        
        self.toggle_button = QPushButton("Dark/Light Mode")
        h0_layout.addWidget(self.toggle_button)
        self.toggle_button.clicked.connect(self.toggle_mode)
        
        # Horizontal layout for request buttons (Pushbuttons-> Code gives their meanings no comments needed)
        h1_layout = QHBoxLayout() 
        
        self.im160x120 = QPushButton("Image : 160x120")
        h1_layout.addWidget(self.im160x120)
        self.im160x120.pressed.connect(self.image160x120info)
        self.im160x120.clicked.connect(self.image160x120)
        
        self.im320x240 = QPushButton("Image : 320x240")
        h1_layout.addWidget(self.im320x240)
        self.im320x240.pressed.connect(self.image320x240info)
        self.im320x240.clicked.connect(self.image320x240)
        
        self.im640x480 = QPushButton("Image : 640x480")
        h1_layout.addWidget(self.im640x480)
        self.im640x480.pressed.connect(self.image640x480info)
        self.im640x480.clicked.connect(self.image640x480)
        
        self.gyrodata = QPushButton("Gyroscope Data")
        h1_layout.addWidget(self.gyrodata)
        self.gyrodata.pressed.connect(self.gyromsg)            
        self.gyrodata.clicked.connect(self.gyro)
        
        layout = QVBoxLayout() # overall vertical layout
        central_widget.setLayout(layout)
        
        #Comments For user
        self.serial_port_label = QLabel("WELCOME TO SATVIEW v1.0.\n\nFirst you need to connect the device to PC (USB) .\n\nSelect Serial Port:")
        layout.addWidget(self.serial_port_label)
        
        self.port_combobox = QComboBox() # To select correct comport from available comports 
        layout.addWidget(self.port_combobox)
        
        layout.addLayout(h0_layout) # connetion control layout attached here
        
        self.verify_display = QTextEdit(self) # To Show Connection status in between the device and PC.
        self.verify_display.setReadOnly(True)
        layout.addWidget(self.verify_display)
        
        self.buttonsetlabel = QLabel("Click on required Data:") # Label for user
        layout.addWidget(self.buttonsetlabel)
        
        layout.addLayout(h1_layout) # request button layout attached here
        
        self.status_label = QLabel('Status Report:') # This displays what you requested.
        layout.addWidget(self.status_label)
        self.status_display = QTextEdit(self)
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)
        
        self.displayrx_label = QLabel('Received Text Data:') # Displays received data or message for images.
        layout.addWidget(self.displayrx_label)
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

        self.bottom_label = QLabel('Wait until the Red Blinking of the device is finished.\nImages are automatically viewed and stored.\nYou can check the directory of this app to locate saved data and images in a folder named with relevant date & time.\n\nALL RIGHTS RESERVED.\nKUSHAN DHANUSHKA') # Info to User.
        layout.addWidget(self.bottom_label)
        
        self.linklabel = QLabel("self")
        self.linklabel.setOpenExternalLinks(True)  # Allow opening external links
        self.linklabel.setText('<a href="https://dhanushkakush@gmail.com">Contact for more details</a>')
        layout.addWidget(self.linklabel)
        
        
        # title of the window opend
        self.setWindowTitle("SATVIEW")
        self.setGeometry(100, 100, 400, 300)
        
        # to update comport list
        self.update_port_list()
        
#@Slot() is used to specify that a Python method should be treated as a Qt slot. A slot is a function that can be connected to a Qt signal.

    @Slot()   # to update comport list
    def update_port_list(self):
        self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combobox.addItem(port.device)
            
    @Slot() # to connet with the selected comport
    def connect_serial(self):
        self.port_name = self.port_combobox.currentText()
        infostr = "Connected to "+str(self.port_name)+"\n"
        self.verify_display.insertPlainText(infostr)
        self.scrollTextvf()
        if self.port_name:
            self.serial = serial.Serial(self.port_name, 9600)  # Adjust baud rate as needed
            self.serial.timeout = 0.1  # Set a timeout for reading data (Not much needed)
        
        # Check the Connectivity of the SAT    
        self.serial.write(bytes("0", 'utf-8'))
        value = 0
        tmeasure1 = time.time()
        while value == 0 :
            data1 = str(self.serial.readline().decode('ascii'))
            if data1:
                self.verify_display.insertPlainText(data1 + "\n")
                value +=1
            else:    
                tmeasure2 = time.time()
                if (tmeasure2-tmeasure1) >5:
                    self.verify_display.insertPlainText("No Connection From Satellite !.\n")
                    break
            
    @Slot() # to disconnet with the selected comport
    def disconnect_serial(self):
        infostr = "Disconnected from "+str(self.port_name)+"\n"
        self.verify_display.insertPlainText(infostr)
        self.scrollTextvf()
        if self.serial:
            self.serial.close()
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(True)
        

    @Slot() # Display the data recieved or image receiving confirmation messages.
    def receiveData(self,data):
        if data:
            self.text_display.insertPlainText(data)
            self.scrollTexttd()
            
    @Slot() # Auto-Scroll for Verification Display
    def scrollTextvf(self):
        scrollbar = self.verify_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @Slot() # Auto-Scroll for Status Display
    def scrollTextsd(self):
        scrollbar = self.status_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @Slot() # Auto-Scroll for Receive data Display
    def scrollTexttd(self):
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    @Slot() # info message - status
    def image160x120info(self):
        current_dateandtime = datetime.now()
        dateandtime = current_dateandtime.strftime("%Y-%m-%d %H:%M:%S")
        info = "Image @ 160x120 is requested @" + dateandtime + ".\n"
        self.status_display.insertPlainText(info)
        self.scrollTextsd()
    
    @Slot() # info message - status
    def image320x240info(self):
        current_dateandtime = datetime.now()
        dateandtime = current_dateandtime.strftime("%Y-%m-%d %H:%M:%S")
        info = "Image @ 320x240 is requested @" + dateandtime + ".\n"
        self.status_display.insertPlainText(info)
        self.scrollTextsd()
        
    @Slot() # info message - status
    def image640x480info(self):
        current_dateandtime = datetime.now()
        dateandtime = current_dateandtime.strftime("%Y-%m-%d %H:%M:%S")
        info = "Image @ 640x480 is requested @" + dateandtime + ".\n"
        self.status_display.insertPlainText(info)
        self.scrollTextsd()
        
    @Slot() # Function for requesting and recieving images
    def image160x120(self):
        self.serial.write(bytes("1", 'utf-8'))
        self.image1(self.imcount,20,self.folder_path)
        self.imcount += 1
        self.receiveData("Requested 160x120 image has been recieved !\n")
    
    @Slot() # Function for requesting and recieving images
    def image320x240(self):
        self.serial.write(bytes("2", 'utf-8'))
        self.image1(self.imcount,40,self.folder_path)
        self.imcount += 1
        self.receiveData("Requested 320x240 image has been recieved !\n")
    
    @Slot() # Function for requesting and recieving images
    def image640x480(self):
        self.serial.write(bytes("3", 'utf-8'))
        self.image1(self.imcount,100,self.folder_path)
        self.imcount += 1
        self.receiveData("Requested 640x480 image has been recieved !\n")
        
    @Slot() # This fucntion is used to gather data received and reconstruct the image and save it in the folder previously specified.
    def image1(self,imagecount,num,foldernm):
        difference = 0
        datastr = ''
        measure1 = time.time()
        
        while difference < num: # Waiting some time to recieve all data
        # Read data from the serial port
            data = self.serial.readline()
            data = data.hex()
            datanew = str(data)
            datastr = datastr + datanew # collect all hex typed data together
            measure2 = time.time()
            difference = measure2 - measure1
            
        # If all data received, Reconstruction happens
        if datastr:
            dataimg = datastr.upper()
            data = dataimg.strip()
            data = data.replace(' ', '')
            data = data.replace('\n', '')
            data = binascii.a2b_hex(data) # ascii to binary to HEX
            
            # Recreation and storing image
            file_path = os.path.join(foldernm, 'No.'+str(imagecount)+'image_recieved.jpg') 
            with open(file_path, 'wb') as image_file:
                image_file.write(data)
                
            # Viewing the image
            image_path = os.path.join(foldernm, 'No.'+str(imagecount)+'image_recieved.jpg')
            image = cv2.imread(image_path)
            cv2.imshow('Recieved Image_'+str(imagecount), image)
            
            datastr = '' # Not necessarily needed. For the sake of convienience only.
            
    @Slot() # info message - status
    def gyromsg(self):
        current_dateandtime = datetime.now()
        dateandtime = current_dateandtime.strftime("%Y-%m-%d %H:%M:%S")
        info = "Gyro Data (Position, Velocity, Acceleration & Temperature) are requested @" + dateandtime + ".\n"
        self.status_display.insertPlainText(info)
        self.scrollTextsd()
        
    @Slot() # Function for recieve and dispaly and store Gyroscope data. 
    def gyro(self):
        
        self.serial.write(bytes("4", 'utf-8'))
        
        self.text_display.insertPlainText("Gyro Data (Position, Velocity, Acceleration & Temperature):\n")
        
         
        current_dateandtime = datetime.now()
        dateandtime = current_dateandtime.strftime("%Y-%m-%d--%H:%M:%S")
        with open(self.file_path, "a") as file:
                    file.write(dateandtime + "\n") # To store recieved time.
        term = 0
        tmeasure1 = time.time()
        while term < 3: # give enough time to print all required lines seperately
            data = str(self.serial.readline().decode('ascii'))
            if data:
                self.receiveData(data)
                with open(self.file_path, "a") as file: # To store recieved gyro data.
                    file.write(data)
                term += 1 
                 
            else:    
                tmeasure2 = time.time()
                if (tmeasure2-tmeasure1) >10:
                    self.receiveData("Time is up!. It seems connection is failed. Try again Later.\n")
                    break
    
    # Below snippets to DARK/LIGHT theme switching
    # Light mode is the default one.
    @Slot()
    def toggle_mode(self):
        if self.mode == "light":
            self.set_dark_mode()
        else:
            self.set_light_mode()

    @Slot()
    def set_light_mode(self):
        self.mode = "light"
        self.setStyleSheet("")  # Clear the style sheet to use the default style

    @Slot()
    def set_dark_mode(self): # DARK MODE
        self.mode = "dark"
        # Define a dark mode style sheet
        dark_mode_stylesheet = """
            QMainWindow {
                background-color: #333333;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #000000;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #0055A4;
            }
            QLabel {
                color: #FFFFFF;
            }
            QTextEdit{
                background-color: #333333;
                color: #FFFFFF;
            }
            QComboBox{
                background-color: #333333;
                color: #FFFFFF;
            }
        """
        self.setStyleSheet(dark_mode_stylesheet) 
               
if __name__ == '__main__': # Main call for clss >> REFER QTPYTHON
    app = QApplication(sys.argv)
    window = SerialMonitor()
    window.show()
    sys.exit(app.exec_())
