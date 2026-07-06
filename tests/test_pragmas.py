from slurm_script_generator.pragmas import PragmaFactory


def test_pragma_factory():
    pragma = PragmaFactory.create_pragma("nodes", 2)
    assert pragma.flags == ["-N", "--nodes"]
    assert pragma.dest == "--nodes"
    assert pragma.type is int
    assert pragma.value == 2


def test_pragma_var_names():
    pragmas = PragmaFactory.pragmas
    for key, pragma_cls in pragmas.items():
        assert pragma_cls.arg_varname == key, (
            f"Pragma arg_varname '{pragma_cls.arg_varname}' "
            + f"does not match key '{key}'"
        )
        assert pragma_cls.arg_varname == pragma_cls.__name__.lower(), (
            f"Pragma arg_varname '{pragma_cls.arg_varname}' "
            + f"does not match class name '{pragma_cls.__name__}'"
        )


def test_pragma_serialization():
    pragma = PragmaFactory.create_pragma("nodes", 3)
    d = pragma.to_dict()
    assert isinstance(d, dict)
    assert list(d.keys())[0] == "nodes"
    assert list(d.values())[0] == 3
    # Re-create from dict
    key, value = list(d.items())[0]
    pragma2 = PragmaFactory.create_pragma(key, value)
    assert pragma2.value == 3
    assert pragma2.dest == "--nodes"


def test_invalid_pragma_key():
    import pytest

    with pytest.raises(ValueError):
        PragmaFactory.create_pragma("notarealpragma", "1")


def test_all_pragmas_have_flags_and_dest():
    for _, pragma_cls in PragmaFactory.pragmas.items():
        pragma = pragma_cls("test")
        assert hasattr(pragma, "flags")
        assert hasattr(pragma, "dest")
        assert isinstance(pragma.flags, list)
        assert isinstance(pragma.dest, str)


def test_pragma_type_and_value():
    pragma = PragmaFactory.create_pragma("nodes", 4)
    assert pragma.type is int
    assert isinstance(pragma.value, int)
    pragma = PragmaFactory.create_pragma("account", "max")
    assert pragma.type is str
    assert isinstance(pragma.value, str)


def test_io_pragmas():
    output = PragmaFactory.create_pragma("output", "./job.out.%j")
    assert output.flags == ["--output", "-o"]
    assert output.dest == "--output"
    assert output.arg_varname == "output"
    assert output.value == "./job.out.%j"

    error = PragmaFactory.create_pragma("error", "./job.err.%j")
    assert error.flags == ["--error", "-e"]
    assert error.dest == "--error"
    assert error.arg_varname == "error"
    assert error.value == "./job.err.%j"

    summary = PragmaFactory.create_pragma("disable_output_job_summary", True)
    assert summary.flags == ["--disable-output-job-summary"]
    assert summary.dest == "--disable-output-job-summary"
    assert summary.arg_varname == "disable_output_job_summary"
