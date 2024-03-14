'''
flet build web
python -m http.server --directory build/web
'''

import flet as ft
import sys

emi2512ii = { # Eminence DeltaLite 2512-ii
    'F_s': {'val': 37, 'units': 'Hz'}, # resonant frequency in Hz
    'R_e': {'val': 5.04, 'units': 'Ohms'}, # series resistance of voice coil in Ohms
    'L_e': {'val': 0.46, 'units': 'mH', 'mult': 0.001}, # inductance of voice coil converted from mH to H
    'Q_ms': {'val': 3.13}, # mechanical contribution to Q factor
    'Q_es': {'val': 0.44}, # electromagnetic contribution to Q factor
    'Vas': {'val': 147, 'units': 'liters', 'mult': 0.001}, # equivalent box volume, liters converted to m^3
    'Xmax': {'val': 4.90, 'units': 'mm', 'mult': 0.001}, # maximum excursion, converted from mm to m
    'S_d': {'val': 519.5, 'units': 'cm^2', 'mult': 1e-4}, # cone area converted from cm^2 to m^2
}

box1 = { # My little 12" box
    'Znom': {'val': 8, 'units': 'Ohms'},
    'Pin': {'val': 100, 'units': 'W rms'},
    'V_box': {'val': 32, 'units': 'liters', 'mult': 1e-3}, # box volume, 32 l converted to m^3
    'n_ports': {'val': 1, 'units': 'number of ports or 0 for sealed'},
    'f_port': {'val': 40, 'units': 'Hz'}, # port tuning frequency in Hz
    'Q_port': {'val': 50}, # value borrowed from WinISD
    'portShape': {'val': 'rectangular', 'units': 'circular or rectangular'}, # circular or rectangular
    'd_port': {'val': 0, 'units': 'cm diameter of port if circular', 'mult': 0.01}, # diameter of port if circular in cm converted to m
    'a_port': {'val': 3.5, 'units': 'cm width of port if rectangular', 'mult': 0.01}, # width of port if rectangular
    'b_port': {'val': 21.5, 'units': 'cm height of port of rectangular', 'mult': 0.01}, # height of port if rectangular
    'endCorrect': {'val': 0.732}, # port end correction factor
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
            n_ports = 1, # number of ports or 0 for sealed
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
            
        if n_ports == 0:
            kappa = 1 # i.e., no port therefore no port correction
        else:
            w_port = 2*np.pi*f_port # port resonant frequency in radians/s
            kappa = w**2/(w**2 - 1j*w*w_port/Q_port - w_port**2) # correction factor for box spring constant based on port behavior

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
            
        return x, Z, spl, phase, v_port, p, report #, pd.DataFrame([[tag, report[tag]] for tag in report])

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
        x, Z, spl, phase, v_port, p1, report = xCone(w, **(name | driver | box), initReport = name | driver | box) 
        label = name['design']
        graphs(ax, f, x, Z, spl, phase, v_port, label)
        return report

    def textField(driver, key):
        '''
        Automatically assign type and create text field for item
        '''
        props = {'dense': True, 'content_padding': ft.padding.all(10)}
        item = driver[key]
        item['type'] = type(item['val'])
        label = key
        if 'units' in item:
            label = label + ' (' + item['units'] + ')'
        item['textfield'] = ft.TextField(label = label, value = item['val'], **props,)
    
    driver = emi2512ii
    for key in driver:
        textField(driver, key)
    
    box = box1
    for key in box:
        textField(box, key)

    fig, axs = plt.subplots(4, 1, figsize = (10, 15))

    mpc = MatplotlibChart(fig, original_size=True)

    def getValues(driver):
        newDriver = {}
        for key in driver:
            item = driver[key]
            val = item['type'](item['textfield'].value)
            if 'mult' in item:
                val = val*item['mult']
            newDriver[key] = val
        return newDriver

    def graph_update(e):
        newDriver = getValues(driver)
        newBox = getValues(box)
        print(newDriver, newBox)
        report = runGraph(axs, {'design': '1x12 ported'}, newDriver, newBox)
        s = '\n'.join([key + ': ' + str(report[key]) for key in report])
        reportText.value = s
        reportText.update()
        fig.canvas.draw()
        mpc.update()

    def clear_and_update(e):
        [ax.clear() for ax in axs]
        graph_update(0)

    page.add(ft.Text(value="Speaker modeling program", color="green"))
    [page.add(driver[key]['textfield']) for key in driver]
    [page.add(box[key]['textfield']) for key in box]
    page.add(ft.Row([ft.ElevatedButton("Update", on_click=graph_update),
                    ft.ElevatedButton("Clear and update", on_click=clear_and_update),
                    ft.Text(value = "Report at bottom of page")]))
    reportText = ft.TextField(min_lines = 5, max_lines = 20, multiline=True)
    page.add(mpc)
    page.add(reportText)
    
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.update()

ft.app(target=main)
