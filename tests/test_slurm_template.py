"""Tests for the `slurm-template` command and the built-in template registry."""

from unittest.mock import MagicMock, patch

import pytest

from slurm_script_generator.slurm_script import SlurmScript
from slurm_script_generator.slurm_template import main
from slurm_script_generator.templates import TEMPLATES, build_script

# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------


def test_all_templates_have_a_description():
    for name, template in TEMPLATES.items():
        assert template.description, f"{name} has no description"


def test_all_templates_have_commands():
    for name, template in TEMPLATES.items():
        assert template.commands, f"{name} has no placeholder command(s)"


def test_all_templates_build_a_valid_script():
    for name in TEMPLATES:
        script = build_script(name)
        assert isinstance(script, SlurmScript)
        # Should render without error and include the placeholder command.
        rendered = script.to_string()
        assert TEMPLATES[name].commands[0].split()[0].lstrip("./") in rendered.replace(
            "./", ""
        )


# ---------------------------------------------------------------------------
# build_script
# ---------------------------------------------------------------------------


def test_build_script_unknown_template_raises():
    with pytest.raises(KeyError, match="Unknown template"):
        build_script("bogus")


def test_build_script_applies_defaults():
    script = build_script("cpu")
    values = {p.arg_varname: p.value for p in script.pragmas}
    assert values["job_name"] == "cpu_job"
    assert values["nodes"] == 1


def test_build_script_overrides_defaults():
    script = build_script("cpu", overrides={"job_name": "custom", "nodes": 3})
    values = {p.arg_varname: p.value for p in script.pragmas}
    assert values["job_name"] == "custom"
    assert values["nodes"] == 3


def test_build_script_none_overrides_are_ignored():
    script = build_script("cpu", overrides={"job_name": None})
    values = {p.arg_varname: p.value for p in script.pragmas}
    assert values["job_name"] == "cpu_job"


def test_build_script_custom_commands_replace_placeholder():
    script = build_script("cpu", commands=["echo hi"])
    assert script.custom_commands == ["echo hi"]


def test_build_script_custom_modules_replace_default():
    script = build_script("cpu", modules=["gcc/12"])
    assert script.modules == ["gcc/12"]


def test_build_script_gpu_template_has_gpus_pragma():
    script = build_script("gpu")
    values = {p.arg_varname: p.value for p in script.pragmas}
    assert values["gpus"] == 1


def test_build_script_array_template_has_array_pragma():
    script = build_script("array")
    values = {p.arg_varname: p.value for p in script.pragmas}
    assert values["array"] == "1-10"


# ---------------------------------------------------------------------------
# CLI — slurm-template
# ---------------------------------------------------------------------------


def _run_main(argv, capsys):
    try:
        main(argv)
    except SystemExit:
        pass
    return capsys.readouterr()


def test_cli_list(capsys):
    out = _run_main(["--list"], capsys).out
    assert "cpu" in out
    assert "gpu" in out
    assert "Available templates" in out


def test_cli_requires_template(capsys):
    with pytest.raises(SystemExit):
        main([])


def test_cli_unknown_template_errors(capsys):
    with pytest.raises(SystemExit):
        main(["bogus"])
    err = capsys.readouterr().err
    assert "Unknown template" in err


def test_cli_prints_to_stdout_by_default(capsys):
    out = _run_main(["cpu"], capsys).out
    assert "#!/bin/bash" in out
    assert "./my_program" in out


def test_cli_overrides_job_name_and_time(capsys):
    out = _run_main(
        ["cpu", "--job-name", "my_job", "--time", "02:00:00"], capsys
    ).out
    assert "--job-name=my_job" in out
    assert "--time=02:00:00" in out


def test_cli_overrides_command(capsys):
    out = _run_main(["cpu", "--command", "python train.py"], capsys).out
    assert "python train.py" in out
    assert "./my_program" not in out


def test_cli_gpu_overrides_gpus(capsys):
    out = _run_main(["gpu", "--gpus", "2"], capsys).out
    assert "--gpus=2" in out


def test_cli_saves_to_output_file(tmp_path):
    path = tmp_path / "job.sh"
    main(["cpu", "--output", str(path)])
    content = path.read_text()
    assert "#!/bin/bash" in content
    assert "./my_program" in content


def test_cli_submit_requires_output(capsys):
    with pytest.raises(SystemExit):
        main(["cpu", "--submit"])
    err = capsys.readouterr().err
    assert "--submit requires --output" in err


def test_cli_submit_calls_sbatch(tmp_path):
    path = tmp_path / "job.sh"
    mock_result = MagicMock(returncode=0, stdout="Submitted batch job 42\n", stderr="")
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        main(["cpu", "--output", str(path), "--submit"])
    cmd = mock_run.call_args[0][0]
    assert cmd == ["sbatch", str(path)]
    assert path.exists()
