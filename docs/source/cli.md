---
engines:
- path: /opt/quarto/share/extension-subtrees/julia-engine/\_extensions/julia-engine/julia-engine.js
execute:
  echo: true
  output: true
title: Command Line Interface --- generate-slurm-script
toc-title: Table of contents
---

`generate-slurm-script` generates a SLURM batch script from command-line
flags. Every `#SBATCH` pragma SLURM supports has a corresponding flag,
so you can build, save, export, and reuse scripts without ever editing a
file by hand.

``` bash
generate-slurm-script [SBATCH flags] [--modules ...] [--custom-commands ...]
                      [--output FILE] [--export-json FILE] [--submit]
```

------------------------------------------------------------------------

## Basic usage

Print a script to stdout:

:::: cell
``` {.bash .cell-code}
generate-slurm-script --nodes 2 --ntasks-per-node 16 --time 04:00:00
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.2            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.2`     #
    ########################################################

    ########################################################
    # Pragmas for Time And Priority                        #
    #SBATCH --time=04:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
:::
::::

Save to a file with `--output`:

:::: cell
``` {.bash .cell-code}
generate-slurm-script --nodes 2 --ntasks-per-node 16 --time 04:00:00 \
    --output job.sh
cat job.sh
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.2            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.2`     #
    ########################################################

    ########################################################
    # Pragmas for Time And Priority                        #
    #SBATCH --time=04:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
:::
::::

Strip the generator header with `--no-header`:

:::: cell
``` {.bash .cell-code}
generate-slurm-script --nodes 2 --ntasks-per-node 16 --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
:::
::::

------------------------------------------------------------------------

## Key flags

All standard `#SBATCH` options are available directly as CLI flags. The
most commonly used ones are listed below.

### Job identity

  -----------------------------------------------------------------------------
  Flag                 Short             `#SBATCH` pragma  Description
  -------------------- ----------------- ----------------- --------------------
  `--job-name NAME`    `-J`              `--job-name`      Name shown in
                                                           `squeue` and used in
                                                           log filenames with
                                                           `%x`

  `--account NAME`     `-A`              `--account`       SLURM account to
                                                           charge compute time
                                                           to

  `--partition NAME`   `-p`              `--partition`     Target partition
                                                           (queue)

  `--qos NAME`         `-q`              `--qos`           Quality-of-service
                                                           level
  -----------------------------------------------------------------------------

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name my_simulation \
    --account proj_gpu \
    --partition gpu \
    --qos high \
    --nodes 1 --ntasks-per-node 4 --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=my_simulation                       # name of job
    #SBATCH --account=proj_gpu                             # charge job to specified account
    #SBATCH --partition=gpu                                # partition requested
    #SBATCH --qos=high                                     # quality of service
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    ########################################################
:::
::::

### Time and resources

  -----------------------------------------------------------------------
  Flag                    Short                   Description
  ----------------------- ----------------------- -----------------------
  `--time MINUTES`        `-t`                    Wall-clock time limit
                                                  (`HH:MM:SS` or minutes)

  `--nodes N`             `-N`                    Number of nodes

  `--ntasks N`            `-n`                    Total MPI tasks (spread
                                                  across however many
                                                  nodes fit)

  `--ntasks-per-node N`                           Tasks per node (use
                                                  with `--nodes`)

  `--cpus-per-task N`     `-c`                    CPU cores per task ---
                                                  set this for OpenMP or
                                                  multithreaded programs

  `--mem MB`                                      Memory per node in MB

  `--mem-per-cpu MB`                              Memory per CPU core in
                                                  MB
  -----------------------------------------------------------------------

