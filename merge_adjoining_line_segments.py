import arcpy

def merge_similar_adjoining_segments(bike_ped_auto, strDate):

    bike_ped_auto_merge_adjoined = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MultimodalScratchData.gdb\\BikePedAutoMergeAdjoined_" + strDate
    dissolve_fields = ["Name", "Oneway", "Speed", "AutoNetwork", "BikeNetwork", "PedNetwork", "SourceData", "ConnectorNetwork", "CartoCode", "AADT", "AADT_YR", "BIKE_L", "BIKE_R", "VERT_LEVEL"]
    arcpy.management.UnsplitLine(bike_ped_auto, bike_ped_auto_merge_adjoined, dissolve_fields)


#: run this script as a stand alone
bike_ped_auto = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MM_NetworkDataset_05132021.gdb\\NetworkDataset\\BikePedAuto"
strDate = "05132021"
merge_similar_adjoining_segments(bike_ped_auto, strDate)