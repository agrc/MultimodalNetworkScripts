import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

#### User Note ####: change dates (only if you didn't run rallyup_network_data.py on the same day) for fgdb to current dataset (ctrl + f for "#### Note ####:")

#arcpy.env.workspace = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork'

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year)

# global variables
#bike_ped_auto = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto'
network_dataset = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb\NetworkDataset'  #### Note ####: change dates for fgdb to current dataset
bike_ped_auto = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_' + strDate +  '.gdb\NetworkDataset\BikePedAuto' #### Note ####: change dates for fgdb to current dataset
### i'm doing this in the rallup script now...  transit_stops_multipoint = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitStops' #### Note ####: change dates (if it's been updated) for fgdb to current dataset     
transit_routes = r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitRoutes' #### Note ####: change dates (if it's been updated) for fgdb to current dataset
transit_stops_singlepoints = r"C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStops_" + strDate #### Note ####: change today's dates if rallyup script was not run today
transit_stops_buffered = ""
auto_lines_in_buffer = ""
bike_lines_in_buffer = ""
ped_lines_in_buffer = ""

# main function
def main():
    ### i'm doing this rallyup data script in the impprt transit data function b/c i need the stop counts for route times
    #### explode transit stops to single points (currently they are mulitpoints)
    ###print "explode multipoint stops to single points"
    ###transit_stops_singlepoints = "C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStops_" + strDate
    ###arcpy.FeatureVerticesToPoints_management(transit_stops_multipoint, transit_stops_singlepoints, "ALL")

    # create a buffer around the transit stops
    print "buffer the transit stops single points"
    transit_stops_buffered = r"C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStopBuff_" + strDate
    arcpy.Buffer_analysis(transit_stops_singlepoints, transit_stops_buffered, 100)

    # get network lines that intersect the buffers, for each mode of travel
    print "intersect the bike network with the buffers"
    intersected_bike_network = get_SouceDataUsingSpatialQuery(transit_stops_buffered, bike_ped_auto, "Bike") 
    print "intersect the auto network with the buffers"
    intersected_auto_network = get_SouceDataUsingSpatialQuery(transit_stops_buffered, bike_ped_auto, "Auto") 
    print "intersect the ped network with the buffers"
    intersected_ped_network = get_SouceDataUsingSpatialQuery(transit_stops_buffered, bike_ped_auto, "Ped") 
    intersected_bike_network = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStopBike' + '_' + strDate
    intersected_auto_network = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStopAuto' + '_' + strDate
    intersected_ped_network = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStopPed' + '_' + strDate

    # convert the network line data (for each of the 3 modes) to vertices 
    outputVertsToPnts = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\Verts'
    print "convert the intersected bike verts to points layer" 
    intersected_bike_network_verts = arcpy.FeatureVerticesToPoints_management(intersected_bike_network, outputVertsToPnts + 'Bike' + '_' + strDate, "ALL")
    print "convert the intersected auto verts to points layer" 
    intersected_auto_network_verts = arcpy.FeatureVerticesToPoints_management(intersected_auto_network, outputVertsToPnts + 'Auto' + '_' + strDate, "ALL")
    print "convert the intersected ped verts to points layer" 
    intersected_ped_network_verts = arcpy.FeatureVerticesToPoints_management(intersected_ped_network, outputVertsToPnts + 'Ped' + '_' + strDate, "ALL")

    # add a field to each of the vert point feature classes (for each of the 3 modes)
    #print "add NEAR_FID field to transit stops"
    #arcpy.AddField_management(transit_stops_singlepoints, "NEAR_FID", "LONG")
    print "add NEAR_FID field to bike vert pnts layer" 
    arcpy.AddField_management(intersected_bike_network_verts, "NEAR_FID", "LONG")
    print "add NEAR_FID field to auto vert pnts layer" 
    arcpy.AddField_management(intersected_auto_network_verts, "NEAR_FID", "LONG")
    print "add NEAR_FID field to ped vert pnts layer" 
    arcpy.AddField_management(intersected_ped_network_verts, "NEAR_FID", "LONG")

    # calculate the OID field values to the NEAR_FID fields
    #print "calc OID values to the NEAR_FID field for bike vert pnts"
    #arcpy.CalculateField_management(transit_stops_singlepoints, field="NEAR_FID", expression="!OBJECTID!", expression_type="PYTHON", code_block="")
    print "calc OID values to the NEAR_FID field for bike vert pnts"
    arcpy.CalculateField_management(intersected_bike_network_verts, field="NEAR_FID", expression="!OBJECTID!", expression_type="PYTHON", code_block="")
    print "calc OID values to the NEAR_FID field for auto vert pnts"
    arcpy.CalculateField_management(intersected_auto_network_verts, field="NEAR_FID", expression="!OBJECTID!", expression_type="PYTHON", code_block="")
    print "calc OID values to the NEAR_FID field for ped vert pnts"
    arcpy.CalculateField_management(intersected_ped_network_verts, field="NEAR_FID", expression="!OBJECTID!", expression_type="PYTHON", code_block="")


    # create three seperate feature classs from the transit stop points - so each one can be used separatly in the near analysis and preserve the near data in the fields 
    print "create a separate feature class of transit stops for each near analysis"
    arcpy.FeatureClassToFeatureClass_conversion(transit_stops_singlepoints, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb', 'StopNearBike_' + strDate)
    arcpy.FeatureClassToFeatureClass_conversion(transit_stops_singlepoints, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb', 'StopNearAuto_' + strDate)
    arcpy.FeatureClassToFeatureClass_conversion(transit_stops_singlepoints, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb', 'StopNearPed_' + strDate)
    stops_near_bike = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\StopNearBike_' + strDate
    stops_near_auto = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\StopNearAuto_' + strDate
    stops_near_ped = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\StopNearPed_' + strDate

    # run near analysis on the transit stops to see the nearest bike/auto/ped vertex
    print "run near analysis on bike"
    arcpy.Near_analysis(stops_near_bike, intersected_bike_network_verts, search_radius="200 Meters", location="LOCATION", angle="NO_ANGLE", method="PLANAR")
    print "run near analysis on auto"
    arcpy.Near_analysis(stops_near_auto, intersected_auto_network_verts, search_radius="200 Meters", location="LOCATION", angle="NO_ANGLE", method="PLANAR")
    print "run near analysis on ped"
    arcpy.Near_analysis(stops_near_ped, intersected_ped_network_verts, search_radius="200 Meters", location="LOCATION", angle="NO_ANGLE", method="PLANAR")


    # append the near verts into the transit stop data, but only append the verts that found a nearby 
    #arcpy.Append_management(inputs="StopNearBike_02192019", target="VertsBike_02192019", schema_type="NO_TEST", field_mapping="""Name "Name" true true false 50 Text 0 0 ,First,#;Oneway "Oneway" true true false 2 Text 0 0 ,First,#;Speed "Speed" true true false 2 Short 0 0 ,First,#;AutoNetwork "AutoNetwork" true true false 1 Text 0 0 ,First,#;BikeNetwork "BikeNetwork" true true false 1 Text 0 0 ,First,#;PedNetwork "PedNetwork" true true false 1 Text 0 0 ,First,#;SourceData "SourceData" true true false 15 Text 0 0 ,First,#;DriveTime "DriveTime" true true false 8 Double 0 0 ,First,#;BikeTime "BikeTime" true true false 8 Double 0 0 ,First,#;PedestrianTime "PedestrianTime" true true false 8 Double 0 0 ,First,#;Length_Miles "Length_Miles" true true false 8 Double 0 0 ,First,#;ORIG_FID "ORIG_FID" true true false 4 Long 0 0 ,First,#,StopNearBike_02192019,ORIG_FID,-1,-1;NEAR_FID "NEAR_FID" true true false 4 Long 0 0 ,First,#,StopNearBike_02192019,NEAR_FID,-1,-1""", subtype="")
    print "append the bike data"
    arcpy.Append_management(stops_near_bike, intersected_bike_network_verts, schema_type="NO_TEST")
    print "append the auto data"
    arcpy.Append_management(stops_near_auto, intersected_auto_network_verts, schema_type="NO_TEST")
    print "append the ped data"
    arcpy.Append_management(stops_near_ped, intersected_ped_network_verts, schema_type="NO_TEST")

    ## remove the -1 from the NEAR_FID field, before creating the connector lines - by way of making a new feture class
    print "remove -1 values from bike"
    arcpy.FeatureClassToFeatureClass_conversion(intersected_bike_network_verts, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb', 'ConnPntsBike_' + strDate, "NEAR_FID <> -1")
    print "remove -1 values from auto"
    arcpy.FeatureClassToFeatureClass_conversion(intersected_auto_network_verts, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb', 'ConnPntsAuto_' + strDate, "NEAR_FID <> -1")
    print "remove -1 values from auto"
    arcpy.FeatureClassToFeatureClass_conversion(intersected_ped_network_verts, 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb', 'ConnPntsPed_' + strDate, "NEAR_FID <> -1")
    conn_pnts_bike = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\ConnPntsBike_' + strDate
    conn_pnts_auto = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\ConnPntsAuto_' + strDate
    conn_pnts_ped = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\ConnPntsPed_' + strDate

    # create lines between the verts
    print "create the connector lines for bike"
    bike_connectors = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\BikeConn_' + strDate
    arcpy.PointsToLine_management(conn_pnts_bike, bike_connectors, "NEAR_FID","NEAR_FID", "NO_CLOSE")

    print "create the connector lines for auto"
    auto_connectors = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\AutoConn_' + strDate
    arcpy.PointsToLine_management(conn_pnts_auto, auto_connectors, Line_Field="NEAR_FID", Sort_Field="NEAR_FID", Close_Line="NO_CLOSE")

    print "create the connector lines for ped"
    ped_connectors = 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\PedConn_' + strDate
    arcpy.PointsToLine_management(conn_pnts_ped, ped_connectors, Line_Field="NEAR_FID", Sort_Field="NEAR_FID", Close_Line="NO_CLOSE")

    # remove the identical connectors in each feature class
    print "delete identical connector lines for bike"
    arcpy.DeleteIdentical_management(bike_connectors, fields="Shape", xy_tolerance="", z_tolerance="0")
    print "delete identical connector lines for auto"
    arcpy.DeleteIdentical_management(auto_connectors, fields="Shape", xy_tolerance="", z_tolerance="0")  
    print "delete identical connector lines for ped"       
    arcpy.DeleteIdentical_management(ped_connectors, fields="Shape", xy_tolerance="", z_tolerance="0")

    # call the function to add and calc network fields on the connectors
    print "add fields and calc values for the bike connector data"
    addAndCalcNetworkFields(bike_connectors, "Bike")
    print "add fields and calc values for the auto connector data"
    addAndCalcNetworkFields(auto_connectors, "Auto")
    print "add fields and calc values for the ped connector data"
    addAndCalcNetworkFields(ped_connectors, "Ped")

    # append the connector data to the BikePedAuto feature class
    print "append the bike connectors into the BikePedAuto feature class"
    arcpy.Append_management(bike_connectors, bike_ped_auto, schema_type="NO_TEST")
    print "append the auto connectors into the BikePedAuto feature class"
    arcpy.Append_management(auto_connectors, bike_ped_auto, schema_type="NO_TEST")
    print "append the ped connectors into the BikePedAuto feature class"
    arcpy.Append_management(ped_connectors, bike_ped_auto, schema_type="NO_TEST")


    # import the transit routes and transit tops into the netork dataset
    ###print "import transit stops"
    ###arcpy.FeatureClassToFeatureClass_conversion(transit_stops_singlepoints, r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_03192019.gdb\NetworkDataset', 'TransitStops') #### Note ####: change dates for fgdb to current dataset
    #arcpy.FeatureClassToFeatureClass_conversion(transit_routes, r'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MM_NetworkDataset_02202019.gdb\NetworkDataset', 'TransitRoutes')

    # pull out the connectors (that we just appended) from the BikePedAuto to a separate feature class
    print "creating separate connector network feature class"
    arcpy.FeatureClassToFeatureClass_conversion(bike_ped_auto, network_dataset, 'ConnectorNetwork', "ConnectorNetwork = 'Y'")

    ### delete the connectors from the BikePedAuto feature class --- use this option if we're going the route of having the connector lines in their own connectivity group (which we currently are doing)
    query_filter = "ConnectorNetwork = 'Y'"
    with arcpy.da.UpdateCursor(bike_ped_auto, "*", query_filter) as uCur:
        for dRow in uCur:
            uCur.deleteRow()


    print "create_connectors.py script is done!"

# this function returns either network line data that intersects the transit stop buffers 
def get_SouceDataUsingSpatialQuery(spatial_boundary, networkFeatureClass, source):
    # remove referernce of any feature layers from possible previous function run
    if arcpy.Exists('spatialSelectPolygon_lyr'):
        arcpy.Delete_management('spatialSelectPolygon_lyr')
    if arcpy.Exists('linesIntersected_lyr'):
        arcpy.Delete_management('linesIntersected_lyr')

    # use the transit stop buffers to create a select by location on the network line data
    arcpy.MakeFeatureLayer_management(spatial_boundary, 'spatialSelectPolygon_lyr')

    # make feature layer of network data
    if source == "Bike":
        arcpy.MakeFeatureLayer_management(networkFeatureClass, 'linesIntersected_lyr', r"BikeNetwork = 'Y'")
    if source == "Auto":
        arcpy.MakeFeatureLayer_management(networkFeatureClass, 'linesIntersected_lyr', r"AutoNetwork = 'Y'")
    if source == "Ped":
        arcpy.MakeFeatureLayer_management(networkFeatureClass, 'linesIntersected_lyr', r"PedNetwork = 'Y'")

    # instersect the network data with the transit stop buffers
    arcpy.SelectLayerByLocation_management('linesIntersected_lyr', 'intersect', 'spatialSelectPolygon_lyr')
    
    # make new feature layer from the intersected network line data
    matchcount = int(arcpy.GetCount_management('linesIntersected_lyr')[0]) 
    if matchcount == 0:
        print('no features matched spatial and attribute criteria')
    else:
        intersected_roads = arcpy.CopyFeatures_management('linesIntersected_lyr', 'C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\TranStop' + source + '_' + strDate)
        #print('{0} cities that matched criteria written to {0}'.format(matchcount, utrans_IntersectedRoads))

    return 'linesIntersected_lyr'



def addAndCalcNetworkFields(connector_lines, connector_name):
    # set local variables
    source_data = "Connector" + connector_name
    source_data_FieldLength = 15
    network_FieldLength = 1

    # Execute AddField twice for two new fields
    # add source data field
    arcpy.AddField_management(connector_lines, "SourceData", "TEXT", field_length=source_data_FieldLength)
    # add network fields
    arcpy.AddField_management(connector_lines, "AutoNetwork", "TEXT", field_length=network_FieldLength)
    arcpy.AddField_management(connector_lines, "BikeNetwork", "TEXT", field_length=network_FieldLength)
    arcpy.AddField_management(connector_lines, "PedNetwork", "TEXT", field_length=network_FieldLength)
    arcpy.AddField_management(connector_lines, "ConnectorNetwork", "TEXT", field_length=network_FieldLength)
    # add ped_time field
    arcpy.AddField_management(connector_lines, "PedestrianTime", "DOUBLE", "", "", "", "", "NULLABLE")


    # calc the new field values
    # calc the netork fields
    if connector_name == "Bike":
        #arcpy.CalculateField_management(connector_lines, field="BikeNetwork", expression='"Y"')
        arcpy.CalculateField_management(connector_lines, field="ConnectorNetwork", expression='"Y"')
        arcpy.CalculateField_management(connector_lines, field="AutoNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="BikeNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="PedNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="SourceData", expression='"Connector_Bike"')
    if connector_name == "Auto":
        #arcpy.CalculateField_management(connector_lines, field="AutoNetwork", expression='"Y"')
        arcpy.CalculateField_management(connector_lines, field="ConnectorNetwork", expression='"Y"')
        arcpy.CalculateField_management(connector_lines, field="AutoNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="BikeNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="PedNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="SourceData", expression='"Connector_Auto"')
    if connector_name == "Ped":
        #arcpy.CalculateField_management(connector_lines, field="PedNetwork", expression='"Y"')
        arcpy.CalculateField_management(connector_lines, field="ConnectorNetwork", expression='"Y"')
        arcpy.CalculateField_management(connector_lines, field="AutoNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="BikeNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="PedNetwork", expression='"N"')
        arcpy.CalculateField_management(connector_lines, field="SourceData", expression='"Connector_Ped"')
    # calc the pedtime for all connectors
    arcpy.CalculateField_management(connector_lines, field="PedestrianTime", expression="((!Shape_Length! * 0.000621371) / 3.1) * 60", expression_type="PYTHON_9.3")



if __name__ == "__main__":
    # execute only if run as a script
    main()
