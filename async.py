import sys
import time
import random
import threading

def actuateSustainPedal(dir):
    """
    Thread trigger function for the sustain pedal - clockwise is UP, counter-clockwise is DOWN
    :param dir: direction to actuate the pedal - INT - 1 for UP, 0 for DOWN
    :return: None
    """
    if dir == 1:
        print("1")
        time.sleep(2)  # Time for sustain pedal to actuate - UP
        print("1")
    else:
        print("2")
        time.sleep(2)  # Time for sustain pedal to actuate - DOWN
        print("2")

def timer():
    print("3")
    act = threading.Thread(target=actuateSustainPedal, args=(0,))
    act.start()
    print("3")
    print("3")

timer()

"""
try:
	def runtime():
		for i in range(6):
			print(i+1)
			time.sleep(1)
		
	runtime()
except:
	def printer():
		return "damn"
	printer()
"""
