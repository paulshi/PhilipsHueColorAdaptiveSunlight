import requests
import datetime
from config import *

class LastUpdate:
	def __init__(self):
		self.date = None
		self.sunrise_h = None
		self.sunrise_m = None
		self.sunset_h = None
		self.sunset_m = None

	def updateLastUpdate(self, date,sunrise_h,sunrise_m,sunset_h,sunset_m):
		self.date = date
		self.sunrise_h = sunrise_h
		self.sunrise_m = sunrise_m
		self.sunset_h = sunset_h
		self.sunset_m = sunset_m

	def getLastUpdate(self):
		return (self.sunrise_h, self.sunrise_m, self.sunset_h, self.sunset_m)

	def getLastUpdateDate(self):
		return self.date

weatherUndergroundUrl = "http://api.wunderground.com/api/"+weatherUnderGroundAPIKey+"/astronomy/q/"+zipCode+".json"

class ColorTemperatureChange:
	def __init__(self):
		self.lastUpdate = LastUpdate()

	def getColorTemperature(self,mode):
		# max range of philip hue color temperature setting
		maxRangeVal = 153.0
		minRangeVal = 500.0
		# which corresponds to
		maxRange = 6500.0 #K
		minRange = 2000.0 #K
		# My Setting 
		morningRange = 6500.0 #K
		nightRange = 3400.0 #K

		perKValueChnage = (abs(maxRangeVal -  minRangeVal) / abs(maxRange - minRange))
		myMorningVal = maxRangeVal + perKValueChnage*(maxRange - morningRange)
		myNightVal =  minRangeVal + perKValueChnage*(minRange - nightRange)

		# print int(myMorningVal)
		# print int(myNightVal)

		if mode == "hi":
			return int(myMorningVal)
		elif mode == "low":
			return int(myNightVal)
		else:
			return -1

	def determineHueStates(self):
		today = datetime.date.today()
		if self.lastUpdate.getLastUpdateDate() != today:
			#get sunrise and sunset from weather underground

			print ("getting new sunrise and sunset info from weather Underground for Today")
			r = requests.get(weatherUndergroundUrl)
			rjson = r.json()
			self.lastUpdate.updateLastUpdate( \
				today, \
				rjson['sun_phase']['sunrise']['hour'], \
				rjson['sun_phase']['sunrise']['minute'], \
				rjson['sun_phase']['sunset']['hour'], \
				rjson['sun_phase']['sunset']['minute'] \
			)
			

		currenttime = datetime.datetime.now();

		(sunrise_h, sunrise_m, sunset_h, sunset_m) = self.lastUpdate.getLastUpdate();

		#this makes sure that the time frame is always constructed form today's date
		reconstructed_sunrise_time = datetime.datetime(currenttime.year, currenttime.month, currenttime.day, int(sunrise_h), int(sunrise_m))
		reconstructed_sunset_time = datetime.datetime(currenttime.year, currenttime.month, currenttime.day, int(sunset_h), int(sunset_m))
		
		print "sunrise time: {}".format(reconstructed_sunrise_time)
		print "sunset time: {}".format(reconstructed_sunset_time)
		print "current time: {}".format(currenttime)

		flagA = currenttime > reconstructed_sunrise_time
		flagB =  currenttime > reconstructed_sunset_time

		if flagA and not flagB:
			return 1
		elif flagA and flagB:
			return 0
		elif not flagA and not flagB:
			return 0
		else:
			return -1

	def setHueMode(self):
		SunInfo = self.determineHueStates()
		if SunInfo==1:
			return "hi"
		elif SunInfo == 0:
			return "low"
		else:
			return "time logic error!"
