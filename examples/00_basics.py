from slurm_script_generator.pragmas import Nodes, Ntasks_per_node
from slurm_script_generator.slurm_script import SlurmScript

slurm_script = SlurmScript(
    nodes=2,
    ntasks_per_core=16,
    custom_command="mpirun -n 4 ./bin > run.out",
)

print(slurm_script)
