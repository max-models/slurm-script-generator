def test_import_app():
    from slurm_script_generator.main import main

    print("slurm_script_generator imported")


def test_options():
    from slurm_script_generator.main import generate_script

    args = {}
    generate_script(sbatch_args=args)


if __name__ == "__main__":
    test_import_app()
