import logging
import subprocess


class CommandError(RuntimeError):
    pass

def run(cmd: list[str], show_live_output: bool = False):
    """
    Run a bash command.

    :param cmd: The command to run as a list of strings.
    :param show_live_output: If True, return the command's live output in the terminal.
    :return: CompletedProcess instance or stdout string.
    :raises CommandError: If the command fails.
    """
    logging.debug("Executing: %s", " ".join(cmd))

    try:
        if show_live_output:
            result = subprocess.run(
                cmd,
                check=True,
                text=True
            )
            #return result.stdout.strip()
        else:
            result = subprocess.run(
                cmd,
                check=True,
                text=True,
                capture_output = True
            )
        return result
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", " ".join(cmd))
        logging.debug(e.stderr.strip())
        raise CommandError(cmd) from e