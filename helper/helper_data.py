import cudf
import cuopt
from cuopt.routing import utils

# Reads one of the homberger's insatnce definition to read dataset
# This function is specifically desgined only to read homberger's insatnce definition
def read_data(filename):
    df, vehicle_capacity, n_vehicles = utils.create_from_file(filename)
    return df, vehicle_capacity, n_vehicles
