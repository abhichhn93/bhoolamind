"""BhoolamMind entrypoint wrapper."""

import sys


def _print_help():
    print(
        """usage: run.py [-h] [{interactive,batch-voice,summary,sync,test}]

BhoolamMind v1.5 CLI

positional arguments:
  {interactive,batch-voice,summary,sync,test}
                        Command to run (default: interactive)

options:
  -h, --help            show this help message and exit
"""
    )


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        _print_help()
        return

    from run_bhoolamind import main as run_main

    run_main()


if __name__ == "__main__":
    main()
