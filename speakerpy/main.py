'''
Speaker modeling program

Francis Deck, 3/32/2024
MIT License: https://opensource.org/license/mit'

build command:
    flet build web
to serve locally for testing:
    python -m http.server --directory build/web
To serve online, change index.html in this way:
    <base href="./">
'''

import flet as ft

driver_defaults = {  # Eminence DeltaLite 2512-ii
    'F_s': {'val': 37, 'units': 'Hz'}, 
    'R_e': {'val': 5.04, 'units': 'Ohms'},
    'L_e': {'val': 0.46, 'units': 'mH', 'mult': 0.001},
    'Q_ms': {'val': 3.13},
    'Q_es': {'val': 0.44},
    'Vas': {'val': 147, 'units': 'liters', 'mult': 0.001},
    'Xmax': {'val': 4.90, 'units': 'mm', 'mult': 0.001},
    'S_d': {'val': 519.5, 'units': 'cm^2', 'mult': 1e-4},
}

box_defaults = {  # My little 12" box
    'V_box': {'val': 32, 'units': 'liters', 'mult': 1e-3},
    'n_ports': {'val': 1, 'units': 'number of ports or 0 for sealed'},
    'f_port': {'val': 40, 'units': 'Hz'},
    'Q_port': {'val': 50},
    'portShape': {'val': ['rectangular', 'circular']},
    'd_port': {'val': 0, 'units': 'cm diameter of port if circular', 'mult': 0.01},
    'a_port': {'val': 3.5, 'units': 'cm width of port if rectangular', 'mult': 0.01},
    'b_port': {'val': 21.5, 'units': 'cm height of port of rectangular', 'mult': 0.01},
    'endCorrect': {'val': 0.732},
}

system_defaults = {
    'Znom': {'val': 8, 'units': 'Ohms'},
    'Pin': {'val': 100, 'units': 'W rms'},
    }


def add_widgets(dict_in):
    '''
    Create text fields for all of the input parameters. This is a way of converting
    all of the parameters of interest into GUI widgets, en masse.

    See the default parameters sets above, for how dict_in is structured.
    '''
    props = {'dense': True, 
             'content_padding': ft.padding.all(10)}
    
    dict_out = {}
    for key in dict_in:
        item = dict_in[key]
        item['type'] = type(item['val'])
        label = key
        if 'units' in item:
            label = label + ' (' + item['units'] + ')'
        if item['type'] == list:
            item['radios'] = [ft.Radio(value = v, label = v) for v in item['val']]
            item['rg'] = ft.RadioGroup(content = ft.Row(item['radios']),
                                        value = item['radios'][0].value)
            item['widget'] = ft.Row([ft.Text(value = label, 
                                            size = 12),
                                        item['rg']])
        else:
            item['widget'] = ft.TextField(label=label, 
                                        value=item['val'], 
                                        **props)
        dict_out[key] = item
    return dict_out

def get_values(dict_in, use_mult = True):
    '''
    Convert GUI dictionary back into simple key-value pairs that can
    be passed to the functions doing computation
    '''
    dict_out = {}
    for key in dict_in:
        item = dict_in[key]
        if item['type'] == list:
            val = item['rg'].value
        else:
            val = item['type'](item['widget'].value)
        if ('mult' in item) and use_mult:
            val = val*item['mult']
        dict_out[key] = val
    return dict_out

def inject_values(gui, new_params):
    '''
    Inject the values from a new parameter list into an existing GUI
    '''   
    for key in new_params:
        if gui[key]['type'] == list:
            gui[key]['rg'].value = new_params[key]
            gui[key]['rg'].update()
        else:
            gui[key]['widget'].value = new_params[key]
            gui[key]['widget'].update()

def load_parameters(new_params, driver_gui, box_gui, system_gui):
    '''
    Handler for "load design parameters" button
    '''
    inject_values(driver_gui, new_params['driver'])
    inject_values(box_gui, new_params['box'])
    inject_values(system_gui, new_params['system'])

