# Change in_csv, lat, long, List, Filename_start, Filename_end between ###################
import os, sys, subprocess, csv, multiprocessing, re
from glob import glob
import numpy as np
import pandas as pd
import random as rd
import gdal
import shutil
from osgeo import osr
from osgeo import gdal_array
from threading import Thread
from tqdm import tqdm
from line_profiler import LineProfiler
tifDriver = gdal.GetDriverByName('GTiff')
tifDriver.Register()
import datetime
import os

t1 = datetime.datetime.now()
print(t1)
##########################################################################################################
### Add location of csv 
in_csv = './test.csv'
### Add column number for lat long position
latitude = 0
longitude = 1
### List the s3 bucket files with vsis3 (all same projection), make a list that the program runs through
List = []
### Use to specify the name of the columns [first letter:-4] removes folder path and end .tif
filename_start = 28
filename_end = -4
### Can change bottom code for line profiler    
##########################################################################################################

print(in_csv)
print()
new_csv = in_csv[:-4] + "1" + ".csv"
shutil.copy(in_csv, new_csv)
in_csv = new_csv
outFile = in_csv
rm_csv = in_csv

def GetGeoInfo(SourceDS):
	"""
	Take raster image as input and returns various properties
	Args:
		image file                                      input map image

	Return:
		image size with column and row numbers,
		geotransformation information
		projection information
		image data type
		count of bands in the image
	"""
	#NDV             = SourceDS.GetRasterBand(1).GetNoDataValue()
	xsize           = SourceDS.RasterXSize
	ysize           = SourceDS.RasterYSize
	bands           = SourceDS.RasterCount
	GeoT            = SourceDS.GetGeoTransform()
	proj            = SourceDS.GetProjection()
	DataType        = SourceDS.GetRasterBand(1).DataType
	return xsize, ysize, GeoT, proj, DataType, bands
def extValue(src_filename, in_csv, outFile, type):

	src_ds=gdal.Open(src_filename)

	xsize, ysize, gt, proj, DataType, bands = GetGeoInfo(src_ds)
	print("Extent is:       ", xsize, ysize)

	with open(outFile, 'w',newline = '') as csvfile:
		out_File = csv.writer(csvfile, doublequote= False,escapechar=',', quoting=csv.QUOTE_NONE)
		#out_File.writerow(HList)
		#Convert from map to pixel coordinates.
		#Only works for geotransforms with no rotation.
		with open(in_csv) as csvRead:
			csvLs = csv.reader(csvRead, delimiter= ',')
			header_of_new_col = src_filename[filename_start:filename_end]
			print("Column name is: ", header_of_new_col)

			#for row in csvLs:
				#for i, line in enumerate(csvLs):
			#out_File.append(header_of_new_col)
			#csvLs.append(header_of_new_col)
			#next(csvLs)
			for i, line in enumerate(csvLs):
				if i == 0:
					line.append(header_of_new_col)
					out_File.writerow(line)
				else:
					mx = float(line[longitude])
					my = float(line[latitude])
					px = int((mx - gt[0]) / gt[1]) #x pixel
					py = int((my - gt[3]) / gt[5]) #y pixel
					# loop through the bands
					if type.upper() == 'SINGLE':
						#line = [str(mx),str(my)]
						line = line
					elif type.upper() == 'TREND':
						line = [str(line[0]),str(mx),str(my)]
					elif type.upper() == 'MERGE':
						line = [str(line[3]),str(line[0]),str(line[4])]

					for i in range(1,bands+1):
						band = src_ds.GetRasterBand(i) # 1-based index
						# read data and add the value to the string
						data = band.ReadAsArray(px, py, 1, 1)
						#print(data)
						line.append(str(data[0,0]))
						#line.append(str(data))
						#print(line)
					out_File.writerow(line)
			print("\n")
            
# reads through lists and sends to extValue
for file in List:
    print(datetime.datetime.now())
    src_filename = file
    print("File path is: ", file)
    outFile = outFile[:-4] + "1" + ".csv"
    ### Line Profiler
    #lp = LineProfiler()
    #lp_wrapper = lp(extValue)
    #lp_wrapper(src_filename, in_csv, outFile, "single")
    #lp.print_stats()    
    extValue(src_filename, in_csv, outFile, "single")
    del_csv = in_csv
    os.remove(del_csv)
    in_csv = outFile
    
t2 = datetime.datetime.now()
time = t2 -t1
print("Total time for processing is: ", time)