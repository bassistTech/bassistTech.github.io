import numpy as np
import matplotlib.pyplot as plt

def kappa(f, f_port):
    '''
    Correction factor for port tuning
    '''
    if f_port is None:
        return 1
    else:
        return f**2/(f**2 - f_port**2)
    
def x(f, f_s, Q_ts, H, f_port):
    '''
    Excursion function
    '''
    kappa_factor = 1 + kappa(f, f_port)*H
    return 1/(f_s**2*(kappa_factor) + 1j*f*f_s/Q_ts - f**2)

def spl_total(f, f_s, Q_ts, H, f_port):
    '''
    Total sound pressure level function
    '''
    return 20*np.log10(np.abs(f**2*kappa(f, f_port)*x(f, f_s, Q_ts, H, f_port)))