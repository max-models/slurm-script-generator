from slurm_script_generator.pragmas import PragmaFactory


def test_pragma_factory():
    pragma = PragmaFactory.create_pragma("nodes", 2)
    assert pragma.flags == ["-N", "--nodes"]
    assert pragma.dest == "--nodes"
    assert pragma.type == int
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
