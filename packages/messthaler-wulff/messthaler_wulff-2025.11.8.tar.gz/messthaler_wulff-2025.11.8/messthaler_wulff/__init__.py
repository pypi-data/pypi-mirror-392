import argparse
import logging

import messthaler_wulff.mode_interactive as mode_interactive
import messthaler_wulff.mode_simulate as mode_simulate
import messthaler_wulff.mode_view as mode_view
from .data import fcc_transform
from .terminal_formatting import parse_color
from .version import program_version

log = logging.getLogger("messthaler_wulff")
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.DEBUG)
console.setFormatter(
    logging.Formatter(parse_color("{asctime} [ℂ3.{levelname:>5}ℂ.] ℂ4.{name}ℂ.: {message}"),
                      style="{", datefmt="%W %a %I:%M"))

PROGRAM_NAME = "messthaler-wulff"
DEFAULT_DATE_FORMAT = "%y/%b/%NAME"


def command_entry_point():
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Program was interrupted by user")


def parse_lattice(lattice):
    match lattice.lower():
        case "fcc":
            return fcc_transform()

    log.info(f"Unknown lattice name {lattice}, interpreting lattice as python code")

    transform = exec(f"import numpy as np;from math import *;{lattice}")

    log.info(f"Using result as lattice transform:\n{transform}")

    input()
    return transform


def main():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description="Wudduwudduwudduwudduwudduwudduwudduwuddu",
                                     allow_abbrev=True, add_help=True, exit_on_error=True)

    parser.add_argument('-v', '--verbose', action='store_true', help="Show more output")
    parser.add_argument("--version", action="store_true", help="Show the current version of the program")
    parser.add_argument("MODE", help="What subprogram to execute; Can be 'view' or 'simulate' or 'interactive'")
    parser.add_argument("--goal", help="The number of atoms to add initially", default="100")
    parser.add_argument("--dimension", default="3")
    parser.add_argument("--lattice", default="fcc")

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    if args.version:
        log.info(f"{PROGRAM_NAME} version {program_version}")
        return

    match args.MODE.lower():
        case 'view':
            mode_view.run_mode()
        case 'simulate':
            mode_simulate.run_mode(goal=int(args.goal))
        case 'interactive':
            mode_interactive.run_mode(goal=int(args.goal), dimension=int(args.dimension))
        case _:
            log.error(f"Unknown mode {args.MODE}. Must be one of 'view' or 'simulate'")
