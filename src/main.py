from helper import runner, sudo_keepalive


def main():
    print("--- Fedora Update Control Kit ---")

    # Start sudo keepalive to maintain privileges throughout execution
    sudo_keepalive.start()

    try:
        # Run all update commands
        _print_output(["sudo", "dnf", "update"])
        # Add more sudo commands here as needed

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        # Ensure keepalive is stopped
        sudo_keepalive.stop()

    return 0


def _print_output(cmd: list[str]):
    try:
        result = runner.run(cmd, True)
        print(result)
    except runner.CommandError as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    exit(main())
