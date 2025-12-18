from helper import runner


def main():
    print("--- Fedora Update Control Kit ---")
    _print_output(["python", "--version"])


def _print_output(cmd: list[str]):
    try:
        result = runner.run(cmd, True)
        print(result)
    except runner.CommandError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
