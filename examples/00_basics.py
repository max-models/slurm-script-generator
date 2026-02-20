from slurm_script_generator.slurm_script import SlurmScript

slurm_script = SlurmScript(
    nodes=2,
    ntasks_per_core=16,
    custom_commands=[
        "# Run simulation",
        "srun ./bin > run.out",
    ],
)

print(slurm_script)
