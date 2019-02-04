# data source http://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/create-template-from-network-dataset.htm

import arcpy

network = "C:/data/SanDiego.gdb/Transportation/Streets_ND"
output_xml_file = "C:/data/NDTemplate.xml"
arcpy.na.CreateTemplateFromNetworkDataset(network, output_xml_file)