# ADC 
# mV
# ke-
# MeV (include work function, recombination and lifetime correction)
import numpy as np

from functions import units
from functions import charge_calibration as Cali

def get_calo_ADC(packets_arr):
    return packets_arr['dataword']

def get_calo_mV(packets_arr, run_config):
    packet_mv = []
    packet_mV = packets_arr['dataword'] / run_config['ADC_COUNTS'] * (run_config['V_REF'] - run_config['V_CM']) + run_config['V_CM'] - run_config['V_PEDESTAL']
    return packet_mV

def get_calo_ke(packets_arr, run_config):
    packet_mV = get_calo_mV(packets_arr, run_config)
    packet_ke = packet_mV / run_config['GAIN']
    return packet_ke

def get_calo_MeV(packets_arr, t_drift_arr, run_config):
    ## recombination require truth matching
    # W_ion [MeV/e]
    lifetime_red = Cali.lifetime(t_drift_arr, run_config) 
    recomb = Cali.recombination(2, run_config)
    packet_MeV = get_calo_ke(packets_arr, run_config) * 1000 / recomb / lifetime_red * run_config['W_ion']
    return packet_MeV    

def get_calo_true(packets_arr, assn, g4_seg):
    contribution_mask = assn['track_ids'] == -1
    track_id = np.ma.array(assn['track_ids'], mask = contribution_mask)
    packet_charge_frac = np.ma.array(assn['fraction'], mask = contribution_mask)
    pdgcode = np.ma.array(g4_seg['pdg_id'][track_id], mask = contribution_mask)
    dE = np.ma.array(g4_seg['dE'][track_id], mask = contribution_mask)
    return track_id, packet_charge_frac, pdgcode, dE
