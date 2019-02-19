import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

# global variables
#bike_ped_auto = r'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto'
bike_ped_auto = r'D:\MultimodalNetwork\MM_NetworkDataset_02112019.gdb\NetworkDataset\BikePedAuto'
transit_stops_multipoint = r'D:\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitStops'

# explode transit stops to single point layer (currently they are mulitpoints)
stops_out_name = "D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStops_" + strDate
transit_stops_singlepoints = arcpy.FeatureVerticesToPoints_management(transit_stops_multipoint, stops_out_name, "ALL")


## create a near table showing what transit stops are what near what BikePedAuto routes
out_near_table = "D:/MultimodalNetwork/MultimodalScratchData.gdb/NearTable_" + strDate
arcpy.GenerateNearTable_analysis(transit_stops_singlepoints, bike_ped_auto, out_near_table, search_radius="100 Meters", location="LOCATION", angle="NO_ANGLE", closest="CLOSEST", closest_count="0", method="PLANAR")


## create a new layer based on the BikePedAuto that was found to near the transit stops
#                   0           1             2          3           4          5              6              7            8              9             10          11 
network_fields = ['Name', 'Length_Miles', 'Oneway', 'SourceData', 'Speed', 'DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetork', 'PedNetwork', 'BikeNetwork', 'SHAPE@']
arcpy.CreateFeatureclass_management(fgdb_dataset_name, "BikePedAuto_near", "POLYLINE", 
                                    'D:\MultimodalNetwork\MultimodalScriptData.gdb\BikePedAuto_template', "DISABLED", "DISABLED", 
                                    utrans_roads)







## convert transit lines to points
# Execute FeatureVerticesToPoints
bike_ped_auto_verts = arcpy.FeatureVerticesToPoints_management(bike_ped_auto, r"D:\MultimodalNetwork\MultimodalScratchData.gdb\vertices_ " + strDate, "ALL")
# add a field called called "NEAR_FID"



###### loop through all the transit stops
##                   0          1          2          3    
#transit_stops_fields = ['shape_id', 'trip_id', 'route_id', 'SHAPE@']

## set up search cursors to select and insert data between feature classes
#with arcpy.da.SearchCursor(transit_stops, transit_stops_fields) as search_cursor:
#    # itterate though the intersected utrans road centerline features
#    for transit_stops_row in search_cursor:




#        ##### get nearest line-derived point (from transit lines) to the current transit stops
#        # set local variables
#        in_features = "houses"
#        near_features = "parks"
    
#        # find features only within search radius
#        search_radius = "5000 Meters"
    
#        # find location nearest features
#        location = "LOCATION"
    
#        # avoid getting angle of neares features
#        angle = "NO_ANGLE"
    
#        #### execute the function
#        arcpy.Near_analysis(in_features, near_features, search_radius, location, angle)

#            ## create a line between those two points 
#            # Set local variables
#            inFeatures = "calibration_points.shp"
#            outFeatures = "C:/output/output.gdb/out_lines"
#            lineField = "ROUTE1"
#            sortField = "MEASURE"

#            # Execute PointsToLine 
#            arcpy.PointsToLine_management(inFeatures, outFeatures, lineField, sortField)


