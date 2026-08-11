"""Tests for the `slurm-alloc` command."""

import os
from unittest.mock import patch

import pytest

from slurm_script_generator.pragmas import PragmaFactory, UnknownPragma
from slurm_script_generator.salloc import (
    build_command,
    main,
    pragma_to_salloc_arg,
    salloc_args,
    script_body,
)
from slurm_script_generator.slurm_script import SlurmScript

SCRIPT = """#!/bin/bash
#SBATCH --job-name=test
#SBATCH --nodes=2
#SBATCH --time=12:00:00

module load intel
# a comment
srun ./bin > run.out
"""


@pytest.fixture
def script(tmp_path):
    path = tmp_path / "job.sh"
    path.write_text(SCRIPT)
    return str(path)


def completed(returncode=0):
    return type("Completed", (), {"returncode": returncode})


# ---------------------------------------------------------------------------
# Translating pragmas into salloc arguments
# ---------------------------------------------------------------------------


def test_pragma_with_a_value():
    pragma = PragmaFactory.create_pragma("nodes", 2)

    assert pragma_to_salloc_arg(pragma) == "--nodes=2"


def test_switch_has_no_value():
    pragma = PragmaFactory.create_pragma("hold", True)

    assert pragma_to_salloc_arg(pragma) == "--hold"


def test_unknown_valueless_pragma_has_no_value():
    assert pragma_to_salloc_arg(UnknownPragma("--x11")) == "--x11"


def test_supported_pragmas_are_passed_through():
    script = SlurmScript(nodes=2, time="1:00:00")

    args, dropped = salloc_args(script)

    assert args == ["--time=1:00:00", "--nodes=2"]
    assert dropped == []


@pytest.mark.parametrize(
    "key, value",
    [("output", "job.out"), ("error", "job.err"), ("array", "1-4")],
)
def test_sbatch_only_pragmas_are_dropped(key, value):
    script = SlurmScript(pragmas=[PragmaFactory.create_pragma(key, value)])

    args, dropped = salloc_args(script)

    assert args == []
    assert dropped == [PragmaFactory.get_pragma_cls(key).dest]


def test_pragmas_unknown_to_this_library_are_dropped():
    script = SlurmScript(pragmas=[UnknownPragma("--frobnicate", "1")])

    args, dropped = salloc_args(script)

    assert args == []
    assert dropped == ["--frobnicate"]


# ---------------------------------------------------------------------------
# Extracting the body
# ---------------------------------------------------------------------------


def test_script_body_drops_shebang_and_pragmas():
    body = script_body(SCRIPT)

    assert body.startswith("module load intel")
    assert "#SBATCH" not in body
    assert "#!/bin/bash" not in body


def test_script_body_keeps_comments_verbatim():
    assert "# a comment" in script_body(SCRIPT)


def test_script_body_of_a_pragma_only_script():
    assert script_body("#!/bin/bash\n#SBATCH --nodes=2\n") == ""


def test_script_body_keeps_indentation_and_heredocs():
    text = "#!/bin/bash\n#SBATCH --nodes=1\ncat <<EOF\n  indented # not a pragma\nEOF\n"

    assert script_body(text) == "cat <<EOF\n  indented # not a pragma\nEOF"


# ---------------------------------------------------------------------------
# Building the command
# ---------------------------------------------------------------------------


def test_build_command_without_run(script, capsys):
    command, body = build_command(script)

    assert command == ["salloc", "--job-name=test", "--time=12:00:00", "--nodes=2"]
    assert body is None


def test_build_command_with_run(script):
    _, body = build_command(script, run=True)

    assert body == "module load intel\n# a comment\nsrun ./bin > run.out"


def test_build_command_appends_extra_args(script):
    command, _ = build_command(script, extra_args=["--x11"])

    assert command[-1] == "--x11"


def test_dropped_options_are_reported(tmp_path, capsys):
    path = tmp_path / "job.sh"
    path.write_text("#!/bin/bash\n#SBATCH --nodes=1\n#SBATCH --output=job.out\n")

    build_command(str(path))

    assert "--output" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Command line interface
# ---------------------------------------------------------------------------


def test_dry_run_prints_the_command(script, capsys):
    assert main([script, "--dry-run"]) == 0

    assert (
        capsys.readouterr().out.strip()
        == "salloc --job-name=test --time=12:00:00 --nodes=2"
    )


def test_dry_run_shows_the_body(script, capsys):
    main([script, "--run", "--dry-run"])

    out = capsys.readouterr().out
    assert "bash '<script>'" in out
    assert "srun ./bin > run.out" in out


def test_dry_run_does_not_run_salloc(script):
    with patch("subprocess.run") as run:
        main([script, "--dry-run"])

    run.assert_not_called()


def test_runs_salloc(script):
    with patch("subprocess.run", return_value=completed()) as run:
        assert main([script]) == 0

    run.assert_called_once_with(
        ["salloc", "--job-name=test", "--time=12:00:00", "--nodes=2"]
    )


def test_returns_the_salloc_exit_code(script):
    with patch("subprocess.run", return_value=completed(3)):
        assert main([script]) == 3


def test_arguments_after_a_double_dash_go_to_salloc(script):
    with patch("subprocess.run", return_value=completed()) as run:
        main([script, "--", "--x11", "--mem=8G"])

    assert run.call_args[0][0][-2:] == ["--x11", "--mem=8G"]


def test_our_own_options_are_not_passed_to_salloc(script):
    """--run after the script path must not be swallowed as a salloc argument."""
    with patch("subprocess.run", return_value=completed()) as run:
        main([script, "--run"])

    command = run.call_args[0][0]
    assert "--run" not in command
    assert command[-2] == "bash"


def test_run_writes_the_body_to_a_script(script):
    seen = {}

    def fake_run(command, *args, **kwargs):
        seen["path"] = command[-1]
        seen["content"] = open(command[-1]).read()
        return completed()

    with patch("subprocess.run", side_effect=fake_run):
        main([script, "--run"])

    assert seen["content"] == (
        "#!/bin/bash\nmodule load intel\n# a comment\nsrun ./bin > run.out\n"
    )
    assert not os.path.exists(seen["path"]), "temporary script was not cleaned up"


def test_temporary_script_is_removed_when_salloc_fails(script):
    seen = {}

    def fake_run(command, *args, **kwargs):
        seen["path"] = command[-1]
        raise KeyboardInterrupt

    with patch("subprocess.run", side_effect=fake_run):
        with pytest.raises(KeyboardInterrupt):
            main([script, "--run"])

    assert not os.path.exists(seen["path"])


def test_run_without_any_commands_is_an_error(tmp_path, capsys):
    path = tmp_path / "job.sh"
    path.write_text("#!/bin/bash\n#SBATCH --nodes=2\n")

    assert main([str(path), "--run"]) == 1
    assert "no commands" in capsys.readouterr().err


def test_missing_script_is_an_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as excinfo:
        main([str(tmp_path / "nope.sh")])

    assert excinfo.value.code == 2
    assert "No such script" in capsys.readouterr().err


def test_missing_salloc_is_reported(script, capsys):
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert main([script]) == 127

    assert "salloc not found" in capsys.readouterr().err
