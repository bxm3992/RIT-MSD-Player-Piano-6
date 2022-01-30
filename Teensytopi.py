
#dmesg | grep tty
#ls /dev/tty*


import serial
import time
time.sleep(10)

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    ser.reset_input_buffer()
    print("waiting")
    while True:
        if ser.in_waiting > 0:
            print("found message. Displaying.... ")
            line = ser.readline().decode('utf-8').rstrip()
            print(line)