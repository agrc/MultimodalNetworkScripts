import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

#arcpy.env.workspace = 'D:\MultimodalNetwork'

#### User Note ####: change dates for fgdb to current dataset (ctrl + f for "#### Note ####:")
transit_route_source = r'D:\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitRoutes' #### Note ####: change transit data date (if it's been updated)

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

# global variables
network_file_geodatabase = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb'
arcpy.env.workspace = network_file_geodatabase
utrans_roads = 'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Centerlines_Edit\UTRANS.TRANSADMIN.Roads_Edit'
utrans_trails =  'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Trails'
fifty_sites_1mile = 'D:\MultimodalNetwork\MultimodalScriptData.gdb\FiftySites_1mile'
fifty_sites_halfmile = 'D:\MultimodalNetwork\MultimodalScriptData.gdb\FiftySites_halfmile'
fgdb_dataset_name = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset'
bike_ped_auto = 'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto'


# main function
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

    ## -either- import roads data into network dataset by using spatial query ##
    utrans_centerlines_for_network = get_SouceDataUsingSpatialQuery(fifty_sites_1mile, utrans_roads, "Roads")
    ## -or- import roads data into network dataset by using definition query ##
    #where_clause_roads = r"ZIPCODE_L = '84047' or ZIPCODE_R = '84047'"
    #utrans_centerlines_for_network = get_SourceDataUsingDefQuery(where_clause_roads, utrans_roads, "Roads")
    # import the roads into network dataset
    import_RoadsIntoNetworkDataset(utrans_centerlines_for_network)

    ## -either- import trails data into network dataset by using spatial query ##
    utrans_trails_for_network = get_SouceDataUsingSpatialQuery(fifty_sites_1mile, utrans_trails, "Trails")
    ## -or- import trails data into network dataset by using a definition query ##
    #where_clause_trails = r"Status = 'EXISTING' and TransNetwork = 'Yes'"
    #utrans_trails_for_network = get_SourceDataUsingDefQuery(where_clause_trails, utrans_trails, "Trails")

    # import the trails into network dataset
    import_TrailsIntoNetworkDataset(utrans_trails_for_network)

    # import transit route data (the transit stops get added in the create_connectors.py file, after they've been exploded to single part)
    print "import the transit routes"
    importTransitRoutes()

    # export out each transit group (from BikePedAuto) to a separate feature class in the network dataset
    print "creating separate bike network feature class"
    arcpy.FeatureClassToFeatureClass_conversion(bike_ped_auto, fgdb_dataset_name, 'BikeNetwork', "BikeNetwork = 'Y'")
    print "creating separate ped network feature class"
    arcpy.FeatureClassToFeatureClass_conversion(bike_ped_auto, fgdb_dataset_name, 'PedNetwork', "PedNetwork = 'Y'")
    print "creating separate auto network feature class"
    arcpy.FeatureClassToFeatureClass_conversion(bike_ped_auto, fgdb_dataset_name, 'AutoNetwork', "AutoNetwork = 'Y'")

    print "rallyup_network_data.py script is done!"


# this function imports the user-defined utrans roads into the the netork dataset feature class 
def import_RoadsIntoNetworkDataset(utrans_roads_to_import):
    # create list of field names
    #                   0          1         2           3        4        5         6             7           8  
    road_fields = ['FULLNAME', 'ONEWAY', 'SPEED_LMT', 'PED_L', 'PED_R', 'BIKE_L', 'BIKE_R', 'SHAPE@LENGTH', 'SHAPE@']
    #                   0           1             2          3           4          5              6              7            8              9             10              11             12
    network_fields = ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetwork', 'PedNetwork', 'BikeNetwork', 'ConnectorNetwork', 'SHAPE@']

    # set up search cursors to select and insert data between feature classes
    with arcpy.da.SearchCursor(utrans_roads_to_import, road_fields) as search_cursor, arcpy.da.InsertCursor(bike_ped_auto, network_fields) as insert_cursor:
        # itterate though the intersected utrans road centerline features
        for utrans_row in search_cursor:

            # create the network dataset values
            source_data = 'RoadCenterlines'
            auto_network = 'Y'
            connector_network = 'N'

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
            insert_row_values = [(utrans_row[0], miles, oneway, source_data, speed_lmt, drive_time, ped_time, bike_time, auto_network, ped_network, bike_network, connector_network, utrans_row[8])]
            print insert_row_values

            # insert the new row with the list of values
            for insert_row in insert_row_values:
                insert_cursor.insertRow(insert_row)

        
