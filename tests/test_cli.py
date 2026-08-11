"""End-to-end tests of the `generate-slurm-script` command line interface."""

import json
from unittest.mock import patch

import pytest

from slurm_script_generator.main import main as cli_main
from slurm_script_generator.slurm_script import SlurmScript


def run_cli(*args):
    with patch("sys.argv", ["generate-slurm-script", *args]):
        cli_main()


def test_pragmas_are_printed_to_stdout(capsys):
    run_cli("--nodes", "2", "--ntasks-per-node", "16")

    out = capsys.readouterr().out
    assert "#SBATCH --nodes=2" in out
    assert "#SBATCH --ntasks-per-node=16" in out


def test_switch_is_printed_without_a_value(capsys):
    run_cli("--hold")

    out = capsys.readouterr().out
    assert "#SBATCH --hold" in out
    assert "--hold=" not in out


def test_switch_is_absent_when_not_given(capsys):
    run_cli("--nodes", "1")

    assert "--hold" not in capsys.readouterr().out


def test_short_flags_work(capsys):
    run_cli("-J", "my_job", "-N", "4")

    out = capsys.readouterr().out
    assert "#SBATCH --job-name=my_job" in out
    assert "#SBATCH --nodes=4" in out


def test_no_header(capsys):
    run_cli("--nodes", "1", "--no-header")

    assert "This script was generated using" not in capsys.readouterr().out


def test_output_path_writes_a_file(tmp_path):
    path = tmp_path / "job.sh"

    run_cli("--nodes", "2", "--output-path", str(path))

    assert "#SBATCH --nodes=2" in path.read_text()


def test_modules_and_custom_commands(capsys):
    run_cli(
        "--nodes",
        "1",
        "--modules",
        "intel",
        "impi",
        "--custom-command",
        "srun ./bin",
    )

    out = capsys.readouterr().out
    assert "module load intel impi" in out
    assert "srun ./bin" in out


def test_export_json(tmp_path, capsys):
    path = tmp_path / "job.json"

    run_cli("--nodes", "2", "--export-json", str(path))

    assert json.loads(path.read_text())["pragmas"] == {"nodes": 2}


def test_input_json_is_used_as_a_base(tmp_path, capsys):
    path = tmp_path / "job.json"
    SlurmScript(nodes=2, job_name="from_json").to_json(str(path))

    run_cli("--input", str(path), "--ntasks-per-node", "16")

    out = capsys.readouterr().out
    assert "#SBATCH --job-name=from_json" in out
    assert "#SBATCH --nodes=2" in out
    assert "#SBATCH --ntasks-per-node=16" in out


def test_read_script_is_used_as_a_base(tmp_path, capsys):
    path = tmp_path / "job.sh"
    SlurmScript(nodes=2, job_name="from_script", modules=["intel"]).save(str(path))

    run_cli("--read-script", str(path), "--ntasks-per-node", "16")

    out = capsys.readouterr().out
    assert "#SBATCH --job-name=from_script" in out
    assert "module load intel" in out
    assert "#SBATCH --ntasks-per-node=16" in out


def test_read_script_overrides_existing_pragma(tmp_path, capsys):
    path = tmp_path / "job.sh"
    SlurmScript(nodes=2).save(str(path))

    run_cli("--read-script", str(path), "--nodes", "8")

    out = capsys.readouterr().out
    assert "#SBATCH --nodes=8" in out
    assert "#SBATCH --nodes=2" not in out


def test_read_script_keeps_unknown_pragmas(tmp_path, capsys):
    path = tmp_path / "job.sh"
    path.write_text("#!/bin/bash\n#SBATCH --frobnicate=1\n#SBATCH --exclusive\n")

    run_cli("--read-script", str(path))

    out = capsys.readouterr().out
    assert "#SBATCH --frobnicate=1" in out
    assert "#SBATCH --exclusive" in out


def test_submit_requires_output_path(capsys):
    run_cli("--nodes", "1", "--submit")

    assert "requires --output-path" in capsys.readouterr().out


def test_submit_calls_submit_job(tmp_path):
    path = tmp_path / "job.sh"

    with patch("slurm_script_generator.main.SlurmScript.submit_job") as submit_job:
        run_cli("--nodes", "1", "--output-path", str(path), "--submit")

    submit_job.assert_called_once_with(path=str(path))


def test_invalid_choice_is_rejected(capsys):
    with pytest.raises(SystemExit) as excinfo:
        run_cli("--open-mode", "nonsense")

    assert excinfo.value.code != 0
