import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import geopandas as gpd
import veroviz as vrv
import pandas as pd

# Used to plot the Co-ordinates
def gen_plot(df):
    plt.figure(figsize=(10,10))
    plt.scatter(df['xcord'][:1], df['ycord'][:1], label= "Depot", color= "Green", marker= "o", s=100)
    plt.scatter(df['xcord'][1::], df['ycord'][1::], label= "Locations", color= "Red", marker= "o", s=100)
    plt.xlabel('x - axis')
    # frequency label
    plt.ylabel('y - axis')
    # plot title
    plt.title('Simplified Map')
    # showing legend
    plt.legend()


    for i, label in enumerate(df.index.values):
        plt.annotate(label, (df['xcord'][i], df['ycord'][i]), fontproperties = fm.FontProperties(size=20))
        
    return plt

# Used to plot arrows
def add_arrows(df, routes, plt, color="green"):
    prev_cord = ()
    for i, label in enumerate(routes['route'].to_numpy()):
        if i > 0:
            plt.annotate("", xy=(df['xcord'][label], df['ycord'][label]), xytext=prev_cord, arrowprops=dict(arrowstyle="simple, head_length=0.5, head_width=0.5, tail_width=0.15", connectionstyle="arc3", color=color, mutation_scale=20, ec="black"), label="vehicle-1")
        prev_cord = df['xcord'][label], df['ycord'][label]
        
    return plt

# Prints vehicle routes
def show_vehicle_routes(routes, locations):
    vehicles = routes.truck_id.unique().to_numpy()
    for id in vehicles:
        print("For vehicle -",id, "route is: \n")
        route = routes[routes.truck_id == id]
        path = ""
        route_ids = route.route.to_numpy()
        for index, route_id in enumerate(route_ids):
            path += locations[route_id]
            type(route_ids)
            if index != (len(route_ids)-1):
                path += "->"
        print(path + "\n\n")
        
def map_vehicle_routes(df, route, colors):
    plt = gen_plot(df)
    veh_ids = route.truck_id.unique().to_numpy()

    for v_id in veh_ids:
        plt = add_arrows(df, route[route.truck_id == v_id], plt, color=colors[v_id])
        
    return plt

# Function to convert generic X and Y coordinates to longitude and latitude, so it can be visualized on a map.
def map_XY_to_LongLat(routes_df, truck_ids):
  gdf = gpd.GeoDataFrame(routes_df, geometry=gpd.points_from_xy(routes_df.xcord*50, routes_df.ycord*50))
  gdf.crs = {'init': 'epsg:3310'}
  gdf['xy_geometry'] = gdf['geometry']
  gdf.to_crs({'init': 'epsg:4326'}, inplace=True)
  gdf.rename(columns={'geometry': 'lat_long_geometry'}, inplace=True)

  gdf.lat_long_geometry = gdf.lat_long_geometry.apply(lambda p: [p.y -0.55, p.x -1.15 ])
  routes = []
  nodes = [gdf['lat_long_geometry'].iloc[0]]
  for i in truck_ids:
    gdf_id = gdf[gdf['truck_id']==i]
    routes.append(gdf_id['lat_long_geometry'].tolist())
    nodes = nodes + gdf_id['lat_long_geometry'].tolist()[1:-1]
  return nodes, routes

# Creates leaflet to display nodes and routes on the map as per given input
def get_vrv_leaflet(nodes, routes):
  # Single depot node:
  nodesDF = vrv.createNodesFromLocs(
    locs             = [nodes[0]],
    nodeType         = 'depot',
    leafletColor     = 'red',
    leafletIconType  = 'home')

  # 3 Customer nodes:
  nodesDF = vrv.createNodesFromLocs(
    initNodes       = nodesDF,
    locs            = nodes[1:],
    leafletColor    = 'blue',
    leafletIconType = 'star')

  assignmentsDF = vrv.initDataframe('assignments')
  color = ['green', 'red', 'blue', 'black', 'brown', 'purple']
  for i,route in enumerate(routes):
          for location in range(len(route)-1):
            startloc = route[location]
            endloc = route[location+1]
            shapepointsDF = vrv.getShapepoints2D(
                    startLoc         = startloc,
                    endLoc           = endloc,
                    routeType        = 'fastest',
                    leafletColor     = color[i],
                    leafletWeight    = 6,
                    leafletOpacity   = 0.6,
                    dataProvider = 'OSRM-online',
                    useArrows = False,
                    )
            assignmentsDF = pd.concat([assignmentsDF, shapepointsDF], ignore_index=True, sort=False)

  return vrv.createLeaflet(nodes = nodesDF, arcs = assignmentsDF, mapBackground = 'Cartodb Positron')
