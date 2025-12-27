import logging
import subprocess


class CommandError(RuntimeError):
    pass

def run(cmd: list[str], show_live_output: bool = False, check: bool = True):
    """
    Run a bash command.

    :param cmd: The command to run as a list of strings.
    :param show_live_output: If True, shows the command's live output in the terminal.
    :param check: If True, raises CommandError on non-zero exit codes.
                  If False, returns CompletedProcess with any exit code.
    :return: CompletedProcess instance with returncode, stdout, stderr attributes.
    :raises CommandError: If the command fails and check=True.
    """
    logging.debug("Executing: %s", " ".join(cmd))

    try:
        if show_live_output:
            result = subprocess.run(
                cmd,
                check=check,
                text=True
            )
        else:
            result = subprocess.run(
                cmd,
                check=check,
                text=True,
                capture_output=True
            )
        return result
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", " ".join(cmd))
        if e.stderr:
            logging.debug(e.stderr.strip())
        raise CommandError(cmd) from e