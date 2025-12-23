def print_output(function, verbose_mode: bool):
    if verbose_mode:
        function()
    else:
        run_with_spinner(function())

def run_with_spinner(command):
    pass