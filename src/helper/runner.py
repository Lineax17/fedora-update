import logging
import subprocess


class CommandError(RuntimeError):
    pass

def run(cmd: list[str], return_output: bool = False):
    """
    Run a bash command.

    :param cmd: The command to run as a list of strings.
    :param return_output: If True, return the command's stdout as a string.
    :return: CompletedProcess instance or stdout string.
    :raises CommandError: If the command fails.
    """
    logging.debug("Executing: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", " ".join(cmd))
        logging.debug(e.stderr.strip())
        raise CommandError(cmd) from e

    if result.stdout:
        logging.debug(result.stdout.strip())

    if return_output:
        return result.stdout.strip()
    return result
