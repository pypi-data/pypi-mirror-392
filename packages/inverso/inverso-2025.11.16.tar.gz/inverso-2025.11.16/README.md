# Inverso

Inverting pair mappings helper tool.

## Usage:

```bash
❯ inverso
usage: inverso [-h] [--source FILE] [--target FILE] [--debug] [--auto-serial] [--marker-token TOKEN] [--is-value]
               [--generator-caveat] [--preview] [--quiet] [--version]
               [SOURCE_FILE] [TARGET_FILE]

Inverting pair mappings helper tool.

positional arguments:
  SOURCE_FILE           JSON or YAML source as positional argument
  TARGET_FILE           JSON or YAML target as positional argument

options:
  -h, --help            show this help message and exit
  --source FILE, -s FILE
                        JSON or YAML source
  --target FILE, -t FILE
                        JSON or YAML target
  --debug, -d           work in debug mode (default: False), overwrites any environment variable INVERSO_DEBUG value
  --auto-serial, -a     auto-serial mode, rewrite incoming keys as 1-based auto-serial (default: False)
  --marker-token TOKEN, -m TOKEN
                        if in auto-serial mode, marker token to be exempted (default: False)
  --is-value            if marker token, then expect it as value insteadf of as key (default: False)
  --generator-caveat, -g
                        add a generator caveat as first pair to generated inverted map (default: False)
  --preview, -p         preview only (dry-run) reporting on what would be done (default: False)
  --quiet, -q           work in quiet mode (default: False)
  --version, -V         display version and exit```

## Version

```bash
❯ inverso --vesion
2025.7.19
```

## Status

Prototype.
