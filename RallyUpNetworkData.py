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
# fgdb fc name
bike_ped_auto = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto' 
bike_ped_auto_fields = [f.name for f in arcpy.ListFields(bike_ped_auto)]
print bike_ped_auto_fields


# append trail and road features
# append roads
# create an expression with proper delimiters
expression = r"ZIPCODE_L = '84047' or ZIPCODE_R = '84047'"
road_fields = ['NAME', 'ONEWAY', 'SPEED_LMT', 'ZIPCODE_L', 'ZIPCODE_R', 'SHAPE@LENGTH', 'SHAPE@']

# Create a search cursor using an SQL expression
with arcpy.da.SearchCursor(utrans_roads, road_fields, where_clause=expression) as cursor:
    for row in cursor:
        # Print the name of the residential road
        #if row[0] is not None:
        #    print(row[0])
        #print(str(row[5]))
        

        # transfer the values to the network feature class
        # Open an InsertCursor and insert the new geometry
        #cursor = arcpy.da.InsertCursor(bike_ped_auto, ['SHAPE@'])
        #cursor = arcpy.da.InsertCursor(bike_ped_auto, bike_ped_auto_fields)
        #cursor.insertRow([row[6]])

        

        ## Delete cursor object
        #del cursor     

        # create the network dataset values
        # convert meters to miles
        miles = row[5] * 0.000621371
        miles = round(miles, 6)
        oneway = ''
        if row[1] == '0':
            oneway = "B"
        if row[1] == '1':
            oneway = "TF"
        if row[2] == '2':
            oneway = "FT"


        # A list of values that will be used to construct new rows
        insert_row_values = [(row[0], miles, oneway, row[6])]
        print insert_row_values

        # Open an InsertCursor
        insert_cursor = arcpy.da.InsertCursor(bike_ped_auto,
                                       ['Name', 'Length_Miles', 'Oneway', 'SHAPE@'])

        # Insert new rows that include the county name and a x,y coordinate
        #  pair that represents the county center
        for insert_row in insert_row_values:
            insert_cursor.insertRow(insert_row)

        # Delete cursor object
        del insert_cursor

        


# append trails


# calc fields (length and time and oneway)

