import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

#arcpy.env.workspace = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork'

#: Notes before running: verify data sources (local SGID data vs SGID data -- home vpn vs at work). Variables to check:
    # utrans_roads
    # utrans_trails

#### User Note ####: change dates for fgdb to current dataset (ctrl + f for "#### Note ####:")
transit_route_source = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitRoutes' #### Note ####: change transit data date (if it's been updated)

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year)

# global variables
# utrans_roads = 'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Centerlines_Edit\UTRANS.TRANSADMIN.Roads_Edit' #: use when not on VPN
# utrans_trails =  'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Trails_Paths' #: use when not on VPN
utrans_roads = 'C:\\Users\\gbunce\\Documents\\projects\\SGID\\local_sgid_data\\SGID_2020_07_27.gdb\\Roads' #: use when on VPN (update data)
utrans_trails =  'C:\\Users\\gbunce\\Documents\\projects\\SGID\\local_sgid_data\\SGID_2020_07_27.gdb\\TrailsAndPathways' #: use when on VPN (update data)

network_file_geodatabase = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb'
arcpy.env.workspace = network_file_geodatabase
fifty_sites_1mile = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScriptData.gdb\FiftySites_1mile'
fifty_sites_halfmile = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScriptData.gdb\FiftySites_halfmile'
counties_mmp = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScriptData.gdb\Counties_MMP'
fgdb_dataset_name = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset'
bike_ped_auto = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto'


# main function
def main():
    # create new fgdb
    print(network_file_geodatabase)
    arcpy.CreateFileGDB_management('C:\Users\gbunce\Documents\projects\MultimodalNetwork', 'MM_NetworkDataset_' + strDate +  '.gdb')

    # create dataset in the fgdb
    arcpy.CreateFeatureDataset_management(network_file_geodatabase, 'NetworkDataset', utrans_roads)

    # create new feature class in the fgdb
    arcpy.CreateFeatureclass_management(fgdb_dataset_name, "BikePedAuto", "POLYLINE", 
                                        'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScriptData.gdb\BikePedAuto_template', "DISABLED", "DISABLED", 
                                        utrans_roads)

    # create a list of fields for the BikePedAuto feature class 
    #bike_ped_auto_fields = [f.name for f in arcpy.ListFields(bike_ped_auto)]
    #print bike_ped_auto_fields

    ##: -either- import roads data into network dataset by using spatial query ##
    utrans_centerlines_for_network = get_SouceDataUsingSpatialQuery(counties_mmp, utrans_roads, "Roads")
    ##: -or- import roads data into network dataset by using definition query ##
    #where_clause_roads = r"ZIPCODE_L = '84108' or ZIPCODE_R = '84108'"
    #utrans_centerlines_for_network = get_SourceDataUsingDefQuery(where_clause_roads, utrans_roads, "Roads")
    
    # import the roads into network dataset
    import_RoadsIntoNetworkDataset(utrans_centerlines_for_network)

    ## -either- import trails data into network dataset by using spatial query ##
    utrans_trails_for_network = get_SouceDataUsingSpatialQuery(counties_mmp, utrans_trails, "Trails")
    ## -or- import trails data into network dataset by using a definition query ##
    #where_clause_trails = r"Status = 'EXISTING' and TransNetwork = 'Yes'"
    #utrans_trails_for_network = get_SourceDataUsingDefQuery(where_clause_trails, utrans_trails, "Trails")

    # import the trails into network datasetutrans_trails
    import_TrailsIntoNetworkDataset(utrans_trails_for_network)

    # import transit route data (the transit stops get added in the create_connectors.py file, after they've been exploded to single part)
    print "import the transit routes"
    importTransitData()

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
    # get # Get the dictionary of codes and descriptions for cartocode field, for transfering descriptions to RoadClass network field
    gdb = r'Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde'
    desc_lu = [d.codedValues for d in arcpy.da.ListDomains(gdb) if d.name == 'CVDomain_CartoCode'][0]
    
    # create list of field names
    #                   0          1         2           3        4        5         6            7           8           9             10           11  
    road_fields = ['FULLNAME', 'ONEWAY', 'SPEED_LMT', 'PED_L', 'PED_R', 'BIKE_L', 'BIKE_R', 'CARTOCODE', 'DOT_AADT', 'DOT_AADTYR', 'SHAPE@LENGTH', 'SHAPE@']
    #                   0           1             2          3           4          5              6              7            8              9             10              11                 12        13       14        15         16         17
    network_fields = ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetwork', 'PedNetwork', 'BikeNetwork', 'ConnectorNetwork', 'RoadClass', 'AADT', 'AADT_YR', 'BIKE_L', 'BIKE_R', 'SHAPE@']

    # set up search cursors to select and insert data between feature classes (define two cursor on next line: search_cursor and insert_cursor)
    with arcpy.da.SearchCursor(utrans_roads_to_import, road_fields) as search_cursor, arcpy.da.InsertCursor(bike_ped_auto, network_fields) as insert_cursor:
        # itterate though the intersected utrans road centerline features
        for utrans_row in search_cursor:

            # create the network dataset values
            source_data = 'RoadCenterlines'
            auto_network = 'Y'
            connector_network = 'N'
            road_class = ''
            aadt = 0
            aadt_yr = ''

            # bike network
            bike_network = 'N'
            bike_l = utrans_row[5]
            bike_r = utrans_row[6]
            cartocode = utrans_row[7]
            #bike_facilities = ['1','1A','1B','1C','2','2A','2B'] # only roads with bike lanes or cycle tracks are added to the bike network (no shared lanes)
            #if bike_l in bike_facilities and bike_r in bike_facilities:
            #    bike_network = 'Y'            
            if HasFieldValue(bike_l) or HasFieldValue(bike_r):
                bike_network = 'Y'
            if cartocode not in ['1', '2', '4', '7']: #: also mark local roads as bike network for wider connectivity
                bike_network = 'Y'
        
            # ped network (it is assumed that anything other than 'prohibited', ped is allowed)
            ped_network = 'Y'
            ped_l = utrans_row[3]
            ped_r = utrans_row[4]
            if HasFieldValue(ped_l) or HasFieldValue(ped_r):
                if ped_l == 'Restricted' or ped_r == 'Restricted':
                    ped_network = 'N'

            # convert meters to miles
            miles = utrans_row[10] * 0.000621371
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
            if speed_lmt == 0: # and cartocode is 11
                speed_lmt = 25

            # calculate the time fields
            drive_time = (miles / speed_lmt) * 60
            ped_time = (miles / 3.1) * 60
            #: bike time - incentivize bike lanes and local roads. roads with bike facilities, pathways, and cartocode = 11 (local roads) get a 15% faster travel speed (cost of traversing is calculated at 11 mph instead of 9.6 mph)
            if HasFieldValue(bike_l) or HasFieldValue(bike_r) or cartocode == '11':
                bike_time = (miles / 11) * 60
            else:
                bike_time = (miles / 9.6) * 60

            # transfer the road class field over
            road_class = desc_lu[utrans_row[7]]

            # transfer the AADT values over
            if utrans_row[8] is not None:
                aadt = utrans_row[8]

            # transfer the AADT year over
            aadt_yr = utrans_row[9]


            # create a list of values that will be used to construct new row
            insert_row_values = [(utrans_row[0], miles, oneway, source_data, speed_lmt, drive_time, ped_time, bike_time, auto_network, ped_network, bike_network, connector_network, road_class, aadt, aadt_yr, bike_l, bike_r, utrans_row[11])]
            print insert_row_values

            # insert the new row with the list of values
            for insert_row in insert_row_values:
                insert_cursor.insertRow(insert_row)

                
