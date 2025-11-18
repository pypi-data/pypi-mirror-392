import pathlib
import tempfile

import pytest  # type: ignore

import inverso.cli as cli
from inverso import ENCODING, ENC_ERRS, VERSION

FIXTURE = pathlib.Path('test/fixtures/')
USAGE_STARTS_WITH = 'usage: inverso [-h] [--source FILE] [--target FILE] [--debug] [--auto-serial]'

REPRODUCIBLE_PREVIEW_LINES = """Preview of inversion request (dry-run):
  source_pos: None
  target_pos: None
  source: test/fixtures/some-object.yml
  debug: False
  auto_serial: False
  marker_token:
  marker_is_value: False
  generator_caveat: False
  preview: True
  quiet: True
  version: False
  source_format: yaml
  target_format: yaml
  auto_serial_start: 0
  auto_serial_step: 1
""".split()

DYNAMIC_PREVIEW_LINE_STARTS_WITH = '  target:'
DYNAMIC_PREVIEW_LINE_ENDS_WITH = '/away-you-object-thing.yaml'


def test_main_ok_empty(capsys):
    cli.main([])
    out, err = capsys.readouterr()
    assert not err
    assert 'show this help message and exit' in out
    assert 'JSON' in out


def test_main_ok_smvp(capsys):
    with pytest.raises(SystemExit, match='0'):
        cli.main(['-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'show this help message and exit' in out
    assert 'JSON' in out


def test_parse_request_version(capsys):
    options = cli.parse_request(['--version'])
    assert options == 0
    out, err = capsys.readouterr()
    assert not err
    assert out.rstrip() == VERSION


def test_main_nok_no_files(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main(['-d'])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'inverso: error: source path must be given'
        ' - either as first positional argument or as value to the --source option'
    )
    assert not out


def test_main_nok_debug_and_quiet(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--debug', '--quiet'])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith('inverso: error: Cannot be quiet and debug - pick one')
    assert not out


def test_main_nok_no_target_file(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.json')])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: target path must be given - either as second positional argument or as value to the --target option'
    )
    assert not out


def test_main_nok_no_source_file(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--target', str(FIXTURE / 'not-present.json')])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: source path must be given - either as first positional argument or as value to the --source option'
    )
    assert not out


def test_main_nok_source_file_not_present(capsys):
    source = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--source', str(source)])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(f'error: requested source ({source}) is not a file')
    assert not out


def test_main_nok_source_file_has_unknown_suffix(capsys):
    target = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.jason'), str(target)])
    out, err = capsys.readouterr()
    # assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: requested source suffix (.jason) is not in known suffixes (.json, .yaml, .yml)'
    )
    assert not out


def test_main_nok_doubled_source_files(capsys):
    source = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--source', str(source), str(source)])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: source path given both as first positional argument and as value to the --source option - pick one'
    )
    assert not out


def test_main_nok_target_is_source_file(capsys):
    target = FIXTURE / 'empty.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.json'), str(target)])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: target path is identical with source path - cowardly giving up on the attempted in-place inversion'
    )
    assert not out


def test_main_nok_target_file_has_unknown_suffix(capsys):
    target = FIXTURE / 'empty-array.jason'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.json'), str(target)])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: requested target suffix (.jason) is not in known suffixes (.json, .yaml, .yml)'
    )
    assert not out


def test_main_nok_doubled_target_files(capsys):
    source = FIXTURE / 'empty.json'
    target = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(source), '--target', str(target), str(target)])
    out, err = capsys.readouterr()
    assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith(
        'error: target path given both as second positional argument and as value to the --target option - pick one'
    )
    assert not out


def test_main_nok_nonjective_source(capsys):
    source = FIXTURE / 'nonjective.json'
    target = FIXTURE / 'not-present.json'
    # with pytest.raises(SystemExit, match='1'):
    cli.main([str(source), '--target', str(target)])
    out, err = capsys.readouterr()
    # assert err.startswith(USAGE_STARTS_WITH)
    assert err.rstrip().endswith("Error: source has ambiguous values.\n- value='c' occurs for keys=['a', 'b']")
    assert not out


