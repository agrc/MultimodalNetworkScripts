import os
import arcpy


def main():
    # do stuff here
    createServiceArea()
    solve_route()


# create a service area
# http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-network-analyst/serviceareasolverproperties.htm
def createServiceArea():
    #Define variables
    workspace = "D:/MultimodalNetwork/MM_NetworkDataset_04152019.gdb"
    output_folder = "D:/MultimodalNetwork/network_analyst_script_outputs"
    nds = os.path.join(workspace, "NetworkDataset", "NetworkDataset_ND")
    #facilities = os.path.join(workspace, "Warehouses")
    facilities = "D:/MultimodalNetwork/MultimodalScriptData.gdb/FiftySites"
    analysis_layer_name = "TravelShed"

    #Set environment variables
    arcpy.env.overwriteOutput = True

    #Check out the network analyst extension
    arcpy.CheckOutExtension("network")

    #Create a new closest facility analysis layer
    make_layer_result = arcpy.na.MakeServiceAreaLayer(nds, analysis_layer_name, "TravelTime")
    analysis_layer = make_layer_result.getOutput(0)

    #Add facilities to the analysis layer using default field mappings         
    sub_layer_names = arcpy.na.GetNAClassNames(analysis_layer) # http://desktop.arcgis.com/en/arcmap/latest/extensions/network-analyst/network-analysis-classes.htm
    # facilities_layer_name = sub_layer_names["Facilities"]
    arcpy.na.AddLocations(analysis_layer, facilities_layer_name, facilities, "#", "#")

    #Get the Trucking Time travel mode from the network dataset
    travel_modes = arcpy.na.GetTravelModes(nds)
    trucking_mode = travel_modes["Trucking Time"]

    #Apply the travel mode to the analysis layer
    solver_properties = arcpy.na.GetSolverProperties(analysis_layer)
    solver_properties.applyTravelMode(trucking_mode)

    #Solve the analysis layer and save the result as a layer file          
    arcpy.na.Solve(analysis_layer)

    output_layer = os.path.join(output_folder, analysis_layer_name + ".lyr")
    arcpy.management.SaveToLayerFile(analysis_layer, output_layer, "RELATIVE")

    arcpy.AddMessage("Completed")



# solve a route
# http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-network-analyst/routesolverproperties.htm

def solve_route():
    #Set up the environment
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("network")

    #Set up variables
    networkDataset = "C:/Data/SanFrancisco.gdb/Transportation/Streets_ND"
    stops = "C:/Data/SanFrancisco.gdb/Analysis/Stores"
    fastestRoute = "C:/Data/SanFrancisco.gdb/FastestRoute"
    shortestRoute = "C:/Data/SanFrancisco.gdb/ShortestRoute"

    #Make a new route layer using travel time as impedance to determine fastest route
    routeLayer = arcpy.na.MakeRouteLayer(networkDataset, "StoresRoute", "TravelTime").getOutput(0)

    #Get the network analysis class names from the route layer
    naClasses = arcpy.na.GetNAClassNames(routeLayer)

    #Get the routes sublayer from the route layer
    routesSublayer = arcpy.mapping.ListLayers(routeLayer, naClasses["Routes"])[0]

    #Load stops
    arcpy.na.AddLocations(routeLayer, naClasses["Stops"], stops)

    #Solve the route layer
    arcpy.na.Solve(routeLayer)

    #Copy the route as a feature class
    arcpy.management.CopyFeatures(routesSublayer, fastestRoute)

    #Get the RouteSolverProperties object from the route layer to modify the
    #impedance property of the route layer.
    solverProps = arcpy.na.GetSolverProperties(routeLayer)

    #Set the impedance property to "Meters" to determine the shortest route.
    solverProps.impedance = "Meters"

    #Resolve the route layer
    arcpy.na.Solve(routeLayer)

    #Copy the route as a feature class
    arcpy.management.CopyFeatures(routesSublayer, shortestRoute)

    arcpy.AddMessage("Completed")


if __name__ == "__main__":
    # execute only if run as a script
    main()
