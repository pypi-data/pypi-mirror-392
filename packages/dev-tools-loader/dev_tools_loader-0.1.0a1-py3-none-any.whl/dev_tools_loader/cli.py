import os
import argparse
from pathlib import Path

from .dev_tools_loader import DebugLog, DevToolsLoader
from dev_tools_loader import __version__


def main():
    parser = argparse.ArgumentParser(description='Development tools loader CLI')
    parser.add_argument('-j', '--json-path', help='Path to JSON config file (add -j config_example.json)', action='store', required=True)
    parser.add_argument('-o', '--output-path', help='Path to output dir (default <script_path>/output)', action='store', default=Path(os.getcwd()) / Path('output'))
    parser.add_argument('-c', '--clean', help='Clean output before load (default False)', action='store_true')
    parser.add_argument('--version', help='Show version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    try:
        dtl = DevToolsLoader(args.json_path, args.output_path)
        if args.clean:
            dtl.clean_output()
        dtl.pull()

    except KeyboardInterrupt:
        DebugLog.log(f'\n>>> Exit by user', color='yellow')

    except ValueError as e:
        DebugLog.log(f'\n>>> Value error: {e}', color='red')

    except RuntimeError as e:
        DebugLog.log(f'\n>>> Runtime error: {e}', color='red')
