import arcpy
from commands.check_if_field_has_value import HasFieldValue

def calc_miles_time(bike_ped_auto):
    
    #                       0             1            2              3              4            5              6              7              8               9         10        11          12           13
    network_fields = ['Length_Miles','SourceData','DriveTime', 'PedestrianTime', 'BikeTime', 'AutoNetwork', 'PedNetwork', 'BikeNetwork', 'ConnectorNetwork', 'Speed', 'BIKE_L', 'BIKE_R', 'CartoCode', 'SHAPE@LENGTH']

    # Create update cursor for feature class 
    with arcpy.da.UpdateCursor(bike_ped_auto, network_fields) as cursor:
        for row in cursor:
            bike_time = None
            ped_time = None
            drive_time = None
            
            # convert meters to miles
            miles = row[13] * 0.000621371
            miles = round(miles, 10)
            row[0] = miles

            speed_lmt = row[9]
            bike_l = row[10]
            bike_r = row[11]
            cartocode = row[12]

            #: Calculate all time fields for segments originating in the roads feature class.
            if (row[1] == 'RoadCenterlines'):
                #: Calculate the time fields
                #: DriveTime
                drive_time = (miles / speed_lmt) * 60
                row[2] = drive_time

                #: PedTime
                ped_time = (miles / 3.1) * 60
                row[3] = ped_time

                #: BikeTime
                #: bike time - incentivize bike lanes and local roads. roads with bike facilities, pathways, and cartocode = 11 (local roads) get a 15% faster travel speed (cost of traversing is calculated at 11 mph instead of 9.6 mph)
                if HasFieldValue(bike_l) or HasFieldValue(bike_r) or cartocode == '11':
                    bike_time = (miles / 11) * 60
                else:
                    bike_time = (miles / 9.6) * 60
                row[4] = bike_time
            #: Calculate all time fields for segments originating in the trails feature class.
            elif (row[1] == 'Trails'):
                    # Calculate the time fields for ped and bike
                    ped_time = (miles / 3.1) * 60
                    row[3] = ped_time
                    bike_time = (miles / 11) * 60
                    row[4] = bike_time

            # Update the cursor with the updated list
            cursor.updateRow(row)



#: run this script as a stand alone
#bike_ped_auto = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MM_NetworkDataset_05132021.gdb\\NetworkDataset\\BikePedAuto"
#bike_ped_auto = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MultimodalScratchData.gdb\\BikePedAuto_template_new"
#calc_miles_time(bike_ped_auto)