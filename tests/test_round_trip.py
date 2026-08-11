"""Round-trip tests: generating a script and parsing it back must not lose
information, and parsing must cope with scripts written by hand."""

import pytest

from slurm_script_generator.pragmas import (
    PragmaFactory,
    UnknownPragma,
    pragmas_ordered,
)
from slurm_script_generator.slurm_script import SlurmScript


def _round_trip(script: SlurmScript) -> SlurmScript:
    """Generate a script from *script* and parse the result back."""
    return SlurmScript.from_script(script.to_string(include_header=True))


@pytest.mark.parametrize(
    "pragma_cls", pragmas_ordered, ids=[cls.__name__ for cls in pragmas_ordered]
)
def test_every_pragma_survives_round_trip(pragma_cls):
    """Every pragma must generate a line that parses back into itself."""
    value = True if pragma_cls.action == "store_true" else "1"
    script = SlurmScript(pragmas=[pragma_cls(value)])

    parsed = _round_trip(script)

    assert parsed.to_dict() == script.to_dict()
    assert parsed == script


@pytest.mark.parametrize(
    "pragma_cls",
    [cls for cls in pragmas_ordered if cls.action == "store_true"],
    ids=[cls.__name__ for cls in pragmas_ordered if cls.action == "store_true"],
)
def test_switches_are_written_without_a_value(pragma_cls):
    """sbatch rejects `--hold=True`; switches must be written bare."""
    script = SlurmScript(pragmas=[pragma_cls(True)])

    line = f"#SBATCH {pragma_cls.dest}"
    generated = script.to_string(include_header=False)

    assert line in generated
    assert f"{line}=" not in generated


def test_switch_set_to_false_is_not_written():
    script = SlurmScript(pragmas=[PragmaFactory.create_pragma("hold", False)])

    assert "--hold" not in script.to_string(include_header=False)


@pytest.mark.parametrize("value", ["False", "false", "no", "0"])
def test_switch_accepts_false_strings(value):
    pragma = PragmaFactory.create_pragma("hold", value)

    assert pragma.value is False


@pytest.mark.parametrize("value", ["True", "true", "yes", "1"])
def test_switch_accepts_true_strings(value):
    pragma = PragmaFactory.create_pragma("hold", value)

    assert pragma.value is True


def test_switch_rejects_nonsense_value():
    with pytest.raises(ValueError):
        PragmaFactory.create_pragma("hold", "maybe")


def test_full_script_round_trip():
    script = SlurmScript(
        job_name="my_job",
        nodes="2",
        ntasks_per_node="16",
        time="12:00:00",
        hold=True,
        modules=["intel/21.2.0", "impi/2021.2"],
        custom_commands=["srun ./bin > run.out"],
    )

    parsed = _round_trip(script)

    assert parsed.to_dict() == script.to_dict()


def test_numeric_values_come_back_as_strings():
    """Known limitation: pragma values are not converted to their declared
    `type`, so a script round-trip turns ints into strings."""
    script = SlurmScript(nodes=2)

    parsed = _round_trip(script)

    assert script.to_dict()["pragmas"]["nodes"] == 2
    assert parsed.to_dict()["pragmas"]["nodes"] == "2"


def test_round_trip_via_json(tmp_path):
    script = SlurmScript(nodes=2, hold=True, custom_commands=["srun ./bin"])
    path = tmp_path / "script.json"

    script.to_json(str(path))

    assert SlurmScript.from_json(str(path)) == script


# ---------------------------------------------------------------------------
# Parsing scripts we did not write ourselves
# ---------------------------------------------------------------------------


def _parse_line(line: str) -> SlurmScript:
    return SlurmScript.from_script(f"#!/bin/bash\n{line}\n")


@pytest.mark.parametrize("line", ["#SBATCH --hold", "#SBATCH --contiguous"])
def test_parses_valueless_switch(line):
    """A bare switch used to crash the parser with a ValueError."""
    parsed = _parse_line(line)

    assert len(parsed.pragmas) == 1
    assert parsed.pragmas[0].value is True


@pytest.mark.parametrize(
    "line, expected",
    [
        ("#SBATCH --nodes=4", "4"),
        ("#SBATCH --nodes 4", "4"),
        ("#SBATCH -N 4", "4"),
        ("#SBATCH --nodes=4     # number of nodes", "4"),
        ("#SBATCH    --nodes=4", "4"),
    ],
)
def test_parses_value_forms(line, expected):
    parsed = _parse_line(line)

    assert parsed.to_dict()["pragmas"]["nodes"] == expected


def test_hash_inside_a_value_is_not_a_comment():
    parsed = _parse_line("#SBATCH --comment=a#b")

    assert parsed.to_dict()["pragmas"]["comment"] == "a#b"


def test_value_with_spaces_is_kept():
    parsed = _parse_line("#SBATCH --job-name my job")

    assert parsed.to_dict()["pragmas"]["job_name"] == "my job"


def test_unknown_option_is_preserved():
    """Options we do not model must survive read -> write unchanged."""
    parsed = _parse_line("#SBATCH --frobnicate=1")

    assert isinstance(parsed.pragmas[0], UnknownPragma)
    assert "#SBATCH --frobnicate=1" in parsed.to_string(include_header=False)


def test_unknown_valueless_option_is_preserved():
    parsed = _parse_line("#SBATCH --exclusive")

    generated = parsed.to_string(include_header=False)
    assert "#SBATCH --exclusive" in generated
    assert "--exclusive=" not in generated


def test_unknown_option_round_trips_through_json(tmp_path):
    script = _parse_line("#SBATCH --frobnicate=1")
    path = tmp_path / "script.json"
    script.to_json(str(path))

    assert SlurmScript.from_json(str(path)) == script


def test_known_pragma_without_a_value_is_an_error():
    with pytest.raises(ValueError, match="requires a value"):
        _parse_line("#SBATCH --nodes")


def test_empty_sbatch_line_is_ignored():
    parsed = _parse_line("#SBATCH")

    assert parsed.pragmas == []
