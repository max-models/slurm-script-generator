# Slurm script generator

## Install

```
pip install .
```

## Generate scripts

Generate a slurm script to `slurm_script.sh` with

```bash
❯ generate-slurm-script --nodes 1 --ntasks-per-node 16 --output slurm_script.sh
❯ cat slurm_script.sh
#!/bin/bash
##########################################
#SBATCH --nodes 1                        # number of nodes on which to run
#SBATCH --ntasks_per_node 16             # number of tasks to invoke on each node
##########################################
```

To export the settings to a json file you can use `--export-json`:

```bash
❯ generate-slurm-script --nodes 2 --export-json setup.json
#!/bin/bash
##########################################
#SBATCH --nodes 2                        # number of nodes on which to run
##########################################
```

This json file can used as a basis for creating new scripts

```bash
❯ generate-slurm-script --input setup.json --ntasks-per-node 16
#!/bin/bash
##########################################
#SBATCH --nodes 2                        # number of nodes on which to run
#SBATCH --ntasks_per_node 16             # number of tasks to invoke on each node
##########################################
```

### Add modules

Add modules with

```bash
❯ generate-slurm-script --input setup.json --ntasks-per-node 16 --modules gcc/13 openmpi/5.0
#!/bin/bash
##########################################
#SBATCH --nodes=2                        # number of nodes on which to run
#SBATCH --ntasks-per-node=16             # number of tasks to invoke on each node
##########################################
module purge                             # Purge modules
module load gcc/13 openmpi/5.0           # modules
module list                              # List loaded modules
```

### Add virtual environment

```bash
❯ generate-slurm-script --nodes 1 --ntasks-per-node 16 --venv ~/virtual_envs/env
#!/bin/bash
##########################################
#SBATCH --nodes=1                        # number of nodes on which to run
#SBATCH --ntasks-per-node=16             # number of tasks to invoke on each node
##########################################
source /Users/max/virtual_envs/env/bin/activate # virtual environment
```

### Other

All optional arguments can be shown with

