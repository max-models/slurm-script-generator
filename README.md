# slurm-script-generator


Check out the browser version [here](https://slurm-script-generator.github.io/).

Check out the
[documentation](https://max-models.github.io/slurm-script-generator) for
more details and examples!

## Installation

``` bash
pip install slurm-script-generator
```

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

To save the script to file `my_script.sh` use `--output-path`:

``` bash
generate-slurm-script --nodes 1 --ntasks-per-node 16 --output-path my_script.sh
```

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

You can also generate scripts in Python programmatically:

``` python
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
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #                                                      #
    # Pragmas for Cpu Topology And Binding                 #
    #SBATCH --ntasks-per-core=16                           # number of tasks to invoke on each core
    ########################################################
    # Run simulation
    srun ./bin > run.out

You can also generate a string representation of the script with
`generate_script`:

``` python
script = slurm_script.generate_script()
```

You can read more examples of the Python API in the [tutorial
notebooks](https://max-models.github.io/slurm-script-generator/tutorials.html).

## Exporting and reading scripts

To export the settings to a json file you can use `--export-json`:

``` bash
generate-slurm-script --nodes 2 --export-json setup.json --no-header
```

    #!/bin/bash
    ########################################################
    # Pragmas for Core Node And Task Allocation            #
    #SBATCH --nodes=2                                      # number of nodes on which to run
    ########################################################

This json file can used as a basis for creating new scripts

``` bash
generate-slurm-script --input setup.json --ntasks-per-node 16 --no-header
```

    #!/bin/bash
    ########################################################
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
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    #SBATCH --job-name=OLD_JOB_NAME                        # name of job
    ########################################################
    srun ./myprog > prog.out

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
    #SBATCH --nodes=2                                      # number of nodes on which to run
    #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
    ########################################################
    srun ./myprog > prog.out

### Other

All optional arguments can be shown with

``` bash
generate-slurm-script -h
```

    usage: generate-slurm-script [-h] [-J NAME] [-A NAME] [-p PARTITION] [-q QOS]
                                 [-M NAMES] [--reservation NAME] [--wckey WCKEY]
                                 [--mcs-label MCS] [--comment NAME] [-t MINUTES]
                                 [--time-min MINUTES] [-b TIME] [--deadline TIME]
                                 [--priority VALUE] [--nice VALUE] [-D PATH]
                                 [--output OUTPUT] [--error ERROR]
                                 [--disable-output-job-summary] [--get-user-env]
                                 [-Q] [--mail-user USER] [--mail-type TYPE]
                                 [--bell] [-d TYPE:JOBID[:TIME]] [--array INDEXES]
                                 [-N NODES] [-n N] [--ntasks-per-node N]
                                 [-c NCPUS] [--mincpus N] [-m TYPE] [--spread-job]
                                 [--use-min-nodes] [--sockets-per-node S]
                                 [--cores-per-socket C] [--threads-per-core T]
                                 [--ntasks-per-core N] [--ntasks-per-socket N]
                                 [-B S[:C[:T]]] [--hint HINT] [--mem MB]
                                 [--mem-per-cpu MB] [--mem-bind BIND]
                                 [--oom-kill-step [0|1]] [-G N]
                                 [--gpus-per-node N] [--gpus-per-task N]
                                 [--gpus-per-socket N] [--cpus-per-gpu N]
                                 [--mem-per-gpu MEM_PER_GPU] [--gpu-bind ...]
                                 [--gpu-freq ...] [--nvmps] [--gres LIST]
                                 [--gres-flags OPTS] [--tres-bind ...]
                                 [--tres-per-task LIST] [-L NAMES] [-C LIST]
                                 [--cluster-constraint LIST] [--contiguous]
                                 [-w HOST [HOST ...]] [-F FILENAME]
                                 [-x HOST [HOST ...]] [--exclusive-user]
                                 [--exclusive-mcs] [-s] [-O] [-H] [-I [SECS]]
                                 [--reboot] [--delay-boot MINS] [-k] [-K [SIGNAL]]
                                 [--signal [R:]NUM[@TIME]] [-S CORES]
                                 [--thread-spec THREADS]
                                 [--cpu-freq MIN[-MAX[:GOV]]] [--tmp MB]
                                 [--resv-ports]
                                 [--switches MAX_SWITCHES[@MAX_TIME]]
                                 [--power FLAGS] [--profile VALUE] [--bb SPEC]
                                 [--bbf FILE_NAME] [--container PATH]
                                 [--container-id ID] [--line-length LINE_LENGTH]
                                 [--modules MODULES [MODULES ...]]
                                 [--input INPUT_PATH] [--output-path OUTPUT_PATH]
                                 [--export-json JSON_PATH]
                                 [--custom-command COMMAND]
                                 [--custom-commands COMMAND [COMMAND ...]]
                                 [--read-script SCRIPT_PATH]
                                 [--inline-script COMMAND]
                                 [--inline-scripts COMMAND [COMMAND ...]]
                                 [--no-header] [--submit]

    Slurm job submission options

    options:
      -h, --help            show this help message and exit
      -J, --job-name NAME   name of job (default: None)
      -A, --account NAME    charge job to specified account (default: None)
      -p, --partition PARTITION
                            partition requested (default: None)
      -q, --qos QOS         quality of service (default: None)
      -M, --clusters NAMES  Comma separated list of clusters to issue commands to
                            (default: None)
      --reservation NAME    allocate resources from named reservation (default:
                            None)
      --wckey WCKEY         wckey to run job under (default: None)
      --mcs-label MCS       mcs label if mcs plugin mcs/group is used (default:
                            None)
      --comment NAME        arbitrary comment (default: None)
      -t, --time MINUTES    time limit (default: None)
      --time-min MINUTES    minimum time limit (if distinct) (default: None)
      -b, --begin TIME      defer job until HH:MM MM/DD/YY (default: None)
      --deadline TIME       remove the job if no ending possible before this
                            deadline (default: None)
      --priority VALUE      set the priority of the job (default: None)
      --nice VALUE          decrease scheduling priority by value (default: None)
      -D, --chdir PATH      change working directory (default: None)
      --output, -o OUTPUT   File to redirect output (%x=jobname, %j=jobid)
                            (default: None)
      --error, -e ERROR     File to redirect error (%x=jobname, %j=jobid)
                            (default: None)
      --disable-output-job-summary
                            disable job summary in output file for the job
                            (default: None)
      --get-user-env        used by Moab. See srun man page (default: None)
      -Q, --quiet           quiet mode (suppress informational messages) (default:
                            None)
      --mail-user USER      who to send email notification for job state changes
                            (default: None)
      --mail-type TYPE      notify on state change (default: None)
      --bell                ring the terminal bell when the job is allocated
                            (default: None)
      -d, --dependency TYPE:JOBID[:TIME]
                            defer job until condition on jobid is satisfied
                            (default: None)
      --array INDEXES       submit a job array (default: None)
      -N, --nodes NODES     number of nodes on which to run (default: None)
      -n, --ntasks N        number of processors required (default: None)
      --ntasks-per-node N   number of tasks to invoke on each node (default: None)
      -c, --cpus-per-task NCPUS
                            number of cpus required per task (default: None)
      --mincpus N           minimum number of logical processors per node
                            (default: None)
      -m, --distribution TYPE
                            distribution method for processes to nodes (default:
                            None)
      --spread-job          spread job across as many nodes as possible (default:
                            None)
      --use-min-nodes       if a range of node counts is given, prefer the smaller
                            count (default: None)
      --sockets-per-node S  number of sockets per node to allocate (default: None)
      --cores-per-socket C  number of cores per socket to allocate (default: None)
      --threads-per-core T  number of threads per core to allocate (default: None)
      --ntasks-per-core N   number of tasks to invoke on each core (default: None)
      --ntasks-per-socket N
                            number of tasks to invoke on each socket (default:
                            None)
      -B, --extra-node-info S[:C[:T]]
                            combine request of sockets, cores and threads
                            (default: None)
      --hint HINT           Bind tasks according to application hints (default:
                            None)
      --mem MB              minimum amount of real memory (default: None)
      --mem-per-cpu MB      maximum amount of real memory per allocated cpu
                            (default: None)
      --mem-bind BIND       Bind memory to locality domains (default: None)
      --oom-kill-step [0|1]
                            set the OOMKillStep behaviour (default: None)
      -G, --gpus N          count of GPUs required for the job (default: None)
      --gpus-per-node N     number of GPUs required per allocated node (default:
                            None)
      --gpus-per-task N     number of GPUs required per spawned task (default:
                            None)
      --gpus-per-socket N   number of GPUs required per allocated socket (default:
                            None)
      --cpus-per-gpu N      number of CPUs required per allocated GPU (default:
                            None)
      --mem-per-gpu MEM_PER_GPU
                            real memory required per allocated GPU (default: None)
      --gpu-bind ...        task to gpu binding options (default: None)
      --gpu-freq ...        frequency and voltage of GPUs (default: None)
      --nvmps               launching NVIDIA MPS for job (default: None)
      --gres LIST           required generic resources (default: None)
      --gres-flags OPTS     flags related to GRES management (default: None)
      --tres-bind ...       task to tres binding options (default: None)
      --tres-per-task LIST  list of tres required per task (default: None)
      -L, --licenses NAMES  required license, comma separated (default: None)
      -C, --constraint LIST
                            specify a list of constraints (default: None)
      --cluster-constraint LIST
                            specify a list of cluster constraints (default: None)
      --contiguous          demand a contiguous range of nodes (default: None)
      -w, --nodelist HOST [HOST ...]
                            request a specific list of hosts (default: None)
      -F, --nodefile FILENAME
                            request a specific list of hosts (default: None)
      -x, --exclude HOST [HOST ...]
                            exclude a specific list of hosts (default: None)
      --exclusive-user      allocate nodes in exclusive mode for cpu consumable
                            resource (default: None)
      --exclusive-mcs       allocate nodes in exclusive mode when mcs plugin is
                            enabled (default: None)
      -s, --oversubscribe   oversubscribe resources with other jobs (default:
                            None)
      -O, --overcommit      overcommit resources (default: None)
      -H, --hold            submit job in held state (default: None)
      -I, --immediate [SECS]
                            exit if resources not available in "secs" (default:
                            None)
      --reboot              reboot compute nodes before starting job (default:
                            None)
      --delay-boot MINS     delay boot for desired node features (default: None)
      -k, --no-kill         do not kill job on node failure (default: None)
      -K, --kill-command [SIGNAL]
                            signal to send terminating job (default: None)
      --signal [R:]NUM[@TIME]
                            send signal when time limit within time seconds
                            (default: None)
      -S, --core-spec CORES
                            count of reserved cores (default: None)
      --thread-spec THREADS
                            count of reserved threads (default: None)
      --cpu-freq MIN[-MAX[:GOV]]
                            requested cpu frequency (and governor) (default: None)
      --tmp MB              minimum amount of temporary disk (default: None)
      --resv-ports          reserve communication ports (default: None)
      --switches MAX_SWITCHES[@MAX_TIME]
                            optimum switches and max time to wait for optimum
                            (default: None)
      --power FLAGS         power management options (default: None)
      --profile VALUE       enable acct_gather_profile for detailed data (default:
                            None)
      --bb SPEC             burst buffer specifications (default: None)
      --bbf FILE_NAME       burst buffer specification file (default: None)
      --container PATH      Path to OCI container bundle (default: None)
      --container-id ID     OCI container ID (default: None)
      --line-length LINE_LENGTH
                            line length before start of comment (default: None)
      --modules MODULES [MODULES ...]
                            Modules to load (e.g., --modules mod1 mod2 mod3)
                            (default: [])
      --input INPUT_PATH    path to input json file (default: None)
      --output-path OUTPUT_PATH
                            path to save the generated SLURM script (default:
                            None)
      --export-json JSON_PATH
                            path to export yaml for generating the slurm script to
                            (default: None)
      --custom-command COMMAND
                            Add a custom command at the end of the script (e.g.
                            --custom-command 'mpirun -n 8 ./bin > run.out')
                            (default: None)
      --custom-commands COMMAND [COMMAND ...]
                            Add custom commands at the end of the script (e.g.
                            --custom-commands '# Run simulation' 'mpirun -n 8
                            ./bin > run.out') (default: [])
      --read-script SCRIPT_PATH
                            Path to a slurm script file to read and include
                            pragmas and commands from (e.g. --read-script
                            sbatch_script.sh) (default: None)
      --inline-script COMMAND
                            Inline script to add at the end of the script (e.g.
                            --inline-script script.sh) (default: None)
      --inline-scripts COMMAND [COMMAND ...]
                            Add inline scripts at the end of the script (e.g.
                            --inline-scripts script1.sh script2.sh) (default: [])
      --no-header           Do not include the header comment in the generated
                            script (default: False)
      --submit              Submit the generated script to the scheduler (requires
                            --output-path to be specified) (default: False)
