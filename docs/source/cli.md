# Command Line Interface


## Generate scripts

Generate a slurm script to `slurm_script.sh` with

``` bash
generate-slurm-script --nodes 1 --ntasks-per-node 16
```

    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.0            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.0`     #
    ########################################################

    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

To save the script to file `my_script.sh` use `--output`:

``` bash
generate-slurm-script --nodes 1 --ntasks-per-node 16 --output my_script.sh
```

Show the contents of the generated script:

``` bash
cat slurm_script.sh
```

    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.0            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.0`     #
    ########################################################

    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

Remove the header comment with `--no-header`:

``` bash
generate-slurm-script --nodes 1 --ntasks-per-node 16 --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

## Exporting and reading scripts

To export the settings to a json file you can use `--export-json`:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 16 --account my_account --export-json setup.json --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --account=my_account                           # charge job to specified account
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

Check the contents of the exported json file:

``` bash
cat setup.json
```

    {
        "pragmas": {
            "account": "my_account",
            "nodes": 2,
            "ntasks_per_node": 16
        },
        "modules": [],
        "custom_commands": []
    }

This json file can used as a basis for creating new scripts

``` bash
generate-slurm-script --input setup.json --ntasks-per-node 16 --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --account=my_account                           # charge job to specified account
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

### Add modules

Add modules with

``` bash
generate-slurm-script --input setup.json --ntasks-per-node 16 --modules gcc/13 openmpi/5.0 --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --account=my_account                           # charge job to specified account
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules

### Read from script

You can also read pragmas and commands from an existing script with
`--read-script`:

Let’s say you have a script `slurm_script.sh` with the following
content:

``` bash
cat slurm_script.sh
```

    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.0            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.0`     #
    ########################################################

    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

You can read the script and add extra pragmas (for example, changing the
job name with `--job-name NEW_JOB_NAME`) or commands to generate a new
script with

``` bash
generate-slurm-script --read-script slurm_script.sh --job-name NEW_JOB_NAME --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=NEW_JOB_NAME                        # name of job
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

## Realistic workflow example

Let’s walk through a typical workflow using the CLI to generate, export,
and reuse SLURM scripts and settings.

### 1. Generate and save a script

Generate a SLURM script and save it to a file:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 8 --job-name TEST_JOB --output my_script.sh
```

### 2. Export settings to JSON

Export the script settings to a JSON file for later reuse:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 8 --job-name TEST_JOB --export-json setup.json
```

    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.0            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.0`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=TEST_JOB                            # name of job
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################

### 3. Inspect the exported JSON

Print the contents of the exported JSON file:

``` bash
cat setup.json
```

    {
        "pragmas": {
            "job_name": "TEST_JOB",
            "nodes": 2,
            "ntasks_per_node": 8
        },
        "modules": [],
        "custom_commands": []
    }

### 4. Reuse settings from JSON

Create a new script using the exported settings, modifying parameters as
needed:

``` bash
generate-slurm-script --input setup.json --ntasks-per-node 16 --output new_script.sh
```

Show the contents of the new script:

``` bash
cat new_script.sh
```

    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.0            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.0`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=TEST_JOB                            # name of job
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

### 5. Add modules and custom commands

Add modules and custom commands to the script:

``` bash
generate-slurm-script --input setup.json --modules gcc/13 openmpi/5.0 --custom-commands 'echo "Starting job"' 'mpirun -n 16 ./bin > run.out' --output run_script.sh
```

Show the contents of the new script:

``` bash
cat run_script.sh
```

    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.0            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.0`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=TEST_JOB                            # name of job
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    echo "Starting job"
    mpirun -n 16 ./bin > run.out

### 6. Read and modify an existing script

Read pragmas and commands from an existing script, then override or add
new options:

``` bash
generate-slurm-script --read-script my_script.sh --job-name FINAL_JOB --modules python/3.10 --output final_script.sh
```

### 8. Combine multiple workflows

You can chain together several options for complex jobs:

``` bash
generate-slurm-script --nodes 4 --ntasks-per-node 32 --job-name BIG_JOB --modules gcc/13 cuda/12 --custom-commands 'echo "Preparing environment"' 'python run.py' --export-json big_job.json --output big_job.sh
```

### 9. Edit JSON and regenerate

Manually edit the exported JSON file (e.g., change job name or modules),
then regenerate a script:

``` bash
# Edit big_job.json in your editor, then:
generate-slurm-script --input big_job.json --output edited_job.sh
```

### 10. Add inline script

You can also add inline scripts to be included in the generated SLURM
script. First, create some example scripts:

``` bash
# Create setup_env.sh
cat <<'EOF' > setup_env.sh
#!/bin/bash
# Setup environment for SLURM job
module load gcc/13
module load openmpi/5.0
echo "Environment setup complete."
EOF
```

``` bash
# Create run_simulation.sh
cat <<'EOF' > run_simulation.sh
#!/bin/bash
# Run simulation for SLURM job
mpirun -n 16 ./bin > run.out
echo "Simulation finished."
EOF
```

Add inline scripts to the end of your SLURM script:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 8 --inline-scripts setup_env.sh run_simulation.sh --output inline_script.sh
```

Show the contents of the inline scripts:

``` bash
cat setup_env.sh
cat run_simulation.sh
```

    #!/bin/bash
    # Setup environment for SLURM job
    module load gcc/13
    module load openmpi/5.0
    echo "Environment setup complete."
    #!/bin/bash
    # Run simulation for SLURM job
    mpirun -n 16 ./bin > run.out
    echo "Simulation finished."

### 11. Print script to terminal

Print the generated script directly to the terminal (without saving):

``` bash
generate-slurm-script --nodes 1 --ntasks-per-node 4 --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    ########################################################

### 12. Use quiet mode for scripting

Suppress header and informational output for scripting or automation:

``` bash
generate-slurm-script --nodes 1 --ntasks-per-node 4 --no-header > minimal_script.sh
```

### 13. Advanced: Read, modify, and export

Read an existing script, modify pragmas, and export the new settings:

``` bash
generate-slurm-script --read-script slurm_script.sh --job-name UPDATED_JOB --modules python/3.10 --export-json updated_setup.json --output updated_script.sh
```
