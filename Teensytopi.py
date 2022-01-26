import serial
import time
time.sleep(20)

port="/dev/serial/usb-Teensyduino_USB_Serial_5214380-if00"
ser=serial.Serial(port,115200)
while True:
    print("Waiting for messages from arduino..")
    read_ser=ser.readline()
    print(read_ser)