# this function imports the user-defined utrans trails into the the netork dataset feature class 
def import_TrailsIntoNetworkDataset(utrans_trails_to_import):
    # create list of field names
    #                    0                1                 2            3 
    trail_fields = ['PrimaryName', 'DesignatedUses', 'SHAPE@LENGTH', 'SHAPE@']
    #                   0           1             2          3           4          5              6              7            8              9             10                11            12
    network_fields = ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetwork', 'PedNetwork', 'BikeNetwork', 'ConnectorNetwork', 'SHAPE@']

    # set up search cursors to select and insert data between feature classes
    with arcpy.da.SearchCursor(utrans_trails_to_import, trail_fields) as search_cursor, arcpy.da.InsertCursor(bike_ped_auto, network_fields) as insert_cursor:
        # itterate though the intersected utrans road centerline features
        for utrans_row in search_cursor:

            # create the network dataset values
            source_data = 'Trails'
            auto_network = 'N'
            connector_network = 'N'
            drive_time = None
            speed_lmt = None
            oneway = ''

            # populate bike and ped netork values
            designated_use = ''
            bike = ''
            ped_network = '' 
            # domains for this field are: ['Bike', 'Pedestrian', 'Multiuse']
            if HasFieldValue(utrans_row[1]):
                designated_use = utrans_row[1]
                
            if designated_use == 'Bike':
                bike_network = 'Y'
                ped_network = 'N'
            elif designated_use == 'Pedestrian':
                bike_network = 'N'
                ped_network = 'Y'
            elif designated_use == 'Multiuse':
                bike_network = 'Y'
                ped_network = 'Y'
            else:
                bike_network = '?'
                ped_network = '?'

            # convert meters to miles
            miles = utrans_row[2] * 0.000621371
            miles = round(miles, 10)

            # calculate the time fields
            ped_time = (miles / 3.1) * 60
            bike_time = (miles / 9.6) * 60

            # create a list of values that will be used to construct new row
            insert_row_values = [(utrans_row[0], miles, oneway, source_data, speed_lmt, drive_time, ped_time, bike_time, auto_network, ped_network, bike_network, connector_network, utrans_row[3])]
            print insert_row_values

            # insert the new row with the list of values
            for insert_row in insert_row_values:
                insert_cursor.insertRow(insert_row)


# this function returns either utrans roads or trails that intersect a specified boundary (ex: 50 sites buffer polygon) 
def get_SouceDataUsingSpatialQuery(spatial_boundary, utransFeatureClass, source):
    # remove referernce of any feature layers from possible previous function run
    if arcpy.Exists('spatialSelectPolygon_lyr'):
        arcpy.Delete_management('spatialSelectPolygon_lyr')
    if arcpy.Exists('utransIntersected_lyr'):
        arcpy.Delete_management('utransIntersected_lyr')

    # use the .5 or 1 mile fifty sites buffers to create a select by location on the MMP data
    arcpy.MakeFeatureLayer_management(spatial_boundary, 'spatialSelectPolygon_lyr')

    # make feature layer of utrans data (but, also use a where clause if it's trails dataset, to limit the segments to transportation trails only)
    if source == "Roads":
        arcpy.MakeFeatureLayer_management(utransFeatureClass, 'utransIntersected_lyr', r"CARTOCODE not in (99, 15, 14)")
    if source == "Trails":
        arcpy.MakeFeatureLayer_management(utransFeatureClass, 'utransIntersected_lyr', r"Status = 'EXISTING' and TransNetwork = 'Yes'")

    # instersect the utrans data with the fifty site buffers
    arcpy.SelectLayerByLocation_management('utransIntersected_lyr', 'intersect', 'spatialSelectPolygon_lyr')
    
    # make new feature layer from the intersected utrans data
    matchcount = int(arcpy.GetCount_management('utransIntersected_lyr')[0]) 
    if matchcount == 0:
        print('no features matched spatial and attribute criteria')
    else:
        intersected_roads = arcpy.CopyFeatures_management('utransIntersected_lyr', 'D:\MultimodalNetwork\MultimodalScratchData.gdb\utransIntersected' + source + '_' + strDate)
        #print('{0} cities that matched criteria written to {0}'.format(matchcount, utrans_IntersectedRoads))

    return 'utransIntersected_lyr'