def test_main_ok_some_json_object_to_yaml(capsys):
    source = FIXTURE / 'some-object.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yml'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
        with open(target, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            result = handle.read()
        with open(FIXTURE / 'some-object.yml', 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            expected = handle.read()
        assert result == expected
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested inversion from json to yaml' in out
    assert "json_load(path=test/fixtures/some-object.json, options={'debug': True})" in out
    assert 'away-you-object-thing.yml' in out


def test_main_ok_auto_serialize_json_object_to_json_without_generator_caveat(capsys):
    marker = '4321'
    source = FIXTURE / f'auto-serial-marker-{marker}.json'
    target_ref = FIXTURE / f'auto-serial-marker-{marker}-inverted-without-generator-caveat.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.json'
        cli.main(['-am', marker, str(source), str(target)])
        assert target.is_file()
        with open(target, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            result = handle.read()
        with open(target_ref, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            expected = handle.read()
        assert result == expected
    out, err = capsys.readouterr()
    assert not err
    assert not out


def test_main_ok_auto_serialize_json_object_to_json_with_generator_caveat(capsys):
    marker = '4321'
    source = FIXTURE / f'auto-serial-marker-{marker}.json'
    target_ref = FIXTURE / f'auto-serial-marker-{marker}-inverted-with-generator-caveat.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.json'
        cli.main(['-agq', '-m', marker, str(source), str(target)])
        assert target.is_file()
        with open(target, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            result = handle.read()
        with open(target_ref, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            expected = handle.read()
        assert result == expected
    out, err = capsys.readouterr()
    assert not err
    assert not out


def test_main_ok_auto_serialize_json_object_no_marker_to_json_without_generator_caveat(capsys):
    source = FIXTURE / 'auto-serial-no-marker.json'
    target_ref = FIXTURE / 'auto-serial-no-marker-inverted-without-generator-caveat.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.json'
        cli.main(['-a', str(source), str(target)])
        assert target.is_file()
        with open(target, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            result = handle.read()
        with open(target_ref, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            expected = handle.read()
        assert result == expected
    out, err = capsys.readouterr()
    assert not err
    assert not out


def test_main_ok_auto_serialize_json_object_no_marker_to_json_with_generator_caveat(capsys):
    source = FIXTURE / 'auto-serial-no-marker.json'
    target_ref = FIXTURE / 'auto-serial-no-marker-inverted-with-generator-caveat.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.json'
        cli.main(['-agq', str(source), str(target)])
        assert target.is_file()
        with open(target, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            result = handle.read()
        with open(target_ref, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            expected = handle.read()
        assert result == expected
    out, err = capsys.readouterr()
    assert not err
    assert not out


def test_main_ok_some_yaml_object_to_json(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.json'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested inversion from yaml to json' in out
    assert "yaml_load(path=test/fixtures/some-object.yml, options={'debug': True})" in out
    assert 'away-you-object-thing.json' in out


def test_main_ok_some_json_object_to_json(capsys):
    source = FIXTURE / 'some-object.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.JSON'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested inversion from json to json' in out
    assert "json_load(path=test/fixtures/some-object.json, options={'debug': True})" in out
    assert 'away-you-object-thing.json' in out.lower()


def test_main_ok_some_yaml_object_to_yaml(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested inversion from yaml to yaml' in out
    assert "yaml_load(path=test/fixtures/some-object.yml, options={'debug': True})" in out
    assert 'away-you-object-thing.yaml' in out


def test_main_ok_target_from_option(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-d', '-s', str(source), '-t', str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested inversion from yaml to yaml' in out
    assert "yaml_load(path=test/fixtures/some-object.yml, options={'debug': True})" in out
    assert 'away-you-object-thing.yaml' in out


def test_main_ok_quiet(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-q', '-s', str(source), '-t', str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert not out


def test_main_ok_preview(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-qp', '-s', str(source), '-t', str(target)])
        assert not target.is_file()
    out, err = capsys.readouterr()
    assert not err
    out_lines = out.split()
    for out_line in out_lines:
        if out_line.startswith(DYNAMIC_PREVIEW_LINE_STARTS_WITH):
            assert out_line.endswith(DYNAMIC_PREVIEW_LINE_ENDS_WITH)
        else:
            out_line in REPRODUCIBLE_PREVIEW_LINES
