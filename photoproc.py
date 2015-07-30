#-*- coding: utf-8 -*-
#This program is for mass modification of images. 

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import time
from shutil import copyfile

def get_exif_data(image):
	"""
	This function gets the exit data off of an image. Please pass it an image file with associated EXIF data.
	"""
	exif_data = {}
	info = image._getexif()
	if info:
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			if decoded == "GPSInfo":
				gps_data = {}
				for t in value:
					sub_decoded = GPSTAGS.get(t, t)
					gps_data[sub_decoded] = value[t]

				exif_data[decoded] = gps_data
			else:
				exif_data[decoded] = value
	return exif_data

def _get_if_exist(data, key):
	"""
	Give me (data, key) and I will return data[key] if data is in key.
	"""
	if key in data:
		return data[key]
	return None

def _convert_to_degress(value):
	"""
	Convert to angle asmuth or some such? I'm not actually sure how these seconds to degrees whatnot work, but the math works. Thanks Jason Weston for that.
	"""
	0 = value[0][0]
	d1 = value[0][1]
	d = float(d0) / float(d1)

	m0 = value[1][0]
	m1 = value[1][1]
	m = float(m0) / float(m1)

	s0 = value[2][0]
	s1 = value[2][1]
	s = float(s0) / float(s1)

	return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
	"""
	If there's GPS data in exif data, this will return it in four arguments: lat, lon, gps_longitude, gps_latitude.
	If there isn't, the return is undefined.
	"""	
	lat = None
	lon = None
	if "GPSInfo" in exif_data:
		gps_info = exif_data["GPSInfo"]

		gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
		gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
		gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
		gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

		if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
			lat = _convert_to_degress(gps_latitude)
			if gps_latitude_ref != "N":
				lat = 0 - lat

			lon = _convert_to_degress(gps_longitude)
			if gps_longitude_ref != "E":
				lon = 0 - lon
	return lat, lon, gps_longitude, gps_latitude

def generateName(lat, lon):
	"""
	Given a latitude and a longitude, this returns a string that is the name formatted.
	"""
	return (str(lat[0][0]) + "." + str(lat[1][0]) + "." + str(lat[2][0])[0:2]+ "." + str(lat[2][0])[2:4] + "N" + "-" + str(lon[0][0]) + "." + str(lon[1][0]) + "." + str(lon[2][0])[0:2] + "." + str(lon[2][0])[2:4]  + "W.JPG")



def rename(name, indir, outdir):
	"""
	This function takes a file of a specific name from the input directory (indir) and writes it with the new name from generateName to the output directory (outdir).
	"""
	global num_taggless
	num_taggless = 0
	img = Image.open(indir + "/" + name)
	imgIn = open(indir + "/" +  name, 'r')
	data = get_exif_data(img)

	lon = get_lat_lon(data)[2]
	lat = get_lat_lon(data)[3]
	#print lon
	#print lat

	if lon != None:
		nameOfProcFile = generateName(lat, lon)
		#nameOfProcFile = str(lat[0][0]) + "." + str(lat[1][0]) + "." + str(lat[2][0])[0:2]+ "." + str(lat[2][0])[2:4] + "N" + "-" + str(lon[0][0]) + "." + str(lon[1][0]) + "." + str(lon[2][0])[0:2] + "." + str(lon[2][0])[2:4]  + "W.JPG"

	else:
		num_taggless = num_taggless + 1
		nameOfProcFile = "NoGPS.JPG"

	copyfile(indir + "/" + name, outdir + "/" + name[0:8] + " " +nameOfProcFile)
	imgIn.close()



indir = str(input("What's the name of the directory that your unprocessed pictures are in?"))
outdir = "Renamed " + indir 
if not os.path.exists(outdir): os.makedirs(outdir)
files = os.listdir(indir)
for elt in files:
	print str(elt)
	rename(str(elt), indir, outdir)
if num_taggless == 0:
	print "All of these photos have GPS data."
elif num_taggless == 1:
	print "One of the photos doesn't have GPS data."
else:
	print num_taggless + "photos dont have GPS data."
