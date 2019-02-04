# code source: http://desktop.arcgis.com/en/arcmap/latest/tools/network-analyst-toolbox/build-network.htm

# Name: BuildNetwork_ex02.py
# Description: Build a network dataset.
# Requirements: Network Analyst Extension 

#Import system modules
import sys
import os
import shutil
import arcpy
from arcpy import env

#Check out the Network Analyst extension license
arcpy.CheckOutExtension("Network")

#Set environment settings
env.workspace = "C:/Data/SanFrancisco.gdb"

#Set local variables
network = "Transportation/Streets_ND"

#Build the network dataset
arcpy.na.BuildNetwork(network)

#If there are any build errors, they are recorded in a BuildErrors.txt file
#present in the system temp directory, so copy this file to the directory
#containing this script.
temp_dir = os.environ.get("TEMP")
if temp_dir:
    shutil.copy2(os.path.join(temp_dir, "BuildErrors.txt"), sys.path[0])

print("Script completed successfully.")