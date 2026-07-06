# Command Line Interface — generate-slurm-script


`generate-slurm-script` generates a SLURM batch script from command-line
flags. Every `#SBATCH` pragma SLURM supports has a corresponding flag,
so you can build, save, export, and reuse scripts without ever editing a
file by hand.

``` bash
generate-slurm-script [SBATCH flags] [--modules ...] [--custom-commands ...]
                      [--output-path FILE] [--export-json FILE] [--submit]
```

------------------------------------------------------------------------

## Basic usage

Print a script:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 16 --time 04:00:00
```

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

Save to a file with `--output-path`:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 16 --time 04:00:00 \
    --output-path job.sh
cat job.sh
```

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

Strip the generator header with `--no-header`:

``` bash
generate-slurm-script --nodes 2 --ntasks-per-node 16 --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################

------------------------------------------------------------------------

## Key flags

All standard `#SBATCH` options are available directly as CLI flags. The
most commonly used ones are listed below.

### Job identity

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th>Flag</th>
<th>Short</th>
<th><code>#SBATCH</code> pragma</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>--job-name NAME</code></td>
<td><code>-J</code></td>
<td><code>--job-name</code></td>
<td>Name shown in <code>squeue</code> and used in log filenames with
<code>%x</code></td>
</tr>
<tr>
<td><code>--account NAME</code></td>
<td><code>-A</code></td>
<td><code>--account</code></td>
<td>SLURM account to charge compute time to</td>
</tr>
<tr>
<td><code>--partition NAME</code></td>
<td><code>-p</code></td>
<td><code>--partition</code></td>
<td>Target partition (queue)</td>
</tr>
<tr>
<td><code>--qos NAME</code></td>
<td><code>-q</code></td>
<td><code>--qos</code></td>
<td>Quality-of-service level</td>
</tr>
</tbody>
</table>

``` bash
generate-slurm-script \
    --job-name my_simulation \
    --account proj_gpu \
    --partition gpu \
    --qos high \
    --nodes 1 --ntasks-per-node 4 --no-header
```

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

### Time and resources

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr>
<th>Flag</th>
<th>Short</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>--time MINUTES</code></td>
<td><code>-t</code></td>
<td>Wall-clock time limit (<code>HH:MM:SS</code> or minutes)</td>
</tr>
<tr>
<td><code>--nodes N</code></td>
<td><code>-N</code></td>
<td>Number of nodes</td>
</tr>
<tr>
<td><code>--ntasks N</code></td>
<td><code>-n</code></td>
<td>Total MPI tasks (spread across however many nodes fit)</td>
</tr>
<tr>
<td><code>--ntasks-per-node N</code></td>
<td></td>
<td>Tasks per node (use with <code>--nodes</code>)</td>
</tr>
<tr>
<td><code>--cpus-per-task N</code></td>
<td><code>-c</code></td>
<td>CPU cores per task — set this for OpenMP or multithreaded
programs</td>
</tr>
<tr>
<td><code>--mem MB</code></td>
<td></td>
<td>Memory per node in MB</td>
</tr>
<tr>
<td><code>--mem-per-cpu MB</code></td>
<td></td>
<td>Memory per CPU core in MB</td>
</tr>
</tbody>
</table>

``` bash
# Multithreaded job: 1 task, 8 cores, 16 GB RAM
generate-slurm-script \
    --job-name openmp_run \
    --ntasks 1 \
    --cpus-per-task 8 \
    --mem 16000 \
    --time 02:00:00 \
    --no-header
```

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

### GPU resources

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr>
<th>Flag</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>--gpus-per-node N</code></td>
<td>GPUs per node (generic, works on most clusters)</td>
</tr>
<tr>
<td><code>--gres LIST</code></td>
<td>Generic resources — e.g. <code>gpu:a100:2</code> for 2 A100s</td>
</tr>
<tr>
<td><code>--constraint LIST</code></td>
<td>Node feature constraint — e.g. <code>gpu</code> to select GPU
nodes</td>
</tr>
<tr>
<td><code>--cpus-per-gpu N</code></td>
<td>CPU cores to allocate per GPU</td>
</tr>
<tr>
<td><code>--mem-per-gpu MEM</code></td>
<td>Memory per GPU</td>
</tr>
<tr>
<td><code>--nvmps</code></td>
<td>Enable NVIDIA MPS (for many small MPI tasks sharing GPUs)</td>
</tr>
</tbody>
</table>

