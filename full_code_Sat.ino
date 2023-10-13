// Import the necessary libraries for the Satdemo
#include <SPI.h>
#include <SD.h>
#include <Adafruit_VC0706.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// RF, Cam :: USART
// SD :: SPI
// Gyro :: I2C

//Creatring objects
Adafruit_MPU6050 mpu;
Adafruit_VC0706 cam = Adafruit_VC0706(&Serial2);

void setup() {
  pinMode(PA4, OUTPUT);// For SD card
  pinMode(PB3, OUTPUT); // Indicator

  // Open serial communications and wait for port to open:
  Serial1.begin(9600); //RF
  
  if (!SD.begin(PA4)) { // SD initializtion
    Serial1.println("SD card initialization failed!");
    while (1);
  }
  delay(1000);
}

void camr(int PACKET_SIZE){
  delay(3000);
  digitalWrite(PB3, HIGH);
  if (! cam.takePicture())
    Serial1.println("Failed to snap!");

  // Create an image with the name IMAGExx.JPG
  char filename[13];
  strcpy(filename, "IMAGE01.JPG");
  for (int i = 0; i < 100; i++) {
    filename[5] = '0' + i / 10;
    filename[6] = '0' + i % 10;
    // create if does not exist, do not open existing, write, sync after write
    if (! SD.exists(filename)) {
      break;
    }
  }
  
  File imgFile = SD.open(filename, FILE_WRITE);
  uint16_t jpglen = cam.frameLength();
  int32_t time = millis();
  byte wCount = 0; // For counting # of writes
  while (jpglen > 0) {
    // read 32 bytes at a time;
    uint8_t *buffer;
    uint8_t bytesToRead = min(64, jpglen); // change 32 to 64 for a speedup but may not work with all setups!
    buffer = cam.readPicture(bytesToRead);
    imgFile.write(buffer, bytesToRead);
    if (++wCount >= 64) { // Every 2K, give a little feedback so it doesn't appear locked up
      //Serial.print('.');
      wCount = 0;
    }
    //Serial.print("Read ");  Serial.print(bytesToRead, DEC); Serial.println(" bytes");
    jpglen -= bytesToRead;
  }
  imgFile.close();
  time = millis() - time;
  delay (2000);
  
  // Open the image file.
  File imageFile = SD.open(filename,FILE_READ);

  // If the file opened successfully, start sending the data over the serial port as packets.
  if (imageFile) {

    // Get the size of the image file.
    int fileSize = imageFile.size();

    // Calculate the number of packets.
    int numberOfPackets = fileSize / PACKET_SIZE;

    // Create a buffer to store the data from the file.
    byte buffer[PACKET_SIZE];
    
    // Send the packets over the serial port.
    for (int i = 0; i < numberOfPackets; i++) {
      // Read the data from the file into the buffer.
      imageFile.read(buffer, PACKET_SIZE);

      // Send the packet over the serial port.
      Serial1.write(buffer, PACKET_SIZE);
      delay(10);
    }
    // Close the file.
    imageFile.close();

  } else {
    Serial1.println("Failed to open image file!");
  }
  digitalWrite(PB3, LOW); // off the indicator
}

void loop(){  
  if (Serial1.available()) {
    String req = Serial1.readString();
    delay(100);

    if (req == "0"){
      digitalWrite(PB3, HIGH);
      Serial1.print("Satellite is Connected Now !.");
      delay(50);
      digitalWrite(PB3, LOW);
    }

    if (req == "1") { 
      if (cam.begin()) {
      } else {
        Serial1.println("No camera found?");
        return;
      }
      char *reply = cam.getVersion();
      cam.setImageSize(VC0706_160x120);// Small
      cam.begin();
      camr(8);
    }
    
    if (req == "2") { 
      if (cam.begin()) {
      } else {
        Serial1.println("No camera found?");
        return;
      }
      char *reply = cam.getVersion();
      cam.setImageSize(VC0706_320x240);// Medium
      cam.begin();
      camr(8);
    }

    if (req == "3") { 
      if (cam.begin()) {
      } else {
        Serial1.println("No camera found?");
        return;
      }
      char *reply = cam.getVersion();
      cam.setImageSize(VC0706_640x480);// Large
      cam.begin();
      camr(8);
    }
    
    if (req == "4"){
      digitalWrite(PB3, HIGH);
      if (!mpu.begin()) {
        Serial1.print("No Gyro Sensor Found. !");
      }
      mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
      mpu.setGyroRange(MPU6050_RANGE_500_DEG);
      mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
      /* Get new sensor events with the readings */
      sensors_event_t a, g, temp;
      mpu.getEvent(&a, &g, &temp);
      /* Print out the values */
      Serial1.print("Acceleration X: ");
      Serial1.print(a.acceleration.x);
      Serial1.print(", Y: ");
      Serial1.print(a.acceleration.y);
      Serial1.print(", Z: ");
      Serial1.print(a.acceleration.z);
      Serial1.println(" m/s^2");

      Serial1.print("Rotation X: ");
      Serial1.print(g.gyro.x);
      Serial1.print(", Y: ");
      Serial1.print(g.gyro.y);
      Serial1.print(", Z: ");
      Serial1.print(g.gyro.z);
      Serial1.println(" rad/s");
      
      Serial1.print("Temperature: ");
      Serial1.print(temp.temperature);
      Serial1.println(" degC");
      digitalWrite(PB3, LOW);
    }
  }
}
