import sys

from nicegui import ui, app, native

from core.m27q import MonitorControl


def handle_exit():
    ui.run_javascript('close();')
    app.shutdown()


if __name__ in {"__main__", "__mp_main__"}:
    if sys.platform != "darwin":
        raise Exception("This script works only on MacOS.")

    with MonitorControl() as m:
        slider = ui.slider(
            min=0,
            max=100,
            value=m.get_brightness(),
            on_change=lambda e: m.set_brightness(e.value)
        )

        with ui.row():
            ui.label('Brightness')
            ui.label().bind_text_from(slider, 'value')

        ui.button('Close', on_click=lambda: handle_exit())

        ui.run(
            reload=False,
            window_size=(500, 500),
            native=False,
            port=native.find_open_port()
        )
