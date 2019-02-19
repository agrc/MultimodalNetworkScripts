import arcpy
import datetime
import time
from datetime import date
from datetime import datetime

#arcpy.env.workspace = 'D:\MultimodalNetwork'

# get the date
today = date.today()
strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

# global variables
#bike_ped_auto = r'D:\MultimodalNetwork\MM_NetworkDataset_' + strDate + '.gdb\NetworkDataset' + '\BikePedAuto'
bike_ped_auto = r'D:\MultimodalNetwork\MM_NetworkDataset_02112019.gdb\NetworkDataset\BikePedAuto'
transit_stops_multipoint = r'D:\MultimodalNetwork\MM_TransitData_02152019.gdb\TransitStops'
transit_stops_singlepoints = ""
transit_stops_buffered = ""
auto_lines_in_buffer = ""
bike_lines_in_buffer = ""
ped_lines_in_buffer = ""

# main function
def main():
    # explode transit stops to single points (currently they are mulitpoints)
    print "explode multipoint stops to single points"
    transit_stops_singlepoints = "D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStops_" + strDate
    arcpy.FeatureVerticesToPoints_management(transit_stops_multipoint, transit_stops_singlepoints, "ALL")

    # create a buffer around the transit stops
    print "buffer the transit stops single points"
    transit_stops_buffered = "D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStopBuffd_" + strDate
    arcpy.Buffer_analysis(transit_stops_singlepoints, transit_stops_buffered, 100)

    # get network lines that intersect the buffers, for each mode of travel
    print "intersect the bike network with the buffers"
    intersected_bike_network = get_SouceDataUsingSpatialQuery(transit_stops_buffered, bike_ped_auto, "Bike") 
    print "intersect the auto network with the buffers"
    intersected_auto_network = get_SouceDataUsingSpatialQuery(transit_stops_buffered, bike_ped_auto, "Auto") 
    print "intersect the ped network with the buffers"
    intersected_ped_network = get_SouceDataUsingSpatialQuery(transit_stops_buffered, bike_ped_auto, "Ped") 
    intersected_bike_network = 'D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStopBike' + '_' + strDate
    intersected_auto_network = 'D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStopAuto' + '_' + strDate
    intersected_ped_network = 'D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStopPed' + '_' + strDate

    # convert the network line data (for each of the 3 modes) to vertices 
    outputVertsToPnts = 'D:\MultimodalNetwork\MultimodalScratchData.gdb\Verts'
    print "convert the intersected bike verts to points layer" 
    intersected_bike_network_verts = arcpy.FeatureVerticesToPoints_management(intersected_bike_network, outputVertsToPnts + 'Bike' + '_' + strDate, "ALL")
    print "convert the intersected auto verts to points layer" 
    intersected_auto_network_verts = arcpy.FeatureVerticesToPoints_management(intersected_auto_network, outputVertsToPnts + 'Auto' + '_' + strDate, "ALL")
    print "convert the intersected ped verts to points layer" 
    intersected_ped_network_verts = arcpy.FeatureVerticesToPoints_management(intersected_ped_network, outputVertsToPnts + 'Ped' + '_' + strDate, "ALL")

    # add a field to each of the vert point feature classes (for each of the 3 modes)
    print "add NEAR_FID field to bike vert pnts layer" 
    arcpy.AddField_management(intersected_bike_network_verts, "NEAR_FID", "LONG")
    print "add NEAR_FID field to auto vert pnts layer" 
    arcpy.AddField_management(intersected_auto_network_verts, "NEAR_FID", "LONG")
    print "add NEAR_FID field to ped vert pnts layer" 
    arcpy.AddField_management(intersected_ped_network_verts, "NEAR_FID", "LONG")

    # calculate the OID field values to the NEAR_FID fields


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
        arcpy.MakeFeatureLayer_management(networkFeatureClass, 'linesIntersected_lyr', r"AutoNetork = 'Y'")
    if source == "Ped":
        arcpy.MakeFeatureLayer_management(networkFeatureClass, 'linesIntersected_lyr', r"PedNetwork = 'Y'")

    # instersect the network data with the transit stop buffers
    arcpy.SelectLayerByLocation_management('linesIntersected_lyr', 'intersect', 'spatialSelectPolygon_lyr')
    
    # make new feature layer from the intersected network line data
    matchcount = int(arcpy.GetCount_management('linesIntersected_lyr')[0]) 
    if matchcount == 0:
        print('no features matched spatial and attribute criteria')
    else:
        intersected_roads = arcpy.CopyFeatures_management('linesIntersected_lyr', 'D:\MultimodalNetwork\MultimodalScratchData.gdb\TranStop' + source + '_' + strDate)
        #print('{0} cities that matched criteria written to {0}'.format(matchcount, utrans_IntersectedRoads))

    return 'linesIntersected_lyr'


if __name__ == "__main__":
    # execute only if run as a script
    main()
