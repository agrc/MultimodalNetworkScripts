import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

arcpy.env.workspace = 'D:\MultimodalNetwork'

# get access to utrans roads and trails
utrans_roads = 'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Centerlines_Edit\UTRANS.TRANSADMIN.Roads_Edit'
utrans_trails =  'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Trails'

# create new fgdb
file_geodatabase = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb'
print(file_geodatabase)
arcpy.CreateFileGDB_management('D:\MultimodalNetwork', 'MM_NetworkDataset_' + strDate +  '.gdb')

# create dataset
arcpy.CreateFeatureDataset_management(file_geodatabase, 'NetworkDataset', utrans_roads)

# create new feature class
fgdb_dataset_name = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset'
arcpy.CreateFeatureclass_management(fgdb_dataset_name, "BikePedAuto", "POLYLINE", 
                                    'D:\MultimodalNetwork\FeatureClassTemplate.gdb\BikePedAuto_template', "DISABLED", "DISABLED", 
                                    utrans_roads)

# add fields

# append trail and road features

# calc fields (length and time and oneway)

