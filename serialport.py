import serial
import time
import binascii

# Replace 'COM4' with the appropriate port name for your system
serial_port = 'COM4'
baud_rate = 9600
# Establish a connection to the serial port
ser = serial.Serial(serial_port, baud_rate, timeout=1)

#For image data
imcount = 1 #count the saved image

# Function for getting image
def imagerecv(num,dur):
    print("Image is requested.\nWaiting for Image!\nPlease Wait until blinking of USB module is ended.\nAfter that stay calm for few seconds.\nFinally, check the folder for image!!!")
    count = 1
    datastr = ''
    measure1 = time.time()
    measure2 = time.time()
    try:
        while count < 11:
            # Read data from the serial port
            data = ser.readline()
            data = data.hex()
            datanew = str(data)
            datastr = datastr + datanew
            if measure2 - measure1 >= dur:
                measure1 = measure2
                measure2 = time.time()
                count += 1
            else:
                measure2 = time.time()
                
        # If data received, print it
        if datastr:
            dataimg = datastr.upper()
            print(dataimg)
            data=dataimg.strip()
            data=data.replace(' ', '')
            data=data.replace('\n', '')
            data = binascii.a2b_hex(data)
            with open('No.'+str(num)+'image_recieved.jpg', 'wb') as image_file:
                image_file.write(data)
            datastr = ''
                
    # To close the serial port gracefully, use Ctrl+C to break the loop
    except KeyboardInterrupt:
        print("Closing the serial port.")
        ser.close()
        
# Function for getting Gyro data
def gyro():
    print("Gyro Data (Position, Velocity, Acceleration & Temperature):")
    print("")
    try:
        term = 0
        while term < 5: # give enough time to print all required lines seperately
            # Read data from the serial port
            data = str(ser.readline().decode('ascii'))
            term+=1
            # If data received, print it
            if data:
                print(data)
            
    # To close the serial port gracefully, use Ctrl+C to break the loop
    except KeyboardInterrupt:
        print("Closing the serial port.")
        ser.close()

# Main program
while True:
    print("Enter the relavant key to get the data required !\n1 = Image with Resolution - 160x120\n2 = Image with Resolution - 320x240\n3 = Image with Resolution - 640x480\n4 = Gyro Data (Position, Velocity, Acceleration & Temperature)\n5 = Location Data (GPS)")
    print()
    reqno = int(input("Enter the Key Here : ")) # Taking input from user
    ser.write(bytes(str(reqno), 'utf-8')) # Send that i/p to SAT
    
    if reqno == 1 :
        imagerecv(imcount,2) # Calling func. for receiving the image
        imcount +=1 # to rename in ascending order
        
    elif reqno == 2 :
        imagerecv(imcount,4) # Calling func. for receiving the image
        imcount +=1 # to rename in ascending order
        
    elif reqno == 3 :
        imagerecv(imcount,12) # Calling func. for receiving the image
        imcount +=1 # to rename in ascending order
        
    elif reqno == 4:
        gyro() # Calling func. for receiving the gyro data
            

    
