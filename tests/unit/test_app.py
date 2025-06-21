def test_import_app():
    from slurm_script_generator.main import main

    print("slurm_script_generator imported")


def test_options():
    from slurm_script_generator.main import generate_script

    args = {"nodes": 1, "ntasks_per_node": 16}
    script = generate_script(args_dict=args, print_script=False)
    print(script)
    assert "#SBATCH --nodes 1" in script
    assert "#SBATCH --ntasks-per-node 16" in script


if __name__ == "__main__":
    test_import_app()
    test_options()