:::: cell
``` {.bash .cell-code}
# Multithreaded job: 1 task, 8 cores, 16 GB RAM
generate-slurm-script \
    --job-name openmp_run \
    --ntasks 1 \
    --cpus-per-task 8 \
    --mem 16000 \
    --time 02:00:00 \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=openmp_run                          # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=02:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --ntasks=1                                     # number of processors required
    #SBATCH --cpus-per-task=8                              # number of cpus required per task
    #                                                      #
    # Pragmas for Memory                                   #
    #SBATCH --mem=16000                                    # minimum amount of real memory
    ########################################################
:::
::::

### GPU resources

  -----------------------------------------------------------------------
  Flag                                Description
  ----------------------------------- -----------------------------------
  `--gpus-per-node N`                 GPUs per node (generic, works on
                                      most clusters)

  `--gres LIST`                       Generic resources ---
                                      e.g. `gpu:a100:2` for 2 A100s

  `--constraint LIST`                 Node feature constraint ---
                                      e.g. `gpu` to select GPU nodes

  `--cpus-per-gpu N`                  CPU cores to allocate per GPU

  `--mem-per-gpu MEM`                 Memory per GPU

  `--nvmps`                           Enable NVIDIA MPS (for many small
                                      MPI tasks sharing GPUs)
  -----------------------------------------------------------------------

:::: cell
``` {.bash .cell-code}
# Single GPU job
generate-slurm-script \
    --job-name gpu_train \
    --ntasks 1 \
    --gres gpu:a100:1 \
    --cpus-per-task 8 \
    --mem 64000 \
    --time 08:00:00 \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=gpu_train                           # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=08:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --ntasks=1                                     # number of processors required
    #SBATCH --cpus-per-task=8                              # number of cpus required per task
    #                                                      #
    # Pragmas for Memory                                   #
    #SBATCH --mem=64000                                    # minimum amount of real memory
    #                                                      #
    # Pragmas for Generic Resources And Licenses           #
    #SBATCH --gres=gpu:a100:1                              # required generic resources
    ########################################################
:::
::::

### Output and working directory

By default SLURM writes stdout and stderr to `slurm-<jobid>.out`. Use
these flags to control where output goes:

  -----------------------------------------------------------------------
  Flag                    Short                   Description
  ----------------------- ----------------------- -----------------------
  `--stdout FILE`         `-o`                    Redirect stdout (`%j` =
                                                  job ID, `%x` = job
                                                  name)

  `--stderr FILE`         `-e`                    Redirect stderr

  `--chdir PATH`          `-D`                    Set the working
                                                  directory before the
                                                  script runs
  -----------------------------------------------------------------------

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name my_job \
    --nodes 1 --ntasks-per-node 4 \
    --stdout logs/my_job_%j.out \
    --stderr logs/my_job_%j.err \
    --chdir /scratch/my_project \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=my_job                              # name of job
    #                                                      #
    # Pragmas for Io And Directory                         #
    #SBATCH --chdir=/scratch/my_project                    # change working directory
    #SBATCH --stdout=logs/my_job_%j.out                    # File to redirect stdout (%%x=jobname, %%j=jobid)
    #SBATCH --stderr=logs/my_job_%j.err                    # File to redirect stderr (%%x=jobname, %%j=jobid)
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    ########################################################
:::
::::

### Email notifications

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name long_run \
    --nodes 4 --ntasks-per-node 16 \
    --mail-user user@example.com \
    --mail-type END \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=long_run                            # name of job
    #                                                      #
    # Pragmas for Notifications                            #
    #SBATCH --mail-user=user@example.com                   # who to send email notification for job state changes
    #SBATCH --mail-type=END                                # notify on state change
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
:::
::::

Valid `--mail-type` values: `BEGIN`, `END`, `FAIL`, `REQUEUE`, `ALL`,
`TIME_LIMIT`, `TIME_LIMIT_90`, `TIME_LIMIT_80`, `TIME_LIMIT_50`, `NONE`.

------------------------------------------------------------------------

## Modules

Load environment modules with `--modules`. `module purge` and
`module list` are added automatically:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --nodes 4 --ntasks-per-node 16 \
    --modules gcc/13 openmpi/5.0 \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
:::
::::

Multiple modules are loaded in the order given:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --nodes 1 --ntasks-per-node 8 \
    --modules gcc/13 cuda/12 cudnn/8 anaconda/3 \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 cuda/12 cudnn/8 anaconda/3          # modules
    module list                                            # List loaded modules
:::
::::

------------------------------------------------------------------------

## Custom commands

Everything after the `#SBATCH` pragmas and module loads is the body of
your script. Add arbitrary shell commands with `--custom-commands`:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name mpi_run \
    --nodes 2 --ntasks-per-node 16 \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands \
        'echo "Starting on $(hostname) at $(date)"' \
        'srun ./myprog --input data.h5 > results.out' \
        'echo "Done at $(date)"' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=mpi_run                             # name of job
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    echo "Starting on $(hostname) at $(date)"
    srun ./myprog --input data.h5 > results.out
    echo "Done at $(date)"
:::
::::

`--custom-command` (singular) adds a single command --- useful when
quoting is tricky:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --nodes 1 --ntasks-per-node 4 \
    --custom-command 'python train.py --epochs 100' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    ########################################################
    python train.py --epochs 100
