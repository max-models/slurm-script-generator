from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from slurm_script_generator.pragmas import PragmaFactory
from slurm_script_generator.slurm_script import SlurmScript


def test_export_import():

    slurm_script = SlurmScript(
        error="./job.err.%j",
        nodes=2,
        output="./job.out.%j",
        disable_output_job_summary=True,
        ntasks_per_core=16,
        custom_commands=[
            "# Run simulation",
            "srun ./bin > run.out",
        ],
    )

    with NamedTemporaryFile(delete=True) as tmp:
        slurm_script.to_json(tmp.name)
        tmp.seek(0)
        imported = SlurmScript.from_json(tmp.name)
        print(imported)
        print(slurm_script)
        assert imported.pragmas[0] == slurm_script.pragmas[0]
        assert imported == slurm_script


# ---------------------------------------------------------------------------
# Building a script
# ---------------------------------------------------------------------------


def test_adding_the_same_pragma_twice_replaces_it():
    script = SlurmScript(nodes=1)

    script.add_pragma(PragmaFactory.create_pragma("nodes", 4))

    assert len(script.pragmas) == 1
    assert script.to_dict()["pragmas"] == {"nodes": 4}


def test_pragmas_are_grouped_by_category_in_order():
    script = SlurmScript(nodes=2, job_name="my_job", mem="4G")

    lines = [
        line for line in script.to_string(include_header=False).splitlines() if line
    ]
    headers = [line for line in lines if line.startswith("# Pragmas for")]

    assert "Job Config" in headers[0]
    assert "Core Node And Task Allocation" in headers[1]
    assert "Memory" in headers[2]


def test_pragmas_within_a_category_are_sorted_by_id():
    # Added in reverse order of pragma_id.
    script = SlurmScript(partition="gpu", job_name="my_job")

    generated = script.to_string(include_header=False)

    assert generated.index("--job-name") < generated.index("--partition")


def test_modules_are_deduplicated():
    script = SlurmScript(modules=["intel", "impi"])

    script.add_module("intel")

    assert script.modules == ["intel", "impi"]


def test_module_commands_are_generated():
    script = SlurmScript(modules=["intel/21.2.0"])

    generated = script.to_string(include_header=False)

    assert "module purge" in generated
    assert "module load intel/21.2.0" in generated
    assert "module list" in generated


def test_no_module_commands_without_modules():
    assert "module" not in SlurmScript(nodes=1).to_string(include_header=False)


def test_custom_commands_are_appended_in_order():
    script = SlurmScript(custom_commands=["first", "second"])

    generated = script.to_string(include_header=False)

    assert generated.index("first") < generated.index("second")


def test_inlined_script_is_added_as_custom_commands(tmp_path):
    path = tmp_path / "run.sh"
    path.write_text("cd $SLURM_SUBMIT_DIR\nsrun ./bin\n")

    script = SlurmScript(inlined_script=str(path))

    assert script.custom_commands == ["cd $SLURM_SUBMIT_DIR", "srun ./bin"]


def test_inlined_script_must_exist(tmp_path):
    with pytest.raises(AssertionError):
        SlurmScript(inlined_script=str(tmp_path / "missing.sh"))


def test_add_param_rejects_unknown_key():
    with pytest.raises(ValueError, match="Unknown parameter key"):
        SlurmScript().add_param("not_a_param", 1)


def test_add_param_sets_line_length():
    script = SlurmScript()

    script.add_param("line_length", 80)

    assert script.line_length == 80


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def test_script_starts_with_shebang():
    assert SlurmScript(nodes=1).to_string().startswith("#!/bin/bash\n")


def test_header_can_be_omitted():
    script = SlurmScript(nodes=1)

    assert "This script was generated using" in script.to_string(include_header=True)
    assert "This script was generated using" not in script.to_string(
        include_header=False
    )


def test_save_writes_the_script(tmp_path):
    path = tmp_path / "job.sh"

    SlurmScript(nodes=2).save(str(path))

    assert "#SBATCH --nodes=2" in path.read_text()


def test_read_script_reads_from_disk(tmp_path):
    path = tmp_path / "job.sh"
    SlurmScript(nodes=2, modules=["intel"]).save(str(path))

    read_back = SlurmScript.read_script(str(path))

    assert read_back.to_dict()["pragmas"] == {"nodes": "2"}
    assert read_back.modules == ["intel"]


def test_scripts_with_different_pragmas_are_not_equal():
    assert SlurmScript(nodes=1) != SlurmScript(nodes=2)


def test_script_is_not_equal_to_other_types():
    assert SlurmScript(nodes=1) != "not a script"


# ---------------------------------------------------------------------------
# Submitting
# ---------------------------------------------------------------------------


def test_submit_job_returns_the_job_id(tmp_path):
    path = tmp_path / "job.sh"
    completed = type(
        "Completed", (), {"returncode": 0, "stdout": "Submitted batch job 12345\n"}
    )

    with patch("subprocess.run", return_value=completed) as run:
        job_id = SlurmScript(nodes=1).submit_job(str(path))

    assert job_id == 12345
    run.assert_called_once_with(["sbatch", str(path)], capture_output=True, text=True)


def test_submit_job_raises_when_sbatch_fails(tmp_path):
    path = tmp_path / "job.sh"
    completed = type("Completed", (), {"returncode": 1, "stdout": "", "stderr": "boom"})

    with patch("subprocess.run", return_value=completed):
        with pytest.raises(RuntimeError, match="boom"):
            SlurmScript(nodes=1).submit_job(str(path))
