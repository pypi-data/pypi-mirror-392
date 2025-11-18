"""Inverting pair mappings API for opinionated transforms."""

import argparse
import sys

from muuntuu.implementation import json_dump, json_load, yaml_dump, yaml_load  # type: ignore
from inverso.implementation import nonjective, process
from inverso import GENERATOR_CAVEAT_KEY, GENERATOR_CAVEAT_VALUE, JSON_FORMAT, LOG_AMBIGUITY


def invert(request: argparse.Namespace) -> int:
    """Invert between and within the known formats."""
    _ = request.debug and print('Debug mode requested.')

    load_source = json_load if request.source_format == JSON_FORMAT else yaml_load
    dump_source = json_dump if request.source_format == JSON_FORMAT else yaml_dump
    dump_target = json_dump if request.target_format == JSON_FORMAT else yaml_dump

    _ = request.debug and print(f'Requested inversion from {request.source_format} to {request.target_format}')
    auto_serial = request.auto_serial_start
    cleansed: dict[str, str] = {}
    for k, v in load_source(request.source, options={'debug': request.debug}).items():
        key, value, seen = process(k, v, auto_serial, request.marker_token, request.marker_is_value)
        cleansed[key] = value
        if auto_serial:
            if not request.marker_token or not seen:
                auto_serial += request.auto_serial_step

    dump_source(cleansed, request.source, options={'debug': request.debug})

    if findings := nonjective(cleansed):
        print(LOG_AMBIGUITY, file=sys.stderr)
        for finding in findings:
            print(f'- {finding}', file=sys.stderr)
        return 1

    inverted = {v: k for k, v in cleansed.items()}
    ordered = {GENERATOR_CAVEAT_KEY: GENERATOR_CAVEAT_VALUE} if request.generator_caveat else {}
    for k in sorted(inverted):
        ordered[k] = inverted[k]

    dump_target(ordered, request.target, options={'debug': request.debug})

    return 0