:::
::::

Set environment variables in the script body by including `export`
statements:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --nodes 1 --ntasks-per-node 1 \
    --cpus-per-task 8 \
    --modules gcc/13 anaconda/3 \
    --custom-commands \
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK' \
        'srun python multithreaded_job.py' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=1                            # number of tasks to invoke on each node
    #SBATCH --cpus-per-task=8                              # number of cpus required per task
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 anaconda/3                          # modules
    module list                                            # List loaded modules
    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    srun python multithreaded_job.py
:::
::::

------------------------------------------------------------------------

## Inline scripts

`--inline-scripts` appends the full content of existing shell scripts
into the generated SLURM script. This is handy when you already have
setup or run scripts you want to reuse:

:::: cell
``` {.bash .cell-code}
# Create a small helper script
cat > setup_env.sh << 'EOF'
# Load project-specific environment
export MYAPP_DATA=/scratch/data
export MYAPP_RESULTS=/scratch/results
mkdir -p $MYAPP_RESULTS
EOF

generate-slurm-script \
    --nodes 2 --ntasks-per-node 8 \
    --modules gcc/13 openmpi/5.0 \
    --inline-scripts setup_env.sh \
    --custom-commands 'srun ./myprog' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    srun ./myprog
    # Load project-specific environment
    export MYAPP_DATA=/scratch/data
    export MYAPP_RESULTS=/scratch/results
    mkdir -p $MYAPP_RESULTS
:::
::::

------------------------------------------------------------------------

## Saving and reusing settings

### Save the script to a file

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name baseline \
    --nodes 4 --ntasks-per-node 16 \
    --time 12:00:00 \
    --account proj_hpc \
    --output baseline.sh
cat baseline.sh
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.2            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.2`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=baseline                            # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
:::
::::

### Export settings as JSON

`--export-json` saves all current settings to a JSON file so you can
reload and tweak them later --- without repeating every flag:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name baseline \
    --nodes 4 --ntasks-per-node 16 \
    --time 12:00:00 \
    --account proj_hpc \
    --modules gcc/13 openmpi/5.0 \
    --export-json baseline.json \
    --no-header
cat baseline.json
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=baseline                            # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules

    {
        "pragmas": {
            "job_name": "baseline",
            "account": "proj_hpc",
            "time": "12:00:00",
            "nodes": 4,
            "ntasks_per_node": 16
        },
        "modules": [
            "gcc/13",
            "openmpi/5.0"
        ],
        "custom_commands": []
    }
:::
::::

### Build new scripts from a JSON base

Override any setting by passing flags alongside `--input`. Anything not
overridden is inherited from the JSON:

:::: cell
``` {.bash .cell-code}
# Same settings, but scale to 8 nodes and rename the job
generate-slurm-script \
    --input baseline.json \
    --nodes 8 \
    --job-name big_run \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=big_run                             # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=8                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
:::
::::

This is especially useful for parameter studies --- keep a base JSON and
vary one or two things per run:

:::: cell
``` {.bash .cell-code}
# Short test run from the same base
generate-slurm-script \
    --input baseline.json \
    --nodes 1 \
    --time 00:30:00 \
    --job-name baseline_test \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=baseline_test                       # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=00:30:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
:::
::::

### Read pragmas from an existing script

`--read-script` parses an existing `#SBATCH` script and imports its
pragmas and commands. Use it to add new options to a script you received
from a colleague or downloaded from a cluster guide:

:::: cell
``` {.bash .cell-code}
# baseline.sh is the script we saved above; override job-name and add modules
generate-slurm-script \
    --read-script baseline.sh \
    --job-name updated_run \
    --modules python/3.11 \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=updated_run                         # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load python/3.11                                # modules
    module list                                            # List loaded modules
:::
::::

------------------------------------------------------------------------

## Submitting directly

Add `--submit` to write the script (requires `--output`) and immediately
call `sbatch` on it:

``` bash
generate-slurm-script \
    --job-name my_job \
    --nodes 2 --ntasks-per-node 16 \
    --time 04:00:00 \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands 'srun ./myprog > output.txt' \
    --output my_job.sh \
    --submit
