'''
Cone response calculation and graphing utilities for speaker modeling program
'''

import numpy as np
import matplotlib

'''
Physical constants
'''

gamma = 1.4 # adiabatic constant, dimensionless
P_atm = 101325 # atmospheric pressure, Pa
rho = 1.18 # density of air, kg/m^3
c = np.sqrt(gamma*P_atm/rho) # https://en.wikipedia.org/wiki/Speed_of_sound
R = 1 # listening distance in meters

style = 'Francis' # preferred style is 'Francis', use 'WinISD to compare results with the WinISD software'
airspeed_units = 'm/s' # should be 'mach' or 'm/s'

def xCone(w, F_s, R_e, L_e, Q_ms, Q_es, Vas, Xmax, S_d, Znom,
        Pin, V_box, n_ports, f_port, Q_port, portShape, d_port, a_port, b_port, endCorrect,
        initReport = {}, design = ''):
    
    '''
    Compute cone excursion and other performance measures

    Inputs are in SI units
    '''

    w_0 = 2*np.pi*F_s # resonant frequency in radians/s

    '''
    Turn Thiele-Small parameters into electromechanical parameters
    all in SI units
    '''
    m = gamma*P_atm*S_d**2/w_0**2/Vas # cone mass in kg
    BL = np.sqrt(w_0*m*R_e/Q_es) # BL product in T*m
    C = w_0*m/Q_ms # Mechanical damping constant of cone
    K = w_0**2*m # Spring constant of cone
    r = np.sqrt(S_d/np.pi) # Radius of cone
    z = R_e + 1j*w*L_e # Electrical impedance
    if style == 'WinISD':
        Vin = np.sqrt(2*Pin*R_e) # Input voltage peak amplitude
    elif style == 'Francis':
        Vin = np.sqrt(2*Pin*Znom) # Input voltage peak amplitude
    else:
        print('style must be winISD or Francis')
    K_box = gamma*P_atm*S_d**2/V_box # Spring constant of box

    '''
    Port correction factors, described in my article
    '''
        
    if n_ports == 0:
        kappa = 1 # i.e., no port therefore no port correction
    else:
        w_port = 2*np.pi*f_port # port resonant frequency in radians/s
        kappa = w**2/(w**2 - 1j*w*w_port/Q_port - w_port**2) # correction factor for box spring constant based on port behavior

    Keff = K + kappa*K_box # total spring constant, from driver suspension plus port-corrected box

    '''
    Now we can compute excursion, using the electromechanical parameters
    '''
    
    x = BL*Vin/m/z/(Keff/m + 1j*w*(BL**2/m/z + C/m) - w**2) # cone excursion amplitude in meters

    '''
    Everything else is derived from the excursion function.
    '''

    Z = z/(1 - 1j*w*BL*x/Vin) # cone impedance, complex valued, in Ohms

    p = rho*r**2*w**2*kappa*x/R/2 # sound pressure amplitude in Pascal
    p_rms = p/np.sqrt(2)

    p_ref = 20e-6 # reference value for sound pressure, in Pascal RMS
    spl = 20*np.log10(abs(p_rms)/p_ref) # sound pressure level in dB SPL
    
    phaseRot = 180*np.pi/180 # phase rotation for phase graph, to make it agree with WinISD
    phase = np.angle(p*(np.cos(phaseRot) + 1j*np.sin(phaseRot)))*180/np.pi # phase of acoustic wavefront, nearfield
    
    '''
    Performance of the port
    '''
    
    if n_ports != 0:
        kappa2 = w_port**2/(w**2 - 1j*w*w_port/Q_port - w_port**2)
        
        if portShape == 'circular':
            S_port = n_ports*np.pi*d_port**2/4
            Rport = d_port/2
        elif portShape == 'rectangular': 
            S_port = n_ports*a_port*b_port
            Rport = min(a_port, b_port)/2 # assume effective radius is the smaller of the two dimensions
            initReport['d_port'] = np.sqrt(4*S_port/np.pi)
        else:
            print('portShape needs to be circular or rectangular')
        
        if airspeed_units == 'mach':
            v_port = 1j*w*kappa2*x*S_d/S_port/c # speed of port air plug
        elif airspeed_units == 'm/s':
            v_port = 1j*w*kappa2*x*S_d/S_port # speed of port air plug
        else:
            print('Airspeed units must be mach or m/s')
        
        lport = S_port*gamma*P_atm/rho/V_box/w_port**2 - Rport*2*endCorrect # length of port in meters
        
    else:
        v_port = None
        
    report = dict(initReport)
    report['adiabatic constant'] = gamma
    report['atmospheric pressure (Pa)'] = P_atm
    report['density of air (kg/m^3)]'] = rho
    report['speed of sound in air'] = c
    report['listening distance (m)'] = R
    report['resonant angular frequency w_0 (1/s)'] = w_0
    report['cone mass m (kg)'] = m
    report['magnetic field length product BL (T m)'] = BL
    report['mechanical damping factor (N/(m/s))'] = C
    report['mechanical spring constant (N/m)'] = K
    report['mechanical compliance (m/N)'] = 1/K
    report['input power (W)'] = Pin
    report['peak input voltage (V)'] = Vin
    report['cone radius (m)'] = r
    report['box spring constant (N/m)'] = K_box
    if n_ports != 0:
        report['Port angular frequency (1/s)'] = w_port
        report['Port area (m^2)'] = S_port
        report['Port effective radius (m)'] = Rport
        report['Length of port (m)'] = lport
        report['Length of port (in)'] = lport*39.3
        report['Volume of port (l)'] = lport*S_port*1000
        
    return x, Z, spl, phase, v_port, p, report

def graphs(ax, f, x, Z, spl, phase, v_port, label):
    '''
    Display the interesting graphs for the design.
    '''
    ax[0].semilogx(f, np.abs(x)*1000, label = label)
    ax[0].set_ylabel('cone excursion amplitude (mm)')
    
    ax[1].semilogx(f, np.abs(Z), label = label)
    ax[1].set_ylabel('impedance ($\Omega$)')

    ax[2].semilogx(f, spl, label = label)
    ax[2].set_ylabel('Sound pressure (dB SPL)')

    # ax[3].semilogx(f, phase, label = label)
    # ax[3].set_ylabel('Phase')

    ax[3].semilogx(f, np.abs(v_port), label = label)
    ax[3].set_xlabel('frequency (Hz)')
    ax[3].set_ylabel('port air speed (' + airspeed_units + ')')
        
    for a in ax:
        a.set_xticks([10, 20, 40, 60, 100, 200, 400, 600])
        a.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        a.legend()

def runGraph(ax, name, driver, box):
    f_min = 10
    f_max = 500
    f = np.logspace(np.log10(f_min), np.log10(f_max), 300) # a range of frequencies from 10 to 1000 Hz
    w = 2*np.pi*f
    x, Z, spl, phase, v_port, p1, report = xCone(w, **(name | driver | box), initReport = name | driver | box) 
    label = name['design']
    graphs(ax, f, x, Z, spl, phase, v_port, label)
    return report