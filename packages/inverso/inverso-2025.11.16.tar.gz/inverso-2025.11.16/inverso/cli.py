"""Command line interface for inverting pair mappings helper tool."""

import argparse
import pathlib
import sys

from typing import Union  # py39 does not handle |

from inverso.api import invert
from inverso import (
    APP_ALIAS,
    APP_ENV,
    APP_NAME,
    DEBUG,
    JSON_FORMAT,
    VERSION,
    YAML_FORMAT,
)

JSON_SUFFIXES = set(['.json'])
YAML_SUFFIXES = set(['.yaml', '.yml'])
KNOWN_SUFFIXES = JSON_SUFFIXES | YAML_SUFFIXES


def parser_configured() -> argparse.ArgumentParser:
    """Return the configured argument parser."""
    parser = argparse.ArgumentParser(
        prog=APP_ALIAS,
        description=APP_NAME,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        'source_pos',
        nargs='?',
        metavar='SOURCE_FILE',
        help='JSON or YAML source as positional argument',
    )
    parser.add_argument(
        'target_pos',
        nargs='?',
        metavar='TARGET_FILE',
        help='JSON or YAML target as positional argument',
    )
    parser.add_argument(
        '--source',
        '-s',
        dest='source',
        metavar='FILE',
        help='JSON or YAML source',
    )
    parser.add_argument(
        '--target',
        '-t',
        dest='target',
        metavar='FILE',
        help='JSON or YAML target',
    )
    parser.add_argument(
        '--debug',
        '-d',
        dest='debug',
        default=None,  # not False, so we can distinguish environment variable overwrite
        action='store_true',
        help=f'work in debug mode (default: False), overwrites any environment variable {APP_ENV}_DEBUG value',
    )
    parser.add_argument(
        '--auto-serial',
        '-a',
        dest='auto_serial',
        default=False,
        action='store_true',
        help='auto-serial mode, rewrite incoming keys as 1-based auto-serial (default: False)',
    )
    parser.add_argument(
        '--marker-token',
        '-m',
        dest='marker_token',
        metavar='TOKEN',
        default='',
        help='if in auto-serial mode, marker token to be exempted (default: False)',
    )
    parser.add_argument(
        '--is-value',
        dest='marker_is_value',
        default=False,
        action='store_true',
        help='if marker token, then expect it as value insteadf of as key (default: False)',
    )
    parser.add_argument(
        '--generator-caveat',
        '-g',
        dest='generator_caveat',
        default=False,
        action='store_true',
        help='add a generator caveat as first pair to generated inverted map (default: False)',
    )
    parser.add_argument(
        '--preview',
        '-p',
        dest='preview',
        default=False,
        action='store_true',
        help='preview only (dry-run) reporting on what would be done (default: False)',
    )
    parser.add_argument(
        '--quiet',
        '-q',
        dest='quiet',
        default=False,
        action='store_true',
        help='work in quiet mode (default: False)',
    )
    parser.add_argument(
        '--version',
        '-V',
        dest='version',
        default=False,
        action='store_true',
        help='display version and exit',
    )

    return parser


def validate_source(options: argparse.Namespace, engine: argparse.ArgumentParser) -> str:
    """Validate the source given."""
    if not (options.source_pos or options.source):
        engine.error(
            'source path must be given - either as first positional argument or as value to the --source option'
        )

    if options.source_pos and options.source:
        engine.error(
            'source path given both as first positional argument and as value to the --source option - pick one'
        )

    if not options.source:
        options.source = options.source_pos

    if not pathlib.Path(options.source).is_file():
        engine.error(f'requested source ({options.source}) is not a file')

    source_suffix = pathlib.Path(options.source).suffix.lower()
    if source_suffix not in KNOWN_SUFFIXES:
        engine.error(
            f'requested source suffix ({source_suffix}) is not in known suffixes ({", ".join(sorted(KNOWN_SUFFIXES))})'
        )

    return source_suffix


def validate_target(options: argparse.Namespace, engine: argparse.ArgumentParser) -> str:
    """Validate the target given."""
    if not (options.target_pos or options.target):
        engine.error(
            'target path must be given - either as second positional argument or as value to the --target option'
        )

    if options.target_pos and options.target:
        engine.error(
            'target path given both as second positional argument and as value to the --target option - pick one'
        )

    if not options.target:
        options.target = options.target_pos

    target_suffix = pathlib.Path(options.target).suffix.lower()
    if target_suffix not in KNOWN_SUFFIXES:
        engine.error(
            f'requested target suffix ({target_suffix}) is not in known suffixes ({", ".join(sorted(KNOWN_SUFFIXES))})'
        )

    if pathlib.Path(options.target) == pathlib.Path(options.source):
        engine.error(
            'target path is identical with source path - cowardly giving up on the attempted in-place inversion'
        )

    return target_suffix


def parse_request(argv: list[str]) -> Union[int, argparse.Namespace]:
    """Parse the request vector into validated options."""
    parser = parser_configured()
    if not argv:
        parser.print_help()
        return 0

    options = parser.parse_args(argv)

    if options.version:
        print(VERSION)
        return 0

    # Ensure consistent request for verbosity
    if options.debug and options.quiet:
        parser.error('Cannot be quiet and debug - pick one')

    # Ensure hierarchical setting of debug: command line overwrites environment variable value
    if options.debug is None:
        options.debug = DEBUG

    # Quiet overwrites any debug requests
    if options.quiet:
        options.debug = False

    # Validate and derive the DSL values for source and target formats
    options.source_format = JSON_FORMAT if validate_source(options, engine=parser) in JSON_SUFFIXES else YAML_FORMAT
    options.target_format = JSON_FORMAT if validate_target(options, engine=parser) in JSON_SUFFIXES else YAML_FORMAT

    # Derive well-defined values for auto-serial mode related variables
    options.auto_serial_start = 1 if options.auto_serial else 0
    options.auto_serial_step = 1

    # Preview-only requested?
    if options.preview:
        print('Preview of inversion request (dry-run):')
        request = vars(options)
        for opt, val in request.items():
            print(f'  {opt}: {val}')
        return 0

    return options


def main(argv: Union[list[str], None] = None) -> int:
    """Delegate processing to functional module."""
    argv = sys.argv[1:] if argv is None else argv
    options = parse_request(argv)

    if isinstance(options, int):
        return 0
    return invert(request=options)
