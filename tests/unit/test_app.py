import pytest

from slurm_script_generator.main import generate_script
from slurm_script_generator.sbatch_parser import pragmas


def test_import_app():
    from slurm_script_generator.main import main

    print("slurm_script_generator imported")


def test_options():

    args = {"--nodes": 1, "--ntasks_per_node": 16}
    script = generate_script(args_dict=args, print_script=False)
    print(script)
    assert "#SBATCH --nodes 1" in script
    assert "#SBATCH --ntasks-per-node 16" in script


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
        "modules": modules,
        "--likwid": True,
        "--venv": venv_path,
        "--mem": mem,
        "--time": time,
    }
    script = generate_script(args_dict=script_params, print_script=False)

    assert f"#SBATCH --job-name {job_name}" in script
    assert f"#SBATCH --ntasks-per-node {tasks_per_node}" in script
    assert f"#SBATCH --nodes {nodes}" in script
    assert f"module load {' '.join(modules)}" in script


def test_examples():
    script_params = {}
    for p in pragmas:
        if p.example is not None:
            script_params[p.dest] = p.example

    script = generate_script(args_dict=script_params, print_script=False)

    print(script)

    for p in pragmas:
        if p.example is not None:
            assert f"#SBATCH {p.sbatch_flag} {p.example}" in script


if __name__ == "__main__":
    test_import_app()
    test_options()
