import sys
import time
import random
for i in range(4):
    filename="{}".format(str(i))
    fo = open(filename, "wb")
    time.sleep(5)
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
