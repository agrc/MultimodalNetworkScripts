import arcpy

# select all segments in the network ('BikePedAuto') where:
    # "SourceData = 'Trails' and class <> '8 - Bridge, Tunnel' AND SourceData = 'RoadCenterlines' and VertLevel = ?"

#: set local variables
new_network_location = "C:\\Users\\gbunce\\Documents\projects\\MultimodalNetwork\\MM_NetworkDataset_12042020.gdb\\NetworkDataset"