
import sys
import argparse
import platform

from chipiq import __version__
from chipiq.simiq import simiq

"""
Command-line interface for ChipIQ package.
"""

def setup_simiq_parser(parser, func):
    """Setup arguments for 'simiq' subcommand"""
    parser.add_argument(
        "file", 
        type=str,
        default="",
        help="filepath or URI of file to analyze (default: empty string)"
    )
    parser.add_argument(
        "--report",
        type=str,
        default="user_manual",
        help="type of report to generate (default: user_manual)"
    )
    parser.add_argument(
        "--from",
        dest="from_",
        type=int,
        default=0,
        help="first timestamp to report on (default: 0)"
    )
    parser.add_argument(
        "--signals",
        type=str,
        nargs='+',
        default=[".*"],
        help="signal names to include (default: all top-level signals)."
    )
    parser.set_defaults(func=func)
    return parser

def command_simiq(args):
    """Call 'simiq' with parsed arguments"""
    result = simiq(
        uri_or_filepath=args.file,
        report_type=args.report,
        from_timestamp=args.from_,
        signal_names=args.signals
    )

    print(result)

def main():
    """Main entry point for ChipIQ CLI"""
    parser = argparse.ArgumentParser(prog='chipiq', description='ChipIQ Command Line Interface')
    parser.add_argument(
        '--version',
        action="store_true",
        help="show version information and exit"
    )
    subparsers = parser.add_subparsers(dest='command', help='available commands')

    parser_simiq = subparsers.add_parser(
        'simiq', 
        help='analyze or debug simulation results'
    )
    setup_simiq_parser(parser_simiq, func=command_simiq)

    args = parser.parse_args()
    
    if args.version:
        print(f"ChipIQ: {__version__}")
        print(f"Python: {platform.python_version()}")
        print(f"Platform: {platform.platform()}")
        sys.exit(0)

    elif hasattr(args, 'func'):
        args.func(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
