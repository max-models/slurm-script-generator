from slurm_script_generator.pragmas import Nodes, Ntasks_per_node
from slurm_script_generator.slurm_script import SlurmScript

slurm_script = SlurmScript(
    custom_command="mpirun -n 4 ./bin > run.out",
)

slurm_script.add_pragma(Nodes(value=2))
slurm_script.add_pragma(Ntasks_per_node(value=16))

print(slurm_script)
