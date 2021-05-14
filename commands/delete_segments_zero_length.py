import arcpy

def delete_zero_length(bike_ped_auto):

    # Create update cursor for feature class 
    with arcpy.da.UpdateCursor(bike_ped_auto, 'SHAPE@LENGTH') as cursor:
        for row in cursor:
            if row[0] == None or row[0] <= 0:
                cursor.deleteRow()

#: run this script as a stand alone
#bike_ped_auto = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MultimodalScratchData.gdb\\BikePedAutoMergeAdjoined_05132021"
#delete_zero_length(bike_ped_auto)