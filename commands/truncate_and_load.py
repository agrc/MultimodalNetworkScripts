import arcpy

def replace_bikepedauto_with_merged_and_split_data(bike_ped_auto, bike_ped_auto_merged_and_split, network_file_geodatabase):
    #: This line is just for testing, export the original BikePedAuto before truncate to do some verification that everything went okay
    arcpy.FeatureClassToFeatureClass_conversion(bike_ped_auto, network_file_geodatabase, "\\" + "BikePedAuto_orig")

    #: Truncate the existing BikePedAuto
    arcpy.TruncateTable_management(bike_ped_auto)

    #: Append newest data.
    arcpy.management.Append(bike_ped_auto_merged_and_split, bike_ped_auto, "NO_TEST")
