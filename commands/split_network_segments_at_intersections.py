import arcpy

def split_network_at_intersections(bike_ped_auto, strDate):

    bike_ped_auto_split = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MultimodalScratchData.gdb\\BikePedAutoSplit_" + strDate

    #: Make feature layer with where clause
    arcpy.MakeFeatureLayer_management(bike_ped_auto, "bike_ped_auto_lyr", "(SourceData = 'Trails' and CartoCode <> '8 - Bridge, Tunnel') OR (SourceData = 'RoadCenterlines' and VERT_LEVEL Not In ('1','2','3'))")

    #: Use FeatureToLine function to combine features into single feature class
    print("begin feature-to-line")
    finished_product = arcpy.FeatureToLine_management("bike_ped_auto_lyr", bike_ped_auto_split, "0.001 Meters", "ATTRIBUTES")

    #: Delete the newly-created FID_BikePedAuto field (this will keep the schema the same and also allow the append below w/o "NO_TEST")
    arcpy.DeleteField_management(finished_product, ["FID_BikePedAuto"])

    #: Append the segments that did not get split back into the dataset
    arcpy.MakeFeatureLayer_management(bike_ped_auto, "bike_ped_auto_not_split_lyr", "(SourceData = 'Trails' and CartoCode = '8 - Bridge, Tunnel') OR (SourceData = 'RoadCenterlines' and VERT_LEVEL In ('1','2','3'))")
    print("begin appending segments that were not split")
    arcpy.management.Append("bike_ped_auto_not_split_lyr", finished_product, "NO_TEST")

    return bike_ped_auto_split


#: run this script as a stand alone
#bike_ped_auto = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MM_NetworkDataset_05132021.gdb\\NetworkDataset\\BikePedAuto"
#strDate = "05132021"
#split_network_at_intersections(bike_ped_auto, strDate)
