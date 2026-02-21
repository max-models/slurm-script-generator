from tempfile import NamedTemporaryFile

from slurm_script_generator.slurm_script import SlurmScript


def test_export_import():

    slurm_script = SlurmScript(
        nodes=2,
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