# this function returns either utrans roads or trails that satisfy the specified definition query (ex: within a county or zipcode)
def get_SourceDataUsingDefQuery(where_clause, utransFeatureClass, source):
    # remove referernce to the feature layer from possible previous function run
    if arcpy.Exists('utransQueried_lyr'):
        arcpy.Delete_management('utransQueried_lyr')

    # make feature layer of utrans data
    if source == "Roads":
        arcpy.MakeFeatureLayer_management(utransFeatureClass, 'utransQueried_lyr', where_clause)
    if source == "Trails":
        arcpy.MakeFeatureLayer_management(utransFeatureClass, 'utransQueried_lyr', where_clause)

    # make new feature layer from the intersected utrans data
    matchcount = int(arcpy.GetCount_management('utransQueried_lyr')[0]) 
    if matchcount == 0:
        print('no features matched spatial and attribute criteria')
    else:
        intersected_roads = arcpy.CopyFeatures_management('utransQueried_lyr', 'D:\MultimodalNetwork\MultimodalScratchData.gdb\utransWhereClause' + source + '_' + strDate)
        #print('{0} cities that matched criteria written to {0}'.format(matchcount, utrans_IntersectedRoads))

    return 'utransQueried_lyr'

    
# this function checks if the field value has a valid value (that's it's not just an empty string or null value)
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


def importTransitRoutes():
    # import the transit routes feature class
    # transit_route_source = r'D:\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitRoutes' #### Note ####: change transit data date (if it's been updated)
    arcpy.FeatureClassToFeatureClass_conversion(transit_route_source, r'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb' + '\NetworkDataset', 'TransitRoutes')
    transit_routes_network_dataset =  r'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb' + '\NetworkDataset\TransitRoutes'   

    # add miles field
    arcpy.AddField_management(transit_routes_network_dataset, "Length_Miles", "DOUBLE", "", "", "", "", "NULLABLE")
    # convert meters to miles
    # calc newly-created mile values to the miles field
    arcpy.CalculateField_management(transit_routes_network_dataset, field="Length_Miles", expression="(!Shape_Length! * 0.000621371)", expression_type="PYTHON_9.3")

    # add transit time field
    arcpy.AddField_management(transit_routes_network_dataset, "TransitTime", "DOUBLE", "", "", "", "", "NULLABLE")

    # calc values to miles and transit time fields
    # light-rail is typically 17.2 mph
    # commuter rail is typically 30 mph
    # for bus, use 16.9 mph + 18 sec for stop + route length.  for more info see Problem/Solution: https://en.wikibooks.org/wiki/Fundamentals_of_Transportation/Transit_Operations_and_Capacity
    # to use these options i'll have to use an update cursor and loop through each route to assign the correct value
    # for not just calc all the routes to the light-rail speed
    arcpy.CalculateField_management(transit_routes_network_dataset, field="TransitTime", expression="((!Shape_Length! * 0.000621371) / 17.2) * 60", expression_type="PYTHON_9.3")
     


if __name__ == "__main__":
    # execute only if run as a script
    main()