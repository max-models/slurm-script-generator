import pytest

# from slurm_script_generator.main import generate_script
from slurm_script_generator.pragmas import pragma_dict
from slurm_script_generator.slurm_script import SlurmScript


def test_import_app():
    from slurm_script_generator.main import main

    print("slurm_script_generator imported")


def test_options():

    args = {"--nodes": 1, "--ntasks_per_node": 16}
    pragmas = []
    for key, item in args.items():
        pragmas.append(pragma_dict[key](item))
    slurm_script = SlurmScript(pragmas=pragmas)
    script = slurm_script.generate_script()
    assert "#SBATCH --nodes=1" in script
    assert "#SBATCH --ntasks-per-node=16" in script


@pytest.mark.parametrize("job_name", ["test_job1", "test_job2"])
@pytest.mark.parametrize("tasks_per_node", [16, 32, 48])
@pytest.mark.parametrize("nodes", [1, 2, 3, 4])
@pytest.mark.parametrize(
    "modules",
    [
        [
            "gcc/12",
            "openmpi/4.1",
            "anaconda/3/2023.03",
            "git/2.43",
            "pandoc/3.1",
            "likwid/5.2",
        ]
    ],
)
@pytest.mark.parametrize("venv_path", ["~/virtual_envs/env_slurm"])
@pytest.mark.parametrize("mem", ["25GB"])
@pytest.mark.parametrize("time", ["00:45:00"])
def test_default_script(job_name, tasks_per_node, nodes, modules, venv_path, mem, time):
    """Tests a typical script format."""
    script_params = {
        "--job_name": job_name,
        "--ntasks_per_node": tasks_per_node,
        "--nodes": nodes,
        "--mem": mem,
        "--time": time,
    }
    pragmas = []
    for key, item in script_params.items():
        pragmas.append(pragma_dict[key](item))

    # Generate script
    slurm_script = SlurmScript(
        pragmas=pragmas,
        custom_command="mpirun -n 4 ./bin > run.out",
        modules=modules,
        likwid=True,
        venv=venv_path,
    )
    script = slurm_script.generate_script()

    assert f"#SBATCH --job-name={job_name}" in script
    assert f"#SBATCH --ntasks-per-node={tasks_per_node}" in script
    assert f"#SBATCH --nodes={nodes}" in script
    assert f"module load {' '.join(modules)}" in script
    assert "mpirun -n 4 ./bin > run.out" in script


def test_examples():
    pragmas = []
    for key, pragma in pragma_dict.items():
        if pragma.example is not None:
            pragmas.append(pragma(pragma.example))

    slurm_script = SlurmScript(pragmas=pragmas)
    script = slurm_script.generate_script()

    for key, pragma in pragma_dict.items():
        if pragma.example is not None:
            assert f"#SBATCH {pragma.dest.replace('_','-')}" in script


if __name__ == "__main__":
    test_import_app()
    test_options()
