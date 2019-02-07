import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

arcpy.env.workspace = 'D:\MultimodalNetwork'

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

# global variables
network_file_geodatabase = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb'
utrans_roads = 'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Centerlines_Edit\UTRANS.TRANSADMIN.Roads_Edit'
utrans_trails =  'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Trails'
fifty_sites_1mile = 'D:\MultimodalNetwork\MultimodalScriptData.gdb\FiftySites_1mile_Bingham'
fgdb_dataset_name = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset'
bike_ped_auto = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto'


def main():

    # create new fgdb
    print(network_file_geodatabase)
    arcpy.CreateFileGDB_management('D:\MultimodalNetwork', 'MM_NetworkDataset_' + strDate +  '.gdb')

    # create dataset in the fgdb
    arcpy.CreateFeatureDataset_management(network_file_geodatabase, 'NetworkDataset', utrans_roads)

    # create new feature class in the fgdb
    arcpy.CreateFeatureclass_management(fgdb_dataset_name, "BikePedAuto", "POLYLINE", 
                                        'D:\MultimodalNetwork\MultimodalScriptData.gdb\BikePedAuto_template', "DISABLED", "DISABLED", 
                                        utrans_roads)

    # create a list of fields for the BikePedAuto feature class 
    #bike_ped_auto_fields = [f.name for f in arcpy.ListFields(bike_ped_auto)]
    #print bike_ped_auto_fields

    ## import roads data into network dataset ##
    utrans_centerlines_for_network = get_IntersectedSouceData(fifty_sites_1mile)
    import_RoadsIntoNetworkDataset(utrans_centerlines_for_network)

    ## import trails data into network dataset ##
    # utrans_trails_for_network = get_IntersectedSouceData(fifty_sites_halfmile)
    # import_TrailsIntoNetworkDataset(utrans_trails_for_network)


def import_RoadsIntoNetworkDataset(intersected_roads):

    # create list of field names
    #                0        1          2           3        4        5         6             7           8  
    road_fields = ['NAME', 'ONEWAY', 'SPEED_LMT', 'PED_L', 'PED_R', 'BIKE_L', 'BIKE_R', 'SHAPE@LENGTH', 'SHAPE@']
    #                   0           1             2          3           4          5              6              7            8              9             10          11 
    network_fields = ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetork', 'PedNetwork', 'BikeNetwork', 'SHAPE@']

    # set up search cursors to select and insert data between feature classes
    with arcpy.da.SearchCursor(intersected_roads, road_fields) as search_cursor, arcpy.da.InsertCursor(bike_ped_auto, network_fields) as insert_cursor:
        # itterate though the intersected utrans road centerline features
        for utrans_row in search_cursor:

            # create the network dataset values
            source_data = 'RoadCenterlines'
            auto_network = 'Y'
        
            # bike network
            bike_network = 'N'
            bike_l = utrans_row[5]
            bike_r = utrans_row[6]
            if HasFieldValue(bike_l) or HasFieldValue(bike_r):
                bike_network = 'Y'
        
            # ped network (it is assumed that anything other than 'prohibited', ped is allowed)
            ped_network = 'Y'
            ped_l = utrans_row[3]
            ped_r = utrans_row[4]
            if HasFieldValue(ped_l) or HasFieldValue(ped_r):
                if ped_l == 'Prohibited' or ped_r == 'Prohibited':
                    ped_network = 'N'

            # convert meters to miles
            miles = utrans_row[7] * 0.000621371
            miles = round(miles, 10)
            oneway = ''
            if utrans_row[1] == '0':
                oneway = "B"
            if utrans_row[1] == '1':
                oneway = "TF"
            if utrans_row[2] == '2':
                oneway = "FT"

            # transfer the speed value
            speed_lmt = utrans_row[2]

            # calculate the time fields
            drive_time = (miles / speed_lmt) * 60
            ped_time = (miles / 3.1) * 60
            bike_time = (miles / 9.6) * 60

            # create a list of values that will be used to construct new row
            insert_row_values = [(utrans_row[0], miles, oneway, source_data, speed_lmt, drive_time, ped_time, bike_time, auto_network, ped_network, bike_network, utrans_row[8])]
            print insert_row_values

            # insert the new row with the list of values
            for insert_row in insert_row_values:
                insert_cursor.insertRow(insert_row)

        
def import_TrailsIntoNetworkDataset():
    test = "hi"
    # more to come

# intersect utrans roads or trails that fall within the 50 site buffers (.5 or 1 mile)
def get_IntersectedSouceData(bufferSize):
    # use the .5 or 1 mile fifty sites buffers to create a select by location on the MMP data
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

    return 'utransRoads_lyr'


# check if field has a valid value (not empty string or null)
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


if __name__ == "__main__":
    # execute only if run as a script
    main()