#from LarpixParser import geom_dict_loader as DictLoader
from functions import get_charge as GetCharge
from functions import coord_transform as CoordTran
from functions import get_raw_coord as GetCoord
from functions import util as util

def hit_parser_position(t0, packets, geom_dict, run_config, switch_xz=True, **kwargs):

    packets_arr = util.get_data_packets(packets)

    # get 3D hit position, and flip x and z
    x, y, z, t_drift_arr, v_drift_arr = GetCoord.get_hit3D_position_tdrift(t0, packets,
                                                              packets_arr, geom_dict,
                                                              run_config, **kwargs)

    # transform coordinate
    if switch_xz:
        x, y, z = CoordTran.switch_xz(x, y, z)

    return x, y, z, t_drift_arr, v_drift_arr

def hit_parser_charge(t0, packets, geom_dict, run_config, switch_xz=True, **kwargs):
    
    packets_arr = util.get_data_packets(packets)

    x, y, z, t_drift_arr, v_drift_arr = hit_parser_position(t0, packets,
                                               geom_dict, run_config,
                                               switch_xz, **kwargs)

    dQ = GetCharge.get_calo_MeV(packets_arr, t_drift_arr, run_config)

    return x, y, z, dQ, v_drift_arr, t_drift_arr

def hit_parser_energy(t0, packets, geom_dict, run_config, switch_xz=True, **kwargs):

    packets_arr = util.get_data_packets(packets)

    x, y, z, t_drift_arr = hit_parser_position(t0, packets,
                                               geom_dict, run_config,
                                               switch_xz, **kwargs)

    dE = GetCharge.get_calo_MeV(packets_arr, t_drift_arr, run_config)

    return x, y, z, dE

def hit_parser_charge_n_truth(t0, packets, geom_dict,
                              run_config, assn, g4_seg,
                              switch_xz=True, **kwargs):

    packets_arr = util.get_data_packets(packets)

    x, y, z, t_drift_arr = hit_parser_position(t0, packets,
                                               geom_dict, run_config,
                                               switch_xz, **kwargs)

    dQ = GetCharge.get_calo_ke(packets_arr, run_config)

    trackID, frac, pdg = GetCharge.get_calo_true(packets_arr, assn, g4_seg)

    return x, y, z, dQ, trackID, frac, pdg
