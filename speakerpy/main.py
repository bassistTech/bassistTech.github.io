'''
flet publish speaker.py
python -m http.server --directory dist
'''

import flet as ft
import sys

emi2512ii = { # Eminence DeltaLite 2512-ii
    'F_s': 37, # resonant frequency in Hz
    'R_e': 5.04, # series resistance of voice coil in Ohms
    'L_e': 0.46*0.001, # inductance of voice coil converted from mH to H
    'Q_ms': 3.13, # mechanical contribution to Q factor
    'Q_es': 0.44, # electromagnetic contribution to Q factor
    'Vas': 147*0.001, # equivalent box volume, liters converted to m^3
    'Xmax': 4.90*0.001, # maximum excursion, converted from mm to m
    'S_d': 519.5/1e4, # cone area converted from cm^2 to m^2
}

box1 = { # My little 12" box
    'Znom': 8,
    'Pin': 100,
    'V_box': 32*1e-3, # box volume, 32 l converted to m^3
    'ported': True,
    'f_port': 40, # port tuning frequency in Hz
    'Q_port': 50, # value borrowed from WinISD
    'portShape': 'rectangular', # circular or rectangular
    'd_port': 0, # diameter of port if circular in cm converted to m
    'a_port': 3.5*0.01, # width of port if rectangular
    'b_port': 21.5*0.01, # height of port if rectangular
    'endCorrect': 0.732, # port end correction factor
}
    
