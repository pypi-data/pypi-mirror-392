"""Magical main module to allow python -m inverso calls."""

import sys

from inverso.cli import main

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
