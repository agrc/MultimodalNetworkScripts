import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year)


# create new fgdb
arcpy.CreateFileGDB_management("D:/MultimodalNetwork", "MM_NetworkDataset_" + strDate +  ".gdb")


# create dataset

# create new feature class

# add fields

# append trail and road features

# calc fields (length and time and oneway)