def graph_update(xcone, dumps,
                 axs, mpc, 
                 driver_gui, box_gui, system_gui, 
                 reportText, designText, 
                 clearFirst):
    '''
    Handler for "update graph" button
    '''
    if clearFirst:
        [ax.clear() for ax in axs]

    report = xcone.runGraph(axs, 
                            get_values(driver_gui) 
                            | get_values(box_gui)
                            | get_values(system_gui))
    s = '\n'.join([key + ': ' + str(report[key]) for key in report])
    reportText.value = s
    reportText.update()

    design_json = {'driver': get_values(driver_gui, False),
                    'box': get_values(box_gui, False),
                    'system': get_values(system_gui, False)}
    designText.value = dumps(design_json, indent = '  ')
    designText.update()
    mpc.update()

async def main(page: ft.Page):
    '''
    In Pyodide, some modules have to be installed via micropip before they can
    be imported. Moreover, "await micropip.install" can only be called within an
    async function.

    For this reason, the package imports can't be placed at the top of the program,
    where you usually expect to see them. Instead, they have to be imported within 
    main(), and become local to main().

    and because packages are local to main, their functions have to be passed
    to external functions like graph_update(). This is so far the best way I've found
    to manage the awkwardness of using micropip. If there's a better way, 
    please let me know.
    '''

    import sys
    if "pyodide" in sys.modules:
        import micropip
        await micropip.install(['numpy', 
                                'matplotlib',
                                'simplejson'])

    import simplejson
    import matplotlib
    import matplotlib.pyplot as plt
    from flet.matplotlib_chart import MatplotlibChart
    matplotlib.use("svg")

    import xcone

    driver_gui = add_widgets(driver_defaults)
    box_gui = add_widgets(box_defaults)
    system_gui = add_widgets(system_defaults)

    fig, axs = plt.subplots(4, 1, figsize=(10, 15), layout = 'tight')
    mpc = MatplotlibChart(fig, original_size = True)

    page.add(
        ft.Text(value="Speaker modeling program", color="green", size = 20))
    
    page.add(
        ft.Row(
            [ft.Container(ft.Column(
                [ft.Text(value = "Driver parameters", color = "black")]
                + [driver_gui[key]['widget'] for key in driver_gui]
                + [ft.Text(value = 'System parameters', color = 'black')]
                + [system_gui[key]['widget'] for key in system_gui]),
                width = 350),
            ft.Container(ft.Column(
                [ft.Text(value = 'Box parameters', color = 'black')]
                + [box_gui[key]['widget'] for key in box_gui]), 
                width = 350)],
            vertical_alignment = ft.CrossAxisAlignment.START))
    page.add(
        ft.Row(
            [ft.ElevatedButton("Update graph", 
                               on_click = lambda e: graph_update(
                                   xcone, simplejson.dumps,
                                   axs, mpc, 
                                   driver_gui, box_gui, system_gui, 
                                   reportText, designText, 
                                   False)),
            ft.ElevatedButton("Clear and update graph", 
                              on_click = lambda e: graph_update(
                                    xcone, simplejson.dumps,
                                   axs, mpc, 
                                   driver_gui, box_gui, system_gui, 
                                   reportText, designText, 
                                   True)),
            ft.ElevatedButton('Load design parameters from below',
                              on_click = lambda e: load_parameters(simplejson.loads(designText.value),
                                                                   driver_gui, 
                                                                   box_gui, 
                                                                   system_gui)),
            ft.Text(value="Report at bottom of page")]))
    
    page.add(ft.Row([mpc]))

    page.add(ft.Text(value = 'Modeling report', color = 'black'))
    reportText = ft.TextField(min_lines=5, max_lines=20, multiline=True)
    page.add(reportText)

    page.add(ft.Text(value = 'Design parameters. You can save these in a text file.', 
                     color = 'black'))
    designText = ft.TextField(min_lines = 5, max_lines = 20, multiline = True)
    page.add(designText)

    page.scroll = ft.ScrollMode.ADAPTIVE
    page.update()

ft.app(target=main)
