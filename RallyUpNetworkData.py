import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

def HasFieldValue(field_value):
    """ example: (row.STATUS) """
    if field_value is None:
        # the value is of NoneType
        return False
    else:
        _str_field_value = str(field_value)

        # value is not of NoneType
        if _str_field_value.isdigit():
            # it's an int
            if _str_field_value == "":
                return False
            else:
                return True
        else:
            # it's not an int
            if _str_field_value == "" or _str_field_value is None or _str_field_value.isspace():       
                return False
            else:
                return True


# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

arcpy.env.workspace = 'D:\MultimodalNetwork'

# get access to utrans roads and trails
utrans_roads = 'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Centerlines_Edit\UTRANS.TRANSADMIN.Roads_Edit'
utrans_trails =  'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Trails'
fifty_sites_1mile = 'D:\MultimodalNetwork\MultimodalScriptData.gdb\FiftySites_1mile_Bingham'

# create new fgdb
file_geodatabase = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb'
print(file_geodatabase)
arcpy.CreateFileGDB_management('D:\MultimodalNetwork', 'MM_NetworkDataset_' + strDate +  '.gdb')

# create dataset
arcpy.CreateFeatureDataset_management(file_geodatabase, 'NetworkDataset', utrans_roads)

# create new feature class
fgdb_dataset_name = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset'
arcpy.CreateFeatureclass_management(fgdb_dataset_name, "BikePedAuto", "POLYLINE", 
                                    'D:\MultimodalNetwork\MultimodalScriptData.gdb\BikePedAuto_template', "DISABLED", "DISABLED", 
                                    utrans_roads)
# fgdb fc name
bike_ped_auto = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto' 
bike_ped_auto_fields = [f.name for f in arcpy.ListFields(bike_ped_auto)]
print bike_ped_auto_fields


# append trail and road features
# append roads
# create an expression with proper delimiters
expression = r"ZIPCODE_L = '84047' or ZIPCODE_R = '84047'"

# use the 1 mile fifty sites buffers to create a select by location on the MMP data
arcpy.MakeFeatureLayer_management(fifty_sites_1mile, 'fiftySitesOneMile_lyr')
arcpy.MakeFeatureLayer_management(utrans_roads, 'utransRoads_lyr')
arcpy.SelectLayerByLocation_management('utransRoads_lyr', 'intersect', "fiftySitesOneMile_lyr")
# make new feature layer from the intersected, selected utrans roads
matchcount = int(arcpy.GetCount_management('utransRoads_lyr')[0]) 
if matchcount == 0:
    print('no features matched spatial and attribute criteria')
else:
    intersected_roads = arcpy.CopyFeatures_management('utransRoads_lyr', 'D:\MultimodalNetwork\MultimodalScratchData.gdb\utransIntersectedRoads_' + strDate)
    #print('{0} cities that matched criteria written to {0}'.format(matchcount, utrans_IntersectedRoads))

# Create a search cursor using an SQL expression
#                0        1          2           3        4        5         6             7           8  
road_fields = ['NAME', 'ONEWAY', 'SPEED_LMT', 'PED_L', 'PED_R', 'BIKE_L', 'BIKE_R', 'SHAPE@LENGTH', 'SHAPE@']
#with arcpy.da.SearchCursor(utrans_roads, road_fields, where_clause=expression) as cursor:
with arcpy.da.SearchCursor(intersected_roads, road_fields) as cursor:
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
        source_data = 'RoadCenterlines'
        auto_network = 'Y'
        
        # bike network
        bike_network = 'N'
        bike_l = row[5]
        bike_r = row[6]
        if HasFieldValue(bike_l) or HasFieldValue(bike_r):
            bike_network = 'Y'
        
        # ped network (it is assumed that anything other than 'prohibited', ped is allowed)
        ped_network = 'Y'
        ped_l = row[3]
        ped_r = row[4]
        if HasFieldValue(ped_l) or HasFieldValue(ped_r):
            if ped_l == 'Prohibited' or ped_r == 'Prohibited':
                ped_network = 'N'


        # convert meters to miles
        miles = row[7] * 0.000621371
        miles = round(miles, 10)
        oneway = ''
        if row[1] == '0':
            oneway = "B"
        if row[1] == '1':
            oneway = "TF"
        if row[2] == '2':
            oneway = "FT"

        # transfer the speed value
        speed_lmt = row[2]

        # calculate the time fields
        drive_time = (miles / speed_lmt) * 60
        ped_time = (miles / 3.1) * 60
        bike_time = (miles / 9.6) * 60


        # A list of values that will be used to construct new rows
        insert_row_values = [(row[0], miles, oneway, source_data, speed_lmt, drive_time, ped_time, bike_time, auto_network, ped_network, bike_network, row[8])]
        print insert_row_values

        # Open an InsertCursor
        insert_cursor = arcpy.da.InsertCursor(bike_ped_auto,
                                       ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetork', 'PedNetwork', 'BikeNetwork', 'SHAPE@'])

        # Insert new rows that include the county name and a x,y coordinate
        #  pair that represents the county center
        for insert_row in insert_row_values:
            insert_cursor.insertRow(insert_row)

        # Delete cursor object
        del insert_cursor

        


# append trails


# calc fields (length and time and oneway)

