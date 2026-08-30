# slurm-template CLI

`slurm-template` writes a ready-to-edit SLURM batch script for a common job
shape, instead of building one pragma-by-pragma with `generate-slurm-script`.
Pick a template, override what's specific to your job, and fill in the
placeholder command.

```bash
slurm-template --list                 # see what's available
slurm-template TEMPLATE -o job.sh [overrides...]
```

---

## Available templates

| Template | Description |
|----------|-------------|
| `cpu`    | Single-node, single-task CPU job. |
| `openmp` | Single-node, multi-threaded (OpenMP) job. |
| `mpi`    | Multi-node MPI job, one rank per node. |
| `hybrid` | Hybrid MPI + OpenMP job (one rank per node, multiple threads per rank). |
| `gpu`    | Single-node job with one GPU. |
| `array`  | Job array (10 tasks by default); use `$SLURM_ARRAY_TASK_ID` per task. |

```bash
slurm-template --list
```

```
Available templates:

  array   Job array (10 tasks); use $SLURM_ARRAY_TASK_ID to pick work per task.
  cpu     Single-node, single-task CPU job.
  gpu     Single-node job with one GPU.
  hybrid  Hybrid MPI + OpenMP job (one rank per node, multiple threads per rank).
  mpi     Multi-node MPI job, one rank per node.
  openmp  Single-node, multi-threaded (OpenMP) job.
```

---

## Basic usage

Print a script to stdout:

```bash
slurm-template gpu
```

```
#!/bin/bash
########################################################
#            This script was generated using           #
#             slurm-script-generator vX.Y.Z            #
# https://github.com/max-models/slurm-script-generator #
#      `pip install slurm-script-generator==X.Y.Z`     #
########################################################

########################################################
# Pragmas for Job Config                               #
#SBATCH --job-name=gpu_job                             # name of job
#                                                      #
# Pragmas for Time And Priority                        #
#SBATCH --time=01:00:00                                # time limit
#                                                      #
# Pragmas for Core Node And Task Allocation            #
#SBATCH --nodes=1                                      # number of nodes on which to run
#SBATCH --ntasks=1                                     # number of processors required
#SBATCH --cpus-per-task=4                              # number of cpus required per task
#                                                      #
# Pragmas for Gpus                                     #
#SBATCH --gpus=1                                       # count of GPUs required for the job
########################################################
./my_gpu_program
```

Save it with `-o`/`--output`:

```bash
slurm-template gpu -o job.sh
```

---

## Overriding template defaults

Common resource flags override the template's defaults; anything not
overridden keeps its template value:

```bash
slurm-template gpu -o job.sh --job-name train_resnet --gpus 2 --time 04:00:00 --mem 64G
slurm-template mpi -o job.sh --nodes 8 --account myaccount --partition batch
slurm-template array -o job.sh --array 1-100
```

| Flag | Short | Description |
|------|-------|-------------|
| `--job-name NAME` | `-J` | Job name |
| `--account ACCOUNT` | `-A` | Account to charge |
| `--partition PARTITION` | `-p` | Partition |
| `--time TIME` | `-t` | Wall-clock time limit, e.g. `04:00:00` |
| `--nodes N` | `-N` | Number of nodes |
| `--ntasks N` | `-n` | Number of tasks |
| `--ntasks-per-node N` | | Tasks per node |
| `--cpus-per-task N` | `-c` | CPUs per task |
| `--mem MEM` | | Memory, e.g. `16G` |
| `--gpus N` | `-g` | Number of GPUs |
| `--array RANGE` | `-a` | Array range, e.g. `1-100` |

## Replacing the placeholder command

Every template ships a placeholder command (`./my_program`, `srun
./my_mpi_program`, ...) — replace it with `--command`/`-C`. Pass it multiple
times to build up a multi-line body:

```bash
slurm-template cpu -o job.sh --command "python train.py --config cfg.yaml"

slurm-template mpi -o job.sh \
    --command "module load openmpi" \
    --command "srun ./my_mpi_program --input data.h5"
```

## Loading modules

`--modules` replaces the template's module list (empty by default):

```bash
slurm-template gpu -o job.sh --modules cuda/12.2 python/3.11
```

---

## Submitting directly

`--submit` saves the script and submits it with `sbatch` in one step
(requires `-o`/`--output`):

```bash
slurm-template gpu -o job.sh --gpus 2 --submit
```

---

## Python API

Templates are also available from Python via
`slurm_script_generator.templates`:

```python
from slurm_script_generator.templates import build_script

script = build_script(
    "gpu",
    overrides={"job_name": "train_resnet", "gpus": 2, "time": "04:00:00"},
    commands=["python train.py"],
)
script.save("job.sh")
```

`build_script` returns a regular `SlurmScript`, so anything that works on a
script built via `generate-slurm-script` — `.save()`, `.submit_job()`,
`.to_string()`, `.to_json()` — works here too.
