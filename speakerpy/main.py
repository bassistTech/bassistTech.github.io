'''
build command:
    flet build web
to serve locally for testing:
    python -m http.server --directory build/web
'''

import flet as ft

driver = {  # Eminence DeltaLite 2512-ii
    'F_s': {'val': 37, 'units': 'Hz'},  # resonant frequency in Hz
    'R_e': {'val': 5.04, 'units': 'Ohms'},  # series resistance of voice coil in Ohms
    'L_e': {'val': 0.46, 'units': 'mH', 'mult': 0.001},
    'Q_ms': {'val': 3.13},  # mechanical contribution to Q factor
    'Q_es': {'val': 0.44},  # electromagnetic contribution to Q factor
    'Vas': {'val': 147, 'units': 'liters', 'mult': 0.001},
    'Xmax': {'val': 4.90, 'units': 'mm', 'mult': 0.001},
    'S_d': {'val': 519.5, 'units': 'cm^2', 'mult': 1e-4},  # cone area converted from cm^2 to m^2
}

box = {  # My little 12" box
    'V_box': {'val': 32, 'units': 'liters', 'mult': 1e-3},
    'n_ports': {'val': 1, 'units': 'number of ports or 0 for sealed'},
    'f_port': {'val': 40, 'units': 'Hz'},
    'Q_port': {'val': 50},
    'portShape': {'val': ['rectangular', 'circular']},
    'd_port': {'val': 0, 'units': 'cm diameter of port if circular', 'mult': 0.01},
    'a_port': {'val': 3.5, 'units': 'cm width of port if rectangular', 'mult': 0.01},
    'b_port': {'val': 21.5, 'units': 'cm height of port of rectangular', 'mult': 0.01},
    'endCorrect': {'val': 0.732},  # port end correction factor
}

system = {
    'Znom': {'val': 8, 'units': 'Ohms'},
    'Pin': {'val': 100, 'units': 'W rms'},
    }


def add_widgets(dict_in, key):
    '''
    Create text fields for all of the input parameters. Note that dict_in
    is modified. This is a call-by-reference function! TODO: Stop doing this
    '''

    props = {'dense': True, 
             'content_padding': ft.padding.all(10)}
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
        print(item['widget'].label_style)


def get_values(dict_in):
    '''
    Convert GUI dictionary back into simple key-value pairs
    '''

    dict_out = {}
    for key in dict_in:
        item = dict_in[key]
        if item['type'] == list:
            val = item['rg'].value
        else:
            val = item['type'](item['widget'].value)
        if 'mult' in item:
            val = val*item['mult']
        dict_out[key] = val
    return dict_out


async def main(page: ft.Page):
    '''
    "Await" has to happen inside an async function definition, and the packages
    can't be imported until the install happenbuls, so the packages will be local
    to main() and not in the global namespace. Therefore all of your functions
    that use the packages also have to be defined inside main().
    '''

    import sys
    if "pyodide" in sys.modules:
        import micropip
        await micropip.install(['pandas', 'numpy', 'matplotlib'])

    # import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from flet.matplotlib_chart import MatplotlibChart
    matplotlib.use("svg")

    import xcone

    '''
    Handlers for GUI events
    '''

    def graph_update(e):
        newDriver = get_values(driver)
        newBox = get_values(box)
        print(newBox)
        newSystem = get_values(system)
        report = xcone.runGraph(axs, {'design': '1x12 ported'}, newDriver, newBox, newSystem)
        s = '\n'.join([key + ': ' + str(report[key]) for key in report])
        reportText.value = s
        reportText.update()
        fig.canvas.draw()
        mpc.update()

    def clear_and_update(e):
        [ax.clear() for ax in axs]
        graph_update(0)

    '''
    Build the GUI
    '''

    for key in driver:
        add_widgets(driver, key)

    for key in box:
        add_widgets(box, key)

    for key in system:
        add_widgets(system, key)

    fig, axs = plt.subplots(4, 1, figsize=(10, 15), layout = 'tight')
    mpc = MatplotlibChart(fig, original_size = True)

    page.add(
        ft.Text(value="Speaker modeling program", color="green", size = 20))
    
    page.add(
        ft.Row(
            [ft.Container(ft.Column(
                [ft.Text(value = "Driver parameters", color = "black")]
                + [driver[key]['widget'] for key in driver]
                + [ft.Text(value = 'System parameters', color = 'black')]
                + [system[key]['widget'] for key in system]),
                width = 350),
            ft.Container(ft.Column(
                [ft.Text(value = 'Box parameters', color = 'black')]
                + [box[key]['widget'] for key in box]), 
                width = 350)],
            vertical_alignment = ft.CrossAxisAlignment.START))
    page.add(
        ft.Row(
            [ft.ElevatedButton("Update", on_click=graph_update),
            ft.ElevatedButton("Clear and update", on_click=clear_and_update),
            ft.Text(value="Report at bottom of page")]))
    
    page.add(ft.Row([mpc]))
    page.add(ft.Text(value = 'Modeling report', color = 'black'))
    reportText = ft.TextField(min_lines=5, max_lines=20, multiline=True)
    page.add(reportText)
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.update()

ft.app(target=main)