```bash
❯ generate-slurm-script -h
usage: generate-slurm-script [-h] [-A NAME] [-b TIME] [--bell] [--bb SPEC] [--bbf FILE_NAME] [-c NCPUS] [--comment NAME] [--container PATH]
                             [--container-id ID] [--cpu-freq MIN[-MAX[:GOV]]] [--delay-boot MINS] [-d TYPE:JOBID[:TIME]] [--deadline TIME] [-D PATH]
                             [--get-user-env] [--gres LIST] [--gres-flags OPTS] [-H] [-I [SECS]] [-J NAME] [-k] [-K [SIGNAL]] [-L NAMES] [-M NAMES]
                             [-m TYPE] [--mail-type TYPE] [--mail-user USER] [--mcs-label MCS] [-n N] [--nice VALUE] [-N NODES] [--ntasks-per-node N]
                             [--oom-kill-step [0|1]] [-O] [--power FLAGS] [--priority VALUE] [--profile VALUE] [-p PARTITION] [-q QOS] [-Q]
                             [--reboot] [-s] [--signal [R:]NUM[@TIME]] [--spread-job] [--stderr STDERR] [--stdout STDOUT]
                             [--switches MAX_SWITCHES[@MAX_TIME]] [-S CORES] [--thread-spec THREADS] [-t MINUTES] [--time-min MINUTES]
                             [--tres-bind ...] [--tres-per-task LIST] [--use-min-nodes] [--wckey WCKEY] [--cluster-constraint LIST] [--contiguous]
                             [-C LIST] [-F FILENAME] [--mem MB] [--mincpus N] [--reservation NAME] [--tmp MB] [-w HOST [HOST ...]]
                             [-x HOST [HOST ...]] [--exclusive-user] [--exclusive-mcs] [--mem-per-cpu MB] [--resv-ports] [--sockets-per-node S]
                             [--cores-per-socket C] [--threads-per-core T] [-B S[:C[:T]]] [--ntasks-per-core N] [--ntasks-per-socket N] [--hint HINT]
                             [--mem-bind BIND] [--cpus-per-gpu N] [-G N] [--gpu-bind ...] [--gpu-freq ...] [--gpus-per-node N] [--gpus-per-socket N]
                             [--gpus-per-task N] [--mem-per-gpu --MEM_PER_GPU] [--disable-stdout-job-summary] [--nvmps] [--line-length LINE_LENGHT]
                             [--modules MODULES [MODULES ...]] [--vars ENVIRONMENT_VARS [ENVIRONMENT_VARS ...]] [--venv VENV] [--printenv]
                             [--print-self] [--likwid] [--input INPUT_PATH] [--output OUTPUT_PATH] [--export-json JSON_PATH] [--command COMMAND]

Slurm job submission options

options:
  -h, --help            show this help message and exit
  -A, --account NAME    charge job to specified account (default: None)
  -b, --begin TIME      defer job until HH:MM MM/DD/YY (default: None)
  --bell                ring the terminal bell when the job is allocated (default: None)
  --bb SPEC             burst buffer specifications (default: None)
  --bbf FILE_NAME       burst buffer specification file (default: None)
  -c, --cpus-per-task NCPUS
                        number of cpus required per task (default: None)
  --comment NAME        arbitrary comment (default: None)
  --container PATH      Path to OCI container bundle (default: None)
  --container-id ID     OCI container ID (default: None)
  --cpu-freq MIN[-MAX[:GOV]]
                        requested cpu frequency (and governor) (default: None)
  --delay-boot MINS     delay boot for desired node features (default: None)
  -d, --dependency TYPE:JOBID[:TIME]
                        defer job until condition on jobid is satisfied (default: None)
  --deadline TIME       remove the job if no ending possible before this deadline (default: None)
  -D, --chdir PATH      change working directory (default: None)
  --get-user-env        used by Moab. See srun man page (default: None)
  --gres LIST           required generic resources (default: None)
  --gres-flags OPTS     flags related to GRES management (default: None)
  -H, --hold            submit job in held state (default: None)
  -I, --immediate [SECS]
                        exit if resources not available in "secs" (default: None)
  -J, --job-name NAME   name of job (default: None)
  -k, --no-kill         do not kill job on node failure (default: None)
  -K, --kill-command [SIGNAL]
                        signal to send terminating job (default: None)
  -L, --licenses NAMES  required license, comma separated (default: None)
  -M, --clusters NAMES  Comma separated list of clusters to issue commands to (default: None)
  -m, --distribution TYPE
                        distribution method for processes to nodes (default: None)
  --mail-type TYPE      notify on state change (default: None)
  --mail-user USER      who to send email notification for job state changes (default: None)
  --mcs-label MCS       mcs label if mcs plugin mcs/group is used (default: None)
  -n, --ntasks N        number of processors required (default: None)
  --nice VALUE          decrease scheduling priority by value (default: None)
  -N, --nodes NODES     number of nodes on which to run (default: None)
  --ntasks-per-node N   number of tasks to invoke on each node (default: None)
  --oom-kill-step [0|1]
                        set the OOMKillStep behaviour (default: None)
  -O, --overcommit      overcommit resources (default: None)
  --power FLAGS         power management options (default: None)
  --priority VALUE      set the priority of the job (default: None)
  --profile VALUE       enable acct_gather_profile for detailed data (default: None)
  -p, --partition PARTITION
                        partition requested (default: None)
  -q, --qos QOS         quality of service (default: None)
  -Q, --quiet           quiet mode (suppress informational messages) (default: None)
  --reboot              reboot compute nodes before starting job (default: None)
  -s, --oversubscribe   oversubscribe resources with other jobs (default: None)
  --signal [R:]NUM[@TIME]
                        send signal when time limit within time seconds (default: None)
  --spread-job          spread job across as many nodes as possible (default: None)
  --stderr, -e STDERR   File to redirect stderr (%x=jobname, %j=jobid) (default: None)
  --stdout, -o STDOUT   File to redirect stdout (%x=jobname, %j=jobid) (default: None)
  --switches MAX_SWITCHES[@MAX_TIME]
                        optimum switches and max time to wait for optimum (default: None)
  -S, --core-spec CORES
                        count of reserved cores (default: None)
  --thread-spec THREADS
                        count of reserved threads (default: None)
  -t, --time MINUTES    time limit (default: None)
  --time-min MINUTES    minimum time limit (if distinct) (default: None)
  --tres-bind ...       task to tres binding options (default: None)
  --tres-per-task LIST  list of tres required per task (default: None)
  --use-min-nodes       if a range of node counts is given, prefer the smaller count (default: None)
  --wckey WCKEY         wckey to run job under (default: None)
  --cluster-constraint LIST
                        specify a list of cluster constraints (default: None)
  --contiguous          demand a contiguous range of nodes (default: None)
  -C, --constraint LIST
                        specify a list of constraints (default: None)
  -F, --nodefile FILENAME
                        request a specific list of hosts (default: None)
  --mem MB              minimum amount of real memory (default: None)
  --mincpus N           minimum number of logical processors per node (default: None)
  --reservation NAME    allocate resources from named reservation (default: None)
  --tmp MB              minimum amount of temporary disk (default: None)
  -w, --nodelist HOST [HOST ...]
                        request a specific list of hosts (default: None)
  -x, --exclude HOST [HOST ...]
                        exclude a specific list of hosts (default: None)
  --exclusive-user      allocate nodes in exclusive mode for cpu consumable resource (default: None)
  --exclusive-mcs       allocate nodes in exclusive mode when mcs plugin is enabled (default: None)
  --mem-per-cpu MB      maximum amount of real memory per allocated cpu (default: None)
  --resv-ports          reserve communication ports (default: None)
  --sockets-per-node S  number of sockets per node to allocate (default: None)
  --cores-per-socket C  number of cores per socket to allocate (default: None)
  --threads-per-core T  number of threads per core to allocate (default: None)
  -B, --extra-node-info S[:C[:T]]
                        combine request of sockets, cores and threads (default: None)
  --ntasks-per-core N   number of tasks to invoke on each core (default: None)
  --ntasks-per-socket N
                        number of tasks to invoke on each socket (default: None)
  --hint HINT           Bind tasks according to application hints (default: None)
  --mem-bind BIND       Bind memory to locality domains (default: None)
  --cpus-per-gpu N      number of CPUs required per allocated GPU (default: None)
  -G, --gpus N          count of GPUs required for the job (default: None)
  --gpu-bind ...        task to gpu binding options (default: None)
  --gpu-freq ...        frequency and voltage of GPUs (default: None)
  --gpus-per-node N     number of GPUs required per allocated node (default: None)
  --gpus-per-socket N   number of GPUs required per allocated socket (default: None)
  --gpus-per-task N     number of GPUs required per spawned task (default: None)
  --mem-per-gpu --MEM_PER_GPU
                        real memory required per allocated GPU (default: None)
  --disable-stdout-job-summary
                        disable job summary in stdout file for the job (default: None)
  --nvmps               launching NVIDIA MPS for job (default: None)
  --line-length LINE_LENGHT
                        line length before start of comment (default: 40)
  --modules MODULES [MODULES ...]
                        Modules to load (e.g., --modules mod1 mod2 mod3) (default: [])
  --vars ENVIRONMENT_VARS [ENVIRONMENT_VARS ...]
                        Environment variables to export (e.g., --vars VAR1=a VAR2=b) (default: [])
  --venv VENV           virtual environment to load with `source VENV/bin/activate` (default: None)
  --printenv            print all environment variables (default: False)
  --print-self          print the batch script in the batch script (default: False)
  --likwid              Set up likwid environment variables (default: False)
  --input INPUT_PATH    path to input json file (default: None)
  --output OUTPUT_PATH  json path to save slurm batch script to (default: None)
  --export-json JSON_PATH
                        path to export yaml for generating the slurm script to (default: None)
  --command COMMAND     Add a custom command at the end of the script (e.g. mpirun -n 8 ./bin > run.out) (default: None)
```