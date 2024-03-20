from functions import units
from functions import util as util

import yaml
import os
import pickle
import pkg_resources

def load_geom_dict(geom_dict_path):
    with open(geom_dict_path, "rb") as f_geom_dict:
        geom_dict = pickle.load(f_geom_dict)
    return geom_dict

def get_data_packets(packets):

    mask = packets['packet_type'] == 0
    packets_arr = packets[mask]

    return packets_arr

def get_run_config(run_config_path, use_builtin = False):

    run_config = {}

    if use_builtin:
        run_config_path = os.path.join(os.path.dirname(__file__),
                                       "config_repo",
                                       run_config_path)
    
    with open(run_config_path) as infile:
        run_yaml = yaml.load(infile, Loader=yaml.FullLoader)

    run_config['tpc_offsets'] = run_yaml['tpc_offsets'] * units.cm # mm
    run_config['nr_iogroup_module'] = len(run_yaml['module_to_io_groups'][1]) # 2x2 module: 2 io_groups; nd-lar module: 4 io_groups

    run_config['GAIN'] = run_yaml['GAIN']  # mV/ke-
    run_config['V_CM'] = run_yaml['V_CM']  # mV
    run_config['V_REF'] = run_yaml['V_REF']  # mV
    run_config['V_PEDESTAL'] = run_yaml['V_PEDESTAL']  # mV
    run_config['ADC_COUNTS'] = run_yaml['ADC_COUNTS']
    run_config['CLOCK_CYCLE'] = run_yaml['CLOCK_CYCLE'] # us

    run_config['drift_model'] = run_yaml['drift_model'] # 1: LArSoft suite 2: BNL mobility model 
    run_config['efield'] = run_yaml['e_field'] / (units.kV / units.cm) # kV/cm # the input from the yaml should be in kV/mm
    run_config['temp'] = run_yaml['temperature'] / (units.K) #K

    run_config['response_sampling'] = run_yaml['response_sampling'] #us

    run_config['lar_density'] = run_yaml['lar_density'] # g/cm^3

    run_config['box_alpha'] = run_yaml['box_alpha'] 
    run_config['box_beta'] = run_yaml['box_beta'] 
    run_config['birks_Ab'] = run_yaml['birks_Ab'] 
    run_config['birks_kb'] = run_yaml['birks_kb'] 

    run_config['W_ion'] = run_yaml['W_ion'] #MeV

    run_config['lifetime'] = run_yaml['lifetime'] #us

    if 'beam_duration' in run_yaml:
        run_config['beam_duration'] = run_yaml['beam_duration'] #us

    return run_config

def configuration_keywords():
    return ['module0','2x2', '2x2_only', '2x2_MR4','ndlar', 'singlecube']

def detector_configuration(detector):

    if not detector in configuration_keywords():
        raise ValueError('The keyword %s is not in the list of supported detector names %s' % (detector,str(configuration_keywords())))

    if detector == "module0":
        run_config_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/module0.yaml')
        geom_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/dict_repo/multi_tile_layout-2.3.16.pkl')
        run_config = get_run_config(run_config_path)
        geom_dict = load_geom_dict(geom_path)

    elif detector == "2x2":
        run_config_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/2x2.yaml')
        geom_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/dict_repo/multi_tile_layout-2.3.16.pkl')
        run_config = get_run_config(run_config_path)
        geom_dict = load_geom_dict(geom_path)

    elif detector == "2x2_MR4":
        run_config_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/2x2_MR4.yaml')
        geom_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/dict_repo/multi_tile_layout-2.4.16.pkl')
        run_config = get_run_config(run_config_path)
        geom_dict = load_geom_dict(geom_path)

    elif detector == "2x2_only":
        run_config_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/2x2.yaml')
        geom_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/dict_repo/multi_tile_layout-2.4.16.pkl')
        run_config = get_run_config(run_config_path)
        geom_dict = load_geom_dict(geom_path)

    elif detector == "ndlar":
        run_config_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/ndlar-module.yaml')
        geom_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/dict_repo/multi_tile_layout-3.0.40.pkl')
        run_config = get_run_config(run_config_path)
        geom_dict = load_geom_dict(geom_path)
    
    elif detector == "singlecube":
        run_config_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/singlecube.yaml')
        geom_path = pkg_resources.resource_filename('LarpixParser', 'config_repo/dict_repo/multi_tile_layout-3.0.40.pkl')
        #Need to fix this for single cube?
        run_config = get_run_config(run_config_path)
        geom_dict = load_geom_dict(geom_path)     

    else:
        raise ValueError("The detector '%s' should be supported but no code implementation is found (report to package maintainers)." % detector)

    return run_config, geom_dict
