# data source http://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/create-template-from-network-dataset.htm

import arcpy

network = "C:/temp/NetworkDataset_Testing/NetworkDataset_Restrictions.gdb/NetworkDataset\NetworkDataset_ND"
output_xml_file = "D:/MultimodalNetwork/network_xml_template/NDTemplate.xml"
arcpy.na.CreateTemplateFromNetworkDataset(network, output_xml_file)