```

------------------------------------------------------------------------

## Common job templates

### Serial (single-core) job

A sequential Python script using one CPU and minimal memory:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name python_serial \
    --ntasks 1 \
    --cpus-per-task 1 \
    --mem 2000 \
    --time 00:30:00 \
    --modules gcc/10 anaconda/3 \
    --custom-commands \
        'export OMP_NUM_THREADS=1' \
        'srun python3 my_script.py' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=python_serial                       # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=00:30:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --ntasks=1                                     # number of processors required
    #SBATCH --cpus-per-task=1                              # number of cpus required per task
    #                                                      #
    # Pragmas for Memory                                   #
    #SBATCH --mem=2000                                     # minimum amount of real memory
    ########################################################
    module purge                                           # Purge modules
    module load gcc/10 anaconda/3                          # modules
    module list                                            # List loaded modules
    export OMP_NUM_THREADS=1
    srun python3 my_script.py
:::
::::

### Multithreaded job (OpenMP / Python multiprocessing)

One task that uses multiple cores on a single shared node:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name openmp_job \
    --ntasks 1 \
    --cpus-per-task 16 \
    --mem 32000 \
    --time 02:00:00 \
    --modules gcc/13 \
    --custom-commands \
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK' \
        'srun ./openmp_program' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=openmp_job                          # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=02:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --ntasks=1                                     # number of processors required
    #SBATCH --cpus-per-task=16                             # number of cpus required per task
    #                                                      #
    # Pragmas for Memory                                   #
    #SBATCH --mem=32000                                    # minimum amount of real memory
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13                                     # modules
    module list                                            # List loaded modules
    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    srun ./openmp_program
:::
::::

### Pure MPI job

Multiple tasks spread across several full nodes:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name mpi_job \
    --nodes 8 \
    --ntasks-per-node 64 \
    --time 12:00:00 \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands 'srun ./mpi_program > output.txt' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=mpi_job                             # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=8                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=64                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    srun ./mpi_program > output.txt
:::
::::

### Hybrid MPI + OpenMP job

Each MPI task spawns multiple OpenMP threads --- common for modern HPC
codes:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name hybrid_job \
    --nodes 4 \
    --ntasks-per-node 4 \
    --cpus-per-task 16 \
    --time 08:00:00 \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands \
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK' \
        'export OMP_PLACES=cores' \
        'srun ./hybrid_program' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=hybrid_job                          # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=08:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    #SBATCH --cpus-per-task=16                             # number of cpus required per task
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    export OMP_PLACES=cores
    srun ./hybrid_program
:::
::::

### Single-GPU job

One GPU on a shared GPU node, with enough CPUs and RAM to feed it:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name gpu_train \
    --ntasks 1 \
    --gres gpu:a100:1 \
    --cpus-per-task 18 \
    --mem 125000 \
    --time 08:00:00 \
    --modules gcc/13 cuda/12 anaconda/3 \
    --custom-commands \
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK' \
        'srun python3 train.py --config config.yaml' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=gpu_train                           # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=08:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --ntasks=1                                     # number of processors required
    #SBATCH --cpus-per-task=18                             # number of cpus required per task
    #                                                      #
    # Pragmas for Memory                                   #
    #SBATCH --mem=125000                                   # minimum amount of real memory
    #                                                      #
    # Pragmas for Generic Resources And Licenses           #
    #SBATCH --gres=gpu:a100:1                              # required generic resources
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 cuda/12 anaconda/3                  # modules
    module list                                            # List loaded modules
    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    srun python3 train.py --config config.yaml
:::
::::

### Multi-GPU job (full node)

Four GPUs on a dedicated GPU node, one MPI task per GPU:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name multigpu_train \
    --nodes 1 \
    --constraint gpu \
    --gres gpu:a100:4 \
    --ntasks-per-node 4 \
    --cpus-per-task 18 \
    --time 12:00:00 \
    --modules gcc/13 cuda/12 openmpi/5.0 \
    --custom-commands \
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK' \
        'srun python3 train_ddp.py' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=multigpu_train                      # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    #SBATCH --cpus-per-task=18                             # number of cpus required per task
    #                                                      #
    # Pragmas for Generic Resources And Licenses           #
    #SBATCH --gres=gpu:a100:4                              # required generic resources
    #                                                      #
    # Pragmas for Node Constraints And Selection           #
    #SBATCH --constraint=gpu                               # specify a list of constraints
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 cuda/12 openmpi/5.0                 # modules
    module list                                            # List loaded modules
    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    srun python3 train_ddp.py
:::
::::

### Job array

Submit many similar jobs in one `sbatch` call. Each array element gets a
unique `$SLURM_ARRAY_TASK_ID`:

:::: cell
``` {.bash .cell-code}
generate-slurm-script \
    --job-name sweep \
    --array 0-9 \
    --nodes 1 \
    --ntasks-per-node 8 \
    --time 04:00:00 \
    --stdout logs/sweep_%A_%a.out \
    --stderr logs/sweep_%A_%a.err \
    --modules gcc/13 anaconda/3 \
    --custom-commands \
        'python run.py --config configs/config_${SLURM_ARRAY_TASK_ID}.yaml' \
    --no-header
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=sweep                               # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=04:00:00                                # time limit
    #                                                      #
    # Pragmas for Io And Directory                         #
    #SBATCH --stdout=logs/sweep_%A_%a.out                  # File to redirect stdout (%%x=jobname, %%j=jobid)
    #SBATCH --stderr=logs/sweep_%A_%a.err                  # File to redirect stderr (%%x=jobname, %%j=jobid)
    #                                                      #
    # Pragmas for Dependencies And Arrays                  #
    #SBATCH --array=0-9                                    # submit a job array
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 anaconda/3                          # modules
    module list                                            # List loaded modules
    python run.py --config configs/config_${SLURM_ARRAY_TASK_ID}.yaml
