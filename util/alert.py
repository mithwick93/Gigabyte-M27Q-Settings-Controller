import subprocess

ALERT_TYPES = {
    "information": "as informational",
    "warning": "as warning",
    "critical": "as critical",
}


def show_error_message(
        title: str,
        message: str,
        button_text: str = "OK",
        alert_type: str = "information"
):
    alert_script_type = ALERT_TYPES.get(alert_type, "as critical")
    script = f'display alert "{title}" message "{message}" buttons {{"{button_text}"}} default button "{button_text}" {alert_script_type}'

    subprocess.run(["osascript", "-e", script])
