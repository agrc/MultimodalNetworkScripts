import arcpy

def merge_similar_adjoining_segments(bike_ped_auto, strDate):

    bike_ped_auto_merge_adjoined = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MultimodalScratchData.gdb\\BikePedAutoMergeAdjoined_" + strDate
    dissolve_fields = ["Name", "Oneway", "Speed", "AutoNetwork", "BikeNetwork", "PedNetwork", "SourceData", "ConnectorNetwork", "CartoCode", "AADT", "AADT_YR", "BIKE_L", "BIKE_R", "VERT_LEVEL"]
    arcpy.management.UnsplitLine(bike_ped_auto, bike_ped_auto_merge_adjoined, dissolve_fields)

    return bike_ped_auto_merge_adjoined

#: run this script as a stand alone
#bike_ped_auto = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MM_NetworkDataset_05132021.gdb\\NetworkDataset\\BikePedAuto"
#strDate = "05132021"
#merge_similar_adjoining_segments(bike_ped_auto, strDate)


# this is my snippit from Pro when i used statistics on the time and length fields
#arcpy.management.UnsplitLine("BikePedAuto", r"C:\Users\gbunce\Documents\projects\MultimodalNetwork\MultimodalScratchData.gdb\BikePedAutoMergeAdjoined_05132021_pro2", "Name;Oneway;Speed;AutoNetwork;BikeNetwork;PedNetwork;SourceData;ConnectorNetwork;CartoCode;AADT;AADT_YR;BIKE_L;BIKE_R;VERT_LEVEL", "BikeTime SUM;PedestrianTime SUM;Shape_Length SUM;Length_Miles SUM;DriveTime SUM;AADT FIRST;AADT_YR FIRST;AutoNetwork FIRST;BIKE_L FIRST;BIKE_R FIRST;BikeNetwork FIRST;CartoCode FIRST;ConnectorNetwork FIRST;Name FIRST;OBJECTID UNIQUE;Oneway FIRST;PedNetwork FIRST;SourceData FIRST;Speed FIRST;VERT_LEVEL FIRST")