async def main(page: ft.Page):
    '''
    "Await" has to happen inside an async function definition, and the packages
    can't be imported until the install happenbuls, so the packages will be local
    to main() and not in the global namespace. Therefore all of your functions
    that use the packages also have to be defined inside main().
    '''

    if "pyodide" in sys.modules:
        import micropip
        await micropip.install(['pandas', 'numpy', 'matplotlib'])

    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from flet.matplotlib_chart import MatplotlibChart
    matplotlib.use("svg")

    '''
    Physical constants
    '''

    gamma = 1.4 # adiabatic constant, dimensionless
    P_atm = 101325 # atmospheric pressure, Pa
    rho = 1.18 # density of air, kg/m^3
    c = np.sqrt(gamma*P_atm/rho) # https://en.wikipedia.org/wiki/Speed_of_sound
    R = 1 # listening distance in meters

    # TODO review whether this is the best set of parameters
    style = 'Francis' # preferred style is 'Francis', use 'WinISD to compare results with the WinISD software'
    airspeed_units = 'm/s' # should be 'mach' or 'm/s'

    def xCone(w, 
            F_s = 37, # free air resonance in Hz
            R_e= 5.04, # series resistance of voice coil in Ohms
            L_e = 0.46*0.001, # inductance of voice coil converted from mH to H
            Q_ms = 3.13, # mechanical contribution to Q factor
            Q_es = 0.44, # electromagnetic contribution to Q factor
            Vas = 147*0.001, # equivalent box volume, liters converted to m^3
            Xmax = 4.90*0.001, # maximum excursion, converted from mm to m
            S_d = 519.5/1e4, # cone area converted from cm^2 to m^2
            
            Znom = 8,
            Pin = 100, # input power used for calculations like cone excursion and port air speed
            V_box = 32*1e-3, # box volume, 32 l converted to m^3
            ported = True,
            f_port = 40, # port tuning frequency in Hz
            Q_port = 50,
            portShape = 'rectangular', # circular or rectangular
            d_port = 100*0.01, # diameter of port if circular in cm converted to m
            a_port = 3.5*0.01, # width of port if rectangular
            b_port = 21.5*0.01, # height of port if rectangular
            endCorrect = 0.732, # port end correction factor
            initReport = {},
            design = '',
            ):
        
        '''
        Compute cone excursion and other performance measures
        
        Parameters are self explanatory, all are in SI units
        '''

        w_0 = 2*np.pi*F_s # resonant frequency in radians/s
        m = gamma*P_atm*S_d**2/w_0**2/Vas # cone mass in kg
        BL = np.sqrt(w_0*m*R_e/Q_es) # BL product in T*m
        C = w_0*m/Q_ms # Mechanical damping constant of cone
        K = w_0**2*m # Spring constant of cone
        r = np.sqrt(S_d/np.pi) # Radius
        z = R_e + 1j*w*L_e # Electrical impedance
        if style == 'WinISD':
            Vin = np.sqrt(2*Pin*R_e) # Input voltage peak amplitude
        elif style == 'Francis':
            Vin = np.sqrt(2*Pin*Znom) # Input voltage peak amplitude
        else:
            print('style must be winISD or Francis')
        K_box = gamma*P_atm*S_d**2/V_box # Spring constant of box
            
        if ported:
            w_port = 2*np.pi*f_port # port resonant frequency in radians/s
            kappa = w**2/(w**2 - 1j*w*w_port/Q_port - w_port**2) # correction factor for box spring constant based on port behavior
        else:
            kappa = 1 # i.e., no port therefore no port correction

        Keff = K + kappa*K_box # total spring constant, from driver suspension plus port-corrected box
        
        x = BL*Vin/m/z/(Keff/m + 1j*w*(BL**2/m/z + C/m) - w**2) # cone excursion amplitude in meters

        Z = z/(1 - 1j*w*BL*x/Vin) # cone impedance, complex valued, in Ohms

        p = rho*r**2*w**2*kappa*x/R/2 # sound pressure amplitude in Pascal
        p_rms = p/np.sqrt(2)

        p_ref = 20e-6 # reference value for sound pressure, in Pascal
        spl = 20*np.log10(abs(p_rms)/p_ref) # sound pressure level in dB SPL
        
        phaseRot = 180*np.pi/180 # phase rotation for phase graph, to make it agree with WinISD
        phase = np.angle(p*(np.cos(phaseRot) + 1j*np.sin(phaseRot)))*180/np.pi # phase of acoustic wavefront, nearfield
        
        # More ported behavior
        
        if ported:
            kappa2 = w_port**2/(w**2 - 1j*w*w_port/Q_port - w_port**2)
            
            if portShape == 'circular':
                S_port = np.pi*d_port**2/4
                Rport = d_port/2
            elif portShape == 'rectangular': 
                S_port = a_port*b_port
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
        report['Port angular frequency (1/s)'] = w_port
        report['Port area (m^2)'] = S_port
        report['Port effective radius (m)'] = Rport
        report['Length of port (m)'] = lport
        report['Length of port (in)'] = lport*39.3
        report['Volume of port (l)'] = lport*S_port*1000
            
        return x, Z, spl, phase, v_port, p #, pd.DataFrame([[tag, report[tag]] for tag in report])

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
        f_max = 1000
        f = np.logspace(np.log10(f_min), np.log10(f_max), 300) # a range of frequencies from 10 to 1000 Hz
        w = 2*np.pi*f
        x, Z, spl, phase, v_port, p1 = xCone(w, **(name | driver | box), initReport = name | driver | box) 
        label = name['design']
        graphs(ax, f, x, Z, spl, phase, v_port, label)

    props = {'dense': True, 'content_padding': ft.padding.all(10)}
    driver = emi2512ii
    driverControls = {key: ft.TextField(label = key, value = driver[key], **props) for key in driver}
    driverTypes = {key: type(driver[key]) for key in driver}
    
    box = box1
    boxControls = {key: ft.TextField(label = key, value = box[key], **props) for key in box}
    boxTypes = {key: type(box[key]) for key in box}

    fig, axs = plt.subplots(4, 1, figsize = (10, 15))

    mpc = MatplotlibChart(fig, original_size=True)

    def graph_update(e):
        newDriver = {key: driverTypes[key](driverControls[key].value) for key in driverControls}
        newBox = {key: boxTypes[key](boxControls[key].value) for key in boxControls}
        runGraph(axs, {'design': '1x12 ported'}, newDriver, newBox)
        fig.canvas.draw()
        mpc.update()

    def clear_and_update(e):
        [ax.clear() for ax in axs]
        graph_update(0)

    [page.add(driverControls[key]) for key in driverControls]
    [page.add(boxControls[key]) for key in boxControls]
    page.add(ft.Row([ft.ElevatedButton("Update", on_click=graph_update),
                    ft.ElevatedButton("Clear and update", on_click=clear_and_update)]))
    
    page.add(mpc)
    
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.update()

ft.app(target=main)