``` bash
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

### Output, error, and working directory

By default SLURM writes output and error to `slurm-<jobid>.out`. Use
these flags to control where job output goes:

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr>
<th>Flag</th>
<th>Short</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>--output FILE</code></td>
<td><code>-o</code></td>
<td>Redirect output (<code>%j</code> = job ID, <code>%x</code> = job
name)</td>
</tr>
<tr>
<td><code>--error FILE</code></td>
<td><code>-e</code></td>
<td>Redirect error</td>
</tr>
<tr>
<td><code>--chdir PATH</code></td>
<td><code>-D</code></td>
<td>Set the working directory before the script runs</td>
</tr>
</tbody>
</table>

``` bash
generate-slurm-script \
    --job-name my_job \
    --nodes 1 --ntasks-per-node 4 \
    --output logs/my_job_%j.out \
    --error logs/my_job_%j.err \
    --chdir /scratch/my_project \
    --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=my_job                              # name of job
    #                                                      #
    # Pragmas for Io And Directory                         #
    #SBATCH --chdir=/scratch/my_project                    # change working directory
    #SBATCH --output=logs/my_job_%j.out                    # File to redirect output (%%x=jobname, %%j=jobid)
    #SBATCH --error=logs/my_job_%j.err                     # File to redirect error (%%x=jobname, %%j=jobid)
    #                                                      #
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    ########################################################

### Email notifications

``` bash
generate-slurm-script \
    --job-name long_run \
    --nodes 4 --ntasks-per-node 16 \
    --mail-user user@example.com \
    --mail-type END \
    --no-header
```

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

Valid `--mail-type` values: `BEGIN`, `END`, `FAIL`, `REQUEUE`, `ALL`,
`TIME_LIMIT`, `TIME_LIMIT_90`, `TIME_LIMIT_80`, `TIME_LIMIT_50`, `NONE`.

------------------------------------------------------------------------

## Modules

Load environment modules with `--modules`. `module purge` and
`module list` are added automatically:

``` bash
generate-slurm-script \
    --nodes 4 --ntasks-per-node 16 \
    --modules gcc/13 openmpi/5.0 \
    --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=4                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 openmpi/5.0                         # modules
    module list                                            # List loaded modules

Multiple modules are loaded in the order given:

``` bash
generate-slurm-script \
    --nodes 1 --ntasks-per-node 8 \
    --modules gcc/13 cuda/12 cudnn/8 anaconda/3 \
    --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=8                            # number of tasks to invoke on each node
    ########################################################
    module purge                                           # Purge modules
    module load gcc/13 cuda/12 cudnn/8 anaconda/3          # modules
    module list                                            # List loaded modules

------------------------------------------------------------------------

## Custom commands

Everything after the `#SBATCH` pragmas and module loads is the body of
your script. Add arbitrary shell commands with `--custom-commands`:

``` bash
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

`--custom-command` (singular) adds a single command — useful when
quoting is tricky:

``` bash
generate-slurm-script \
    --nodes 1 --ntasks-per-node 4 \
    --custom-command 'python train.py --epochs 100' \
    --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=1                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=4                            # number of tasks to invoke on each node
    ########################################################
    python train.py --epochs 100

Set environment variables in the script body by including `export`
statements:

``` bash
generate-slurm-script \
    --nodes 1 --ntasks-per-node 1 \
    --cpus-per-task 8 \
    --modules gcc/13 anaconda/3 \
    --custom-commands \
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK' \
        'srun python multithreaded_job.py' \
    --no-header
```

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

------------------------------------------------------------------------

## Inline scripts

`--inline-scripts` appends the full content of existing shell scripts
into the generated SLURM script. This is handy when you already have
setup or run scripts you want to reuse:

``` bash
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

------------------------------------------------------------------------

## Saving and reusing settings

### Save the script to a file

``` bash
generate-slurm-script \
    --job-name baseline \
    --nodes 4 --ntasks-per-node 16 \
    --time 12:00:00 \
    --account proj_hpc \
    --output-path baseline.sh
cat baseline.sh
```

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

### Export settings as JSON

`--export-json` saves all current settings to a JSON file so you can
reload and tweak them later — without repeating every flag:

``` bash
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