:::
::::

`%A` expands to the array job ID, `%a` to the element index.

### Job with a dependency

Run a post-processing job only after the main job succeeds:

``` bash
# Submit the main job and capture its ID
MAIN_ID=$(sbatch main_job.sh | awk '{print $NF}')

# Generate and submit the post-processing job, dependent on the main job
generate-slurm-script \
    --job-name postprocess \
    --dependency afterok:${MAIN_ID} \
    --nodes 1 --ntasks-per-node 4 \
    --time 01:00:00 \
    --custom-commands 'python postprocess.py --input results/' \
    --output postprocess.sh \
    --submit
```

`afterok` means the dependent job only starts if the parent exited
successfully. Other dependency types: `afterany` (regardless of exit
code), `afternotok` (only on failure), `after` (after the job starts).

------------------------------------------------------------------------

## Workflow: generate, export, iterate

A typical iterative workflow for developing and scaling up a job:

:::: cell
``` {.bash .cell-code}
# 1. Start with a quick test on 1 node
generate-slurm-script \
    --job-name sim_test \
    --nodes 1 --ntasks-per-node 8 \
    --time 00:15:00 \
    --account proj_hpc \
    --partition test \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands 'srun ./myprog --small-input > test.out' \
    --export-json sim_base.json \
    --output sim_test.sh
cat sim_test.sh
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.2            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.2`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=sim_test                            # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #SBATCH --partition=test                               # partition requested
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=00:15:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    srun ./myprog --small-input > test.out
:::
::::

:::: cell
``` {.bash .cell-code}
# 2. Scale up for the real run — inherit everything from the JSON,
#    override only what changes
generate-slurm-script \
    --input sim_base.json \
    --job-name sim_production \
    --nodes 16 \
    --time 12:00:00 \
    --partition main \
    --custom-commands 'srun ./myprog --full-input > production.out' \
    --output sim_production.sh
cat sim_production.sh
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.2            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.2`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=sim_production                      # name of job
    #SBATCH --account=proj_hpc                             # charge job to specified account
    #SBATCH --partition=main                               # partition requested
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=16                                     # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules
    srun ./myprog --small-input > test.out
    srun ./myprog --full-input > production.out
:::
::::

:::: cell
``` {.bash .cell-code}
# 3. A colleague wants the same setup with a different account and partition —
#    read the production script and override those two fields
generate-slurm-script \
    --read-script sim_production.sh \
    --account colleague_account \
    --partition gpu \
    --output colleague_job.sh
cat colleague_job.sh
```

::: {.cell-output .cell-output-stdout}
    #!/bin/bash
    ########################################################
    #            This script was generated using           #
    #             slurm-script-generator v0.3.2            #
    # https://github.com/max-models/slurm-script-generator #
    #      `pip install slurm-script-generator==0.3.2`     #
    ########################################################

    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=sim_production                      # name of job
    #SBATCH --account=colleague_account                    # charge job to specified account
    #SBATCH --partition=gpu                                # partition requested
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=12:00:00                                # time limit
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=16                                     # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0 # modules               # modules
    module list                                            # List loaded modules
    srun ./myprog --small-input > test.out
    srun ./myprog --full-input > production.out
:::
::::
