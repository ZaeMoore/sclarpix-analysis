import numpy as np

from functions import event_parser as EvtParser
from functions import get_vdrift as GetV
from functions import util as util

def get_pixel_plane_position(packets_arr, geom_dict, run_config):
    # The io_group (pacman) configuration per module is assumed to be the same. Otherwise the larpix layout dictionary should capture the full larpix layout of the multi-module detector. 

    tpc_centers = run_config['tpc_offsets']
    nr_iogroup_module = run_config['nr_iogroup_module']
    
    x, y, z, direction = [], [], [], []
    for packet in packets_arr:
        io_group = packet['io_group']

        module_id = (io_group - 1) // nr_iogroup_module # counting from 0
        io_group = io_group - module_id * nr_iogroup_module
        
        xyz = geom_dict[io_group, packet['io_channel'], packet['chip_id'], packet['channel_id']]
        
        # Note tpc_centers is ordered by z, y, x, as in larnd-sim config files
        x_offset = tpc_centers[module_id][2]*10 #mm
        y_offset = tpc_centers[module_id][1]*10 #mm
        z_offset = tpc_centers[module_id][0]*10 #mm
        
        x.append(xyz[0] + x_offset)
        y.append(xyz[1] + y_offset)
        z.append(xyz[2] + z_offset)
        direction.append(xyz[3])
 
    return x, y, z, direction


def get_hit3D_position_tdrift(t0,  packets, packets_arr, geom_dict, run_config, **kwargs):

    x, y, z_anode, direction = get_pixel_plane_position(packets_arr, geom_dict, run_config)

    if "drift_model" not in kwargs:
        drift_model = run_config['drift_model']
        v_drift = GetV.v_drift(run_config, drift_model)
    else:
        v_drift = GetV.v_drift(run_config, **kwargs)
    #vdrift is in mm/us

    #t0 is us, timestamps is "ticks" = 0.1us
    t = packets_arr['timestamp'].astype(float) * run_config['CLOCK_CYCLE'] #us
    #t_drift = (t - t0) #us
    t_drift = (t - t0) / 5.5

    z = direction * t_drift * v_drift + z_anode #mm

    return x, y, z, t_drift, v_drift
