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
    # inductance of voice coil converted from mH to H
    'L_e': {'val': 0.46, 'units': 'mH', 'mult': 0.001},
    'Q_ms': {'val': 3.13},  # mechanical contribution to Q factor
    'Q_es': {'val': 0.44},  # electromagnetic contribution to Q factor
    # equivalent box volume, liters converted to m^3
    'Vas': {'val': 147, 'units': 'liters', 'mult': 0.001},
    # maximum excursion, converted from mm to m
    'Xmax': {'val': 4.90, 'units': 'mm', 'mult': 0.001},
    'S_d': {'val': 519.5, 'units': 'cm^2', 'mult': 1e-4},  # cone area converted from cm^2 to m^2
}

box = {  # My little 12" box
    'Znom': {'val': 8, 'units': 'Ohms'},
    'Pin': {'val': 100, 'units': 'W rms'},
    'V_box': {'val': 32, 'units': 'liters', 'mult': 1e-3},  # box volume, 32 l converted to m^3
    'n_ports': {'val': 1, 'units': 'number of ports or 0 for sealed'},
    'f_port': {'val': 40, 'units': 'Hz'},  # port tuning frequency in Hz
    'Q_port': {'val': 50},  # value borrowed from WinISD
    # circular or rectangular
    'portShape': {'val': 'rectangular', 'units': 'circular or rectangular'},
    # diameter of port if circular in cm converted to m
    'd_port': {'val': 0, 'units': 'cm diameter of port if circular', 'mult': 0.01},
    # width of port if rectangular
    'a_port': {'val': 3.5, 'units': 'cm width of port if rectangular', 'mult': 0.01},
    # height of port if rectangular
    'b_port': {'val': 21.5, 'units': 'cm height of port of rectangular', 'mult': 0.01},
    'endCorrect': {'val': 0.732},  # port end correction factor
}


def add_textfields(dict_in, key):
    '''
    Create text fields for all of the input parameters. Note that dict_in
    is modified. This is a call-by-reference function!
    '''

    props = {'dense': True, 'content_padding': ft.padding.all(10)}
    item = dict_in[key]
    item['type'] = type(item['val'])
    label = key
    if 'units' in item:
        label = label + ' (' + item['units'] + ')'
    item['textfield'] = ft.TextField(label=label, value=item['val'], **props)


def get_values(dict_in):
    dict_out = {}
    for key in dict_in:
        item = dict_in[key]
        val = item['type'](item['textfield'].value)
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
        report = xcone.runGraph(axs, {'design': '1x12 ported'}, newDriver, newBox)
        s = '\n'.join([key + ': ' + str(report[key]) for key in report])
        reportText.value = s
        reportText.update()
        fig.canvas.draw()
        mpc.update()

    def clear_and_update(e):
        [ax.clear() for ax in axs]
        graph_update(0)

    # def context(e):
    #     try:
    #         reportText.value = str(js.location.search)
    #     except:
    #         reportText.value = 'error'
    #     reportText.update()

    '''
    Build the GUI
    '''

    for key in driver:
        add_textfields(driver, key)

    for key in box:
        add_textfields(box, key)

    fig, axs = plt.subplots(4, 1, figsize=(10, 15))
    mpc = MatplotlibChart(fig, original_size=True)

    page.add(ft.Text(value="Speaker modeling program", color="green"))
    [page.add(driver[key]['textfield']) for key in driver]
    [page.add(box[key]['textfield']) for key in box]
    page.add(ft.Row([ft.ElevatedButton("Update", on_click=graph_update),
                    ft.ElevatedButton("Clear and update", on_click=clear_and_update),
                    ft.Text(value="Report at bottom of page")]))
    reportText = ft.TextField(min_lines=5, max_lines=20, multiline=True)
    page.add(mpc)
    page.add(reportText)
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.update()

ft.app(target=main)