# this function imports the user-defined utrans trails into the the netork dataset feature class 
def import_TrailsIntoNetworkDataset(utrans_trails_to_import):
    
    # convert features in trail dataset from multipart to singlepart
    trails_singlepart = MultipartToSinglepart_management(utrans_trails_to_import, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\trails_singlepart' + '_' + strDate)
    
    
    # create list of field names
    #                    0                1                 2            3 
    trail_fields = ['PrimaryName', 'DesignatedUses', 'SHAPE@LENGTH', 'SHAPE@']
    #                   0           1             2          3           4          5              6              7            8              9             10                11            12
    network_fields = ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetwork', 'PedNetwork', 'BikeNetwork', 'ConnectorNetwork', 'SHAPE@']

    # set up search cursors to select and insert data between feature classes
    with arcpy.da.SearchCursor(trails_singlepart, trail_fields) as search_cursor, arcpy.da.InsertCursor(bike_ped_auto, network_fields) as insert_cursor:
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
            bike_time = (miles / 11) * 60

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
        arcpy.MakeFeatureLayer_management(utransFeatureClass, 'utransIntersected_lyr', r"CARTOCODE not in ('99', '13', '14', '15', '17', '18')")
    if source == "Trails":
        arcpy.MakeFeatureLayer_management(utransFeatureClass, 'utransIntersected_lyr', r"Status = 'EXISTING' and TransNetwork = 'Yes'")

    # instersect the utrans data with the fifty site buffers
    arcpy.SelectLayerByLocation_management('utransIntersected_lyr', 'intersect', 'spatialSelectPolygon_lyr')
    
    # make new feature layer from the intersected utrans data
    matchcount = int(arcpy.GetCount_management('utransIntersected_lyr')[0]) 
    if matchcount == 0:
        print('no features matched spatial and attribute criteria')
    else:
        intersected_roads = arcpy.CopyFeatures_management('utransIntersected_lyr', 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\utransIntersected' + source + '_' + strDate)
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
        intersected_roads = arcpy.CopyFeatures_management('utransQueried_lyr', 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\utransWhereClause' + source + '_' + strDate)
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


def importTransitData():
    # import transit stops
    transit_stops_multipoint = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitStops' #### Note ####: change dates (if it's been updated) for fgdb to current dataset  
    # explode transit stops to single points (currently they are mulitpoints)
    print "explode multipoint stops to single points"
    transit_stops_singlepoints = "C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStops_" + strDate
    arcpy.FeatureVerticesToPoints_management(transit_stops_multipoint, transit_stops_singlepoints, "ALL")       
    print "import transit stops"
    arcpy.FeatureClassToFeatureClass_conversion(transit_stops_singlepoints, r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb\NetworkDataset', 'TransitStops') #### Note ####: change dates (if it's been updated) for fgdb to current dataset 


    # import the transit routes feature class
    # transit_route_source = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitRoutes' #### Note ####: change transit data date (if it's been updated)
    arcpy.FeatureClassToFeatureClass_conversion(transit_route_source, r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb' + '\NetworkDataset', 'TransitRoutes')
    transit_routes_network_dataset =  r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb' + '\NetworkDataset\TransitRoutes'   

    # add miles field
    arcpy.AddField_management(transit_routes_network_dataset, "Length_Miles", "DOUBLE", "", "", "", "", "NULLABLE")
    # convert meters to miles
    # calc newly-created mile values to the miles field
    arcpy.CalculateField_management(transit_routes_network_dataset, field="Length_Miles", expression="(!Shape_Length! * 0.000621371)", expression_type="PYTHON_9.3")

    # add transit time field
    arcpy.AddField_management(transit_routes_network_dataset, "TransitTime", "DOUBLE", "", "", "", "", "NULLABLE")
    ### use stops in the calc (below) arcpy.CalculateField_management(transit_routes_network_dataset, field="TransitTime", expression="((!Shape_Length! * 0.000621371) / 17.2) * 60", expression_type="PYTHON_9.3")
    
    # add a field in the route fc to hold the number of stops
    arcpy.AddField_management(transit_routes_network_dataset, "RouteType", "TEXT", field_length=15)
    # buffer sgid commuter rail layer and then select by location to find the transit routes that have their center in this buffer - then assing those selected routes a RouteType of 'CommmuterRail'
    sgid_commuter_rail = r'Database Connections\DC_agrc@SGID10@sgid.agrc.utah.gov.sde\SGID10.TRANSPORTATION.CommuterRailRoutes_UTA'
    # buffer the comm rail
    sgid_commuter_rail_buff = r"C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\SGID_CommRailBuff_" + strDate
    arcpy.Buffer_analysis(sgid_commuter_rail, sgid_commuter_rail_buff, 30)
    # make feature layer of transit (required input for selection by location)
    arcpy.MakeFeatureLayer_management(transit_routes_network_dataset,'lyr_transit_fgdb')
    # select by location - select transit lines in the  buffer
    select_by_location_selectedFeatures = arcpy.SelectLayerByLocation_management('lyr_transit_fgdb', "HAVE_THEIR_CENTER_IN", sgid_commuter_rail_buff)
    # loop through the selected transit lines and assign the commuter lines a value
    with arcpy.da.UpdateCursor(select_by_location_selectedFeatures, ['RouteType']) as cursor:
        for row in cursor:
            row[0] = 'CommuterRail'

            # update the cursor
            cursor.updateRow(row)

    ## calc values to transit time fields
    # light-rail is typically 17.2 mph
    # commuter rail is typically 30 mph
    # add a field in the route fc to hold the number of stops
    arcpy.AddField_management(transit_routes_network_dataset, "StopCount", "DOUBLE", "", "", "", "", "NULLABLE")

    # populate the number of stops
    # loop through transit routes and assign the number of stops based on atttribute query
    #             0          1            2             3             4               5
    fields = ['trip_id', 'route_id', 'StopCount', 'TransitTime', 'Length_Miles', 'RouteType']
    with arcpy.da.UpdateCursor(transit_routes_network_dataset, fields) as cursor:
        for row in cursor:
            query_string = "trip_id = " + str(row[0]) + " and route_id = " + str(row[1])
            rows_tran_stops = [row_stops for row_stops in arcpy.da.SearchCursor(transit_stops_singlepoints, ['trip_id', 'route_id'], query_string)]
            
            # populate the StopCount field
            row[2] = len(rows_tran_stops) 
            
            # populate the travel time field (calc separately for commuter rail and bus/light rail)
            # note: use this calc from below website: [Total travel time = (8.5 mi) / (16.9 mi/hr) + (22 stops)*(18 sec/stop)*(1 hr / 3600 sec) = 0.613 hr = 37 minutes (rounded up to the nearest minute)]
            # for more info see Problem/Solution section: https://en.wikibooks.org/wiki/Fundamentals_of_Transportation/Transit_Operations_and_Capacity
            if row[5] ==  "CommuterRail":
                # for commuter rail use 30 mph +  18 sec for stop + route length.
                row[3] = (row[4] / 30 * 60) + (row[2] * .3)  # the fisrt parantheses calcs the time the second parentheses adds the stops (.3 mins = 18 seconds)
            else:
                # for bus and light rail, use 16.9 mph + 18 sec for stop + route length.
                row[3] = (row[4] / 16.9 * 60) + (row[2] * .3)  # the fisrt parantheses calcs the time the second parentheses adds the stops (.3 mins = 18 seconds)
            
            # update the cursor
            cursor.updateRow(row)
        

if __name__ == "__main__":
    # execute only if run as a script
    main()