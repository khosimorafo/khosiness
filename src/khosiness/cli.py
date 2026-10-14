import argparse

from . import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kness",
        description="khosiness — personal agentic harness",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="show the khosiness version",
    )
    args = parser.parse_args()

    if args.version:
        print(f"khosiness {__version__}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
