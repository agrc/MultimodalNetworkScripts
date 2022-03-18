#: Name: split_trails_at_intersections.py
#: Description: this script was created to be run once on the UTRANS TrailsAndPathsways dataset to
#:                  split all trails at intersections where the feature is not a bridge or tunnel
#:                  it then reassigns the Unique_IDs for the segments that have been split (b/c they are duplicates)

#: Notes:
#: possible variables to update before each run include:
#:   workspace
#:   trails_paths
#:   trails_paths_split
#:   dup_uniqueid_table

#: Import system modules 
import arcpy

#: Set environment settings
arcpy.env.workspace = "C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\Trails\\split_trails_at_intersections\\split_trails_intersections_June2nd2021.gdb"

#: Set local variables
trails_paths = "TrailsAndPathways"
trails_paths_split = "TrailsAndPathways_split_at_intersections"
dup_uniqueid_table = "duplicate_uniqueids"

#: Make feature layer with where clause
arcpy.MakeFeatureLayer_management(trails_paths, "trails_paths_lyr", "CartoCode <> '8 - Bridge, Tunnel'")

# Use FeatureToLine function to combine features into single feature class
print("begin feature-to-line")
finished_product = arcpy.FeatureToLine_management("trails_paths_lyr", trails_paths_split, "0.001 Meters", "ATTRIBUTES")

#: Delete the newly-created FID_TrailsPathways field (this will keep the schema the same and also allow the append below w/o "NO_TEST")
arcpy.DeleteField_management(finished_product, ["FID_TrailsAndPathways"])

#: Append the segments (bridges and tunnels) that did not get split back into the dataset
arcpy.MakeFeatureLayer_management(trails_paths, "trails_paths_bridges_lyr", "CartoCode = '8 - Bridge, Tunnel'")
print("begin append cartocode 8's")
arcpy.management.Append("trails_paths_bridges_lyr", finished_product)

#: Find duplicate uniqueids - these will need to be recalculated using the arcmap tool
print("begin find duplicate Unique_IDs")
unique_dup_tbl = arcpy.FindIdentical_management(finished_product, dup_uniqueid_table, "Unique_ID", output_record_option="ONLY_DUPLICATES")

#: Null out the duplicates
print("begin null out duplicates unique_ids")
joined_fc = arcpy.management.JoinField(finished_product, "OBJECTID", unique_dup_tbl, "IN_FID")

#: Make feature layer where IN_FID is not null and then calculate UniqueID values to null where this is true
arcpy.MakeFeatureLayer_management(joined_fc, "joined_fc_lyr", "IN_FID is not NULL")
arcpy.management.CalculateField("joined_fc_lyr", "Unique_ID", "None", "PYTHON3", '', "TEXT")

#: Remove the join fields
arcpy.DeleteField_management(finished_product, ["IN_FID", "FEAT_SEQ"])

print("Done!")