### Build new scripts from a JSON base

Override any setting by passing flags alongside `--input`. Anything not
overridden is inherited from the JSON:

``` bash
# Same settings, but scale to 8 nodes and rename the job
generate-slurm-script \
    --input baseline.json \
    --nodes 8 \
    --job-name big_run \
    --no-header
```

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

This is especially useful for parameter studies — keep a base JSON and
vary one or two things per run:

``` bash
# Short test run from the same base
generate-slurm-script \
    --input baseline.json \
    --nodes 1 \
    --time 00:30:00 \
    --job-name baseline_test \
    --no-header
```

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

### Read pragmas from an existing script

`--read-script` parses an existing `#SBATCH` script and imports its
pragmas and commands. Use it to add new options to a script you received
from a colleague or downloaded from a cluster guide:

``` bash
# baseline.sh is the script we saved above; override job-name and add modules
generate-slurm-script \
    --read-script baseline.sh \
    --job-name updated_run \
    --modules python/3.11 \
    --no-header
```

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

------------------------------------------------------------------------

## Submitting directly

Add `--submit` to write the script (requires `--output-path`) and immediately
call `sbatch` on it:

``` bash
generate-slurm-script \
    --job-name my_job \
    --nodes 2 --ntasks-per-node 16 \
    --time 04:00:00 \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands 'srun ./myprog > output.txt' \
    --output-path my_job.sh \
    --submit
```

------------------------------------------------------------------------

## Common job templates

### Serial (single-core) job

A sequential Python script using one CPU and minimal memory:

``` bash
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

### Multithreaded job (OpenMP / Python multiprocessing)

One task that uses multiple cores on a single shared node:

``` bash
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

### Pure MPI job

Multiple tasks spread across several full nodes:

``` bash
generate-slurm-script \
    --job-name mpi_job \
    --nodes 8 \
    --ntasks-per-node 64 \
    --time 12:00:00 \
    --modules gcc/13 openmpi/5.0 \
    --custom-commands 'srun ./mpi_program > output.txt' \
    --no-header
```

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

### Hybrid MPI + OpenMP job

Each MPI task spawns multiple OpenMP threads — common for modern HPC
codes:

``` bash
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

### Single-GPU job

One GPU on a shared GPU node, with enough CPUs and RAM to feed it:

``` bash
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

### Multi-GPU job (full node)

Four GPUs on a dedicated GPU node, one MPI task per GPU:

``` bash
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

### Job array

Submit many similar jobs in one `sbatch` call. Each array element gets a
unique `$SLURM_ARRAY_TASK_ID`:

``` bash
generate-slurm-script \
    --job-name sweep \
    --array 0-9 \
    --nodes 1 \
    --ntasks-per-node 8 \
    --time 04:00:00 \
    --output-path logs/sweep_%A_%a.out \
    --error logs/sweep_%A_%a.err \
    --modules gcc/13 anaconda/3 \
    --custom-commands \
        'python run.py --config configs/config_${SLURM_ARRAY_TASK_ID}.yaml' \
    --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Job Config                               #
    #SBATCH --job-name=sweep                               # name of job
    #                                                      #
    # Pragmas for Time And Priority                        #
    #SBATCH --time=04:00:00                                # time limit
    #                                                      #
    # Pragmas for Io And Directory                         #
    #SBATCH --output=logs/sweep_%A_%a.out                  # File to redirect output (%%x=jobname, %%j=jobid)
    #SBATCH --error=logs/sweep_%A_%a.err                   # File to redirect error (%%x=jobname, %%j=jobid)
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

``` bash
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
    --output-path sim_test.sh
cat sim_test.sh
```

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

``` bash
# 2. Scale up for the real run — inherit everything from the JSON,
#    override only what changes
generate-slurm-script \
    --input sim_base.json \
    --job-name sim_production \
    --nodes 16 \
    --time 12:00:00 \
    --partition main \
    --custom-commands 'srun ./myprog --full-input > production.out' \
    --output-path sim_production.sh
cat sim_production.sh
```

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

``` bash
# 3. A colleague wants the same setup with a different account and partition —
#    read the production script and override those two fields
generate-slurm-script \
    --read-script sim_production.sh \
    --account colleague_account \
    --partition gpu \
    --output-path colleague_job.sh
cat colleague_job.sh
```

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
