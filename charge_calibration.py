import numpy as np

def recombination(mode, run_config):
    dEdx = 2 # MeV/cm, truth match per pixel

    # box
    if mode == 1:
        # Baller, 2013 JINST 8 P08005
        csi = run_config['box_beta'] * dEdx / (run_config['efield'] * run_config['lar_density'])
        recomb = max(0, np.log(run_config['box_alpha'] + csi) / csi)
 
    # birks
    elif mode == 2:
        # Amoruso, et al NIM A 523 (2004) 275
        recomb = run_config['birks_Ab'] / (1 + run_config['birks_kb'] * dEdx / (run_config['efield'] * run_config['lar_density']))

    return recomb

def lifetime(t_drift, run_config):
     lifetime_red = np.exp(-t_drift / run_config['lifetime'])
     return lifetime_red
