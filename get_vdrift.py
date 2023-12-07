import yaml
import numpy as np
import math

import units


def v_drift(run_config, drift_model=2):
    ''' 
        Electron drift velocity in mm/us
        
        mode:
        1. LArSoft (commonly used, a lot hard codded numbers here) 
           Ref: https://internal.dunescience.org/doxygen/lardataalg_2lardataalg_2DetectorInfo_2DetectorPropertiesStandard_8cxx_source.html
        2. BNL mobility measurement (see function electron_mobility())
 
    '''

    # get electric field from run data
    e_field = run_config['efield'] 

    # get temperature from run data
    temp = run_config['temp']

    # calculate drift velocity
    if drift_model == 1:
        # for low eField use mobility, but the parametrization is different than the BNL one
        tdiff = temp - 87.302
        eFit = 0.0938163 - 0.0052563 * tdiff - 0.000146981 * np.power(tdiff,2)
        muFit = 5.183987 + 0.01447761 * tdiff - 0.0034972 * np.power(tdiff,2) - 0.0005162374 * np.power(tdiff,3)

        # parameters for drift speed fit
        # p1, p2, p3, p4, p5, p6, t0
        ICARUS_params = np.array([-0.04640231, 0.0171171, 1.881246, 0.9940772, 0.0117183, 4.202141, 105.7491])
        Walkowiak_params = np.array([-0.01481, -0.0075, 0.141, 12.4, 1.627, 0.317, 90.371])

        # for low eField, vdrift model uses mobility * eField 
        if e_field < eFit:
            v_drift = muFit * e_field

        # for intermediate eField, vdrift model uses ICARUS parametrization
        elif e_field < 0.619:
            v_drift = drift_speed_helper(ICARUS_params, e_field, temp)
    
        # for eField between two model ranges
        elif e_field < 0.699:
            v_drift = (0.699 - e_field) / 0.08 * drift_speed_helper(ICARUS_params, e_field, temp) \
                                 + (e_field - 0.619) / 0.08 * drift_speed_helper(Walkowiak_params, e_field, temp)

        # for high eField, vdrift model uses Walkowiak parametrization
        else:
            v_drift = drift_speed_helper(Walkowiak_params, e_field, temp)

    if drift_model == 2:
        v_drift = electron_mobility(e_field, temp) * (e_field / units.cm) # change e_field's unit to kV/mm

    return v_drift

def electron_mobility(e_field, temp=87.17):
    '''
        Calculation of the electron mobility w.r.t temperature and electric
        field.
        References:
         - https://lar.bnl.gov/properties/trans.html (summary)
         - https://doi.org/10.1016/j.nima.2016.01.073 (parameterization)
        :param e: electric field in kV/mm
        :param t: temperature in K
        :returns: electron mobility in mm^2/kV/us
    '''
    # electron_mobility_params BNL parametrization
    a0, a1, a2, a3, a4, a5 = np.array([551.6, 7158.3, 4440.43, 4.29, 43.63, 0.2053])

    num = a0 + a1 * e_field + a2 * np.power(e_field, 1.5) + a3 * np.power(e_field, 2.5)
    denom = 1 + (a1 / a0) * e_field + a4 * np.power(e_field, 2) + a5 * np.power(e_field, 3)
    temp_corr = np.power(temp / 89, -1.5)

    mu = num / denom * temp_corr

    mu = mu * ((units.cm**2) / units.V / units.s)
    return mu

def drift_speed_helper(params, e_field, temp=87.17):
    '''
        Help function for drift speed calculation  w.r.t LAr temperature and electric field.
    '''
    p1, p2, p3, p4, p5, p6, t0 = params

    v_drift = (1 + p1 * (temp - t0) ) * (p3 * e_field * math.log(1 + abs(p4) / e_field) + p5 * np.power(e_field,p6)) + p2 * (temp-t0)

    return v_drift


