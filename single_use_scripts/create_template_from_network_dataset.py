# data source http://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/create-template-from-network-dataset.htm
# run with 10.6 or Pro

import arcpy

network = r"D:\MultimodalNetwork\MM_NetworkDataset_02282019.gdb\NetworkDataset\NetworkDataset_ND"
output_xml_file = "D:/MultimodalNetwork/network_xml_template/NDTemplate.xml"
arcpy.na.CreateTemplateFromNetworkDataset(network, output_xml_file)