#/usr/bin/python3

from gpiozero import Motor, OutputDevice
from time import sleep
from datetime import datetime as dt
from date_utils import right_now, subtract_days, date_str
from constants import *
import threading

IS_RUNNING = False
LAST_RUN = subtract_days(right_now(), 1)

class MotorUtil:
	def __init__(self):
		self.enable = OutputDevice(GPIO_PIN_ENABLE)
		self.motor = Motor(GPIO_PIN_FORWARD, GPIO_PIN_BACKWARD)

	def turn_motor_async(self, duration=MOTOR_DEFAULT_DURATION, speed=MOTOR_DEFAULT_SPEED, override=False):
		runner = threading.Thread(target=self.turn_motor, args=(duration,speed,override))
		runner.start()
		return

	def turn_motor(self, duration=MOTOR_DEFAULT_DURATION, speed=MOTOR_DEFAULT_SPEED, override=False):
		"""Turns a Pi motor for the specified duration."""
		global IS_RUNNING
		global LAST_RUN

		if IS_RUNNING:
			print("Already running!")
			return False

		if not override:
			current_date = right_now()
			if date_str(current_date) == date_str(LAST_RUN):
				print("Already ran in this minute, ignoring.")
				return False

		LAST_RUN = right_now()
		IS_RUNNING = True
		print(date_str(LAST_RUN))

		self.enable.on()
		self.motor.forward(speed)
		sleep(duration)
		self.enable.off()

		IS_RUNNING = False
		print("Motor going to idle.")
		return True
