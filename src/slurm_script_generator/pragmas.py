from abc import abstractmethod
from argparse import ArgumentParser
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Type

from slurm_script_generator.utils import add_line


class Pragma:
    """Base class representing a SLURM #SBATCH pragma."""

    flags: List[str] = []
    dest: str = ""
    metavar: str | None = None
    help: str = ""
    example: str | None = None
    type: Callable[[str], Any] = str
    nargs: str | None = None
    const: int | None = None
    choices: List[str] | None = None
    action: str | None = None
    default: str | None = None

    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return add_line(
            f"#SBATCH {self.dest.replace('_', '-')}={self.value}", comment=self.help
        )


class Account(Pragma):
    flags = ["-A", "--account"]
    dest = "--account"
    metavar = "NAME"
    help = "charge job to specified account"
    example = "myacct"
    type = str


class Begin(Pragma):
    flags = ["-b", "--begin"]
    dest = "--begin"
    metavar = "TIME"
    help = "defer job until HH:MM MM/DD/YY"
    type = str


class Bell(Pragma):
    flags = ["--bell"]
    dest = "--bell"
    help = "ring the terminal bell when the job is allocated"
    action = "store_true"
    type = str


class Burst_buffer(Pragma):

    flags = ["--bb"]
    dest = "--burst_buffer"
    metavar = "SPEC"
    help = "burst buffer specifications"
    type = str


class Bb_file(Pragma):

    flags = ["--bbf"]
    dest = "--bb_file"
    metavar = "FILE_NAME"
    help = "burst buffer specification file"
    type = str


class Cpus_per_task(Pragma):

    flags = ["-c", "--cpus-per-task"]
    dest = "--cpus_per_task"
    metavar = "NCPUS"
    help = "number of cpus required per task"
    example = "16"
    type = str


class Comment(Pragma):

    flags = ["--comment"]
    dest = "--comment"
    metavar = "NAME"
    help = "arbitrary comment"
    type = str


class Container(Pragma):

    flags = ["--container"]
    dest = "--container"
    metavar = "PATH"
    help = "Path to OCI container bundle"
    type = str


class Container_id(Pragma):

    flags = ["--container-id"]
    dest = "--container_id"
    metavar = "ID"
    help = "OCI container ID"
    type = str


class Cpu_freq(Pragma):

    flags = ["--cpu-freq"]
    dest = "--cpu_freq"
    metavar = "MIN[-MAX[:GOV]]"
    help = "requested cpu frequency (and governor)"
    type = str


class Delay_boot(Pragma):

    flags = ["--delay-boot"]
    dest = "--delay_boot"
    metavar = "MINS"
    help = "delay boot for desired node features"
    type = str


class Dependency(Pragma):

    flags = ["-d", "--dependency"]
    dest = "--dependency"
    metavar = "TYPE:JOBID[:TIME]"
    help = "defer job until condition on jobid is satisfied"
    type = str


class Deadline(Pragma):

    flags = ["--deadline"]
    dest = "--deadline"
    metavar = "TIME"
    help = "remove the job if no ending possible before this deadline"
    type = str


class Chdir(Pragma):

    flags = ["-D", "--chdir"]
    dest = "--chdir"
    metavar = "PATH"
    help = "change working directory"
    type = str


class Get_user_env(Pragma):

    flags = ["--get-user-env"]
    dest = "--get_user_env"
    help = "used by Moab. See srun man page"
    action = "store_true"
    type = str


class Gres(Pragma):

    flags = ["--gres"]
    dest = "--gres"
    metavar = "LIST"
    help = "required generic resources"
    type = str


class Gres_flags(Pragma):

    flags = ["--gres-flags"]
    dest = "--gres_flags"
    metavar = "OPTS"
    help = "flags related to GRES management"
    type = str


class Hold(Pragma):

    flags = ["-H", "--hold"]
    dest = "--hold"
    help = "submit job in held state"
    action = "store_true"
    type = str


class Immediate(Pragma):

    flags = ["-I", "--immediate"]
    dest = "--immediate"
    metavar = "SECS"
    help = 'exit if resources not available in "secs"'
    nargs = "?"
    const = "0"
    type = str


class Job_name(Pragma):

    flags = ["-J", "--job-name"]
    dest = "--job_name"
    metavar = "NAME"
    help = "name of job"
    example = "my_job"
    type = str


class No_kill(Pragma):

    flags = ["-k", "--no-kill"]
    dest = "--no_kill"
    help = "do not kill job on node failure"
    action = "store_true"
    type = str


class Kill_command(Pragma):

    flags = ["-K", "--kill-command"]
    dest = "--kill_command"
    metavar = "SIGNAL"
    help = "signal to send terminating job"
    nargs = "?"
    const = "TERM"
    type = str


class Licenses(Pragma):

    flags = ["-L", "--licenses"]
    dest = "--licenses"
    metavar = "NAMES"
    help = "required license, comma separated"
    type = str


class Clusters(Pragma):

    flags = ["-M", "--clusters"]
    dest = "--clusters"
    metavar = "NAMES"
    help = "Comma separated list of clusters to issue commands to"
    type = str


class Distribution(Pragma):

    flags = ["-m", "--distribution"]
    dest = "--distribution"
    metavar = "TYPE"
    help = "distribution method for processes to nodes"
    choices = ['block', 'cyclic', 'arbitrary']
    type = str


class Mail_type(Pragma):

    flags = ["--mail-type"]
    dest = "--mail_type"
    metavar = "TYPE"
    help = "notify on state change"
    example = "ALL"
    choices = ['NONE', 'BEGIN', 'END', 'FAIL', 'REQUEUE', 'ALL']
    type = str

class Mail_user(Pragma):

    flags = ["--mail-user"]
    dest = "--mail_user"
    metavar = "USER"
    help = "who to send email notification for job state changes"
    example = "example@email.com"
    type = str


class Mcs_label(Pragma):

    flags = ["--mcs-label"]
    dest = "--mcs_label"
    metavar = "MCS"
    help = "mcs label if mcs plugin mcs/group is used"
    type = str


class Ntasks(Pragma):

    flags = ["-n", "--ntasks"]
    dest = "--ntasks"
    metavar = "N"
    help = "number of processors required"
    example = "16"
    type = str


class Nice(Pragma):

    flags = ["--nice"]
    dest = "--nice"
    metavar = "VALUE"
    help = "decrease scheduling priority by value"
    example = "1"
    type = str


class Nodes(Pragma):

    flags = ["-N", "--nodes"]
    dest = "--nodes"
    metavar = "NODES"
    help = "number of nodes on which to run"
    example = "2"
    type = str


class Ntasks_per_node(Pragma):

    flags = ["--ntasks-per-node"]
    dest = "--ntasks_per_node"
    metavar = "N"
    help = "number of tasks to invoke on each node"
    example = "16"
    type = str


class Oom_kill_step(Pragma):

    flags = ["--oom-kill-step"]
    dest = "--oom_kill_step"
    metavar = "0|1"
    help = "set the OOMKillStep behaviour"
    nargs = "?"
    const = "1"
    type = str


class Overcommit(Pragma):

    flags = ["-O", "--overcommit"]
    dest = "--overcommit"
    help = "overcommit resources"
    action = "store_true"
    type = str


class Power(Pragma):

    flags = ["--power"]
    dest = "--power"
    metavar = "FLAGS"
    help = "power management options"
    type = str


class Priority(Pragma):

    flags = ["--priority"]
    dest = "--priority"
    metavar = "VALUE"
    help = "set the priority of the job"
    type = str


class Profile(Pragma):

    flags = ["--profile"]
    dest = "--profile"
    metavar = "VALUE"
    help = "enable acct_gather_profile for detailed data"
    type = str


class Partition(Pragma):

    flags = ["-p", "--partition"]
    dest = "--partition"
    metavar = "PARTITION"
    help = "partition requested"
    type = str


class Qos(Pragma):

    flags = ["-q", "--qos"]
    dest = "--qos"
    metavar = "QOS"
    help = "quality of service"
    type = str


class Quiet(Pragma):

    flags = ["-Q", "--quiet"]
    dest = "--quiet"
    help = "quiet mode (suppress informational messages)"
    action = "store_true"
    type = str


class Reboot(Pragma):

    flags = ["--reboot"]
    dest = "--reboot"
    help = "reboot compute nodes before starting job"
    action = "store_true"
    type = str


class Oversubscribe(Pragma):

    flags = ["-s", "--oversubscribe"]
    dest = "--oversubscribe"
    help = "oversubscribe resources with other jobs"
    action = "store_true"
    type = str


class Signal(Pragma):

    flags = ["--signal"]
    dest = "--signal"
    metavar = "[R:]NUM[@TIME]"
    help = "send signal when time limit within time seconds"
    type = str


class Spread_job(Pragma):

    flags = ["--spread-job"]
    dest = "--spread_job"
    help = "spread job across as many nodes as possible"
    action = "store_true"
    type = str


class E(Pragma):

    flags = ["--stderr", "-e"]
    dest = "-e"
    metavar = "STDERR"
    help = "File to redirect stderr (%%x=jobname, %%j=jobid)"
    example = "--stdout ./%x.%j.out"
    type = str


class O(Pragma):

    flags = ["--stdout", "-o"]
    dest = "-o"
    metavar = "STDOUT"
    help = "File to redirect stdout (%%x=jobname, %%j=jobid)"
    example = "--stdout ./%x.%j.out"
    type = str


class Switches(Pragma):

    flags = ["--switches"]
    dest = "--switches"
    metavar = "MAX_SWITCHES[@MAX_TIME]"
    help = "optimum switches and max time to wait for optimum"
    type = str


class Core_spec(Pragma):

    flags = ["-S", "--core-spec"]
    dest = "--core_spec"
    metavar = "CORES"
    help = "count of reserved cores"
    type = str


class Thread_spec(Pragma):

    flags = ["--thread-spec"]
    dest = "--thread_spec"
    metavar = "THREADS"
    help = "count of reserved threads"
    type = str


class Time(Pragma):

    flags = ["-t", "--time"]
    dest = "--time"
    metavar = "MINUTES"
    help = "time limit"
    example = "00:45:00"
    type = str


class Time_min(Pragma):

    flags = ["--time-min"]
    dest = "--time_min"
    metavar = "MINUTES"
    help = "minimum time limit (if distinct)"
    type = str


class Tres_bind(Pragma):

    flags = ["--tres-bind"]
    dest = "--tres_bind"
    metavar = "..."
    help = "task to tres binding options"
    type = str


class Tres_per_task(Pragma):

    flags = ["--tres-per-task"]
    dest = "--tres_per_task"
    metavar = "LIST"
    help = "list of tres required per task"
    type = str


class Use_min_nodes(Pragma):

    flags = ["--use-min-nodes"]
    dest = "--use_min_nodes"
    help = "if a range of node counts is given, prefer the smaller count"
    action = "store_true"
    type = str


class Wckey(Pragma):

    flags = ["--wckey"]
    dest = "--wckey"
    metavar = "WCKEY"
    help = "wckey to run job under"
    type = str


class Cluster_constraint(Pragma):

    flags = ["--cluster-constraint"]
    dest = "--cluster_constraint"
    metavar = "LIST"
    help = "specify a list of cluster constraints"
    type = str


class Contiguous(Pragma):

    flags = ["--contiguous"]
    dest = "--contiguous"
    help = "demand a contiguous range of nodes"
    action = "store_true"
    type = str


class Constraint(Pragma):

    flags = ["-C", "--constraint"]
    dest = "--constraint"
    metavar = "LIST"
    help = "specify a list of constraints"
    type = str


class Nodefile(Pragma):

    flags = ["-F", "--nodefile"]
    dest = "--nodefile"
    metavar = "FILENAME"
    help = "request a specific list of hosts"
    type = str


class Mem(Pragma):

    flags = ["--mem"]
    dest = "--mem"
    metavar = "MB"
    help = "minimum amount of real memory"
    example = "25GB"
    type = str


class Mincpus(Pragma):

    flags = ["--mincpus"]
    dest = "--mincpus"
    metavar = "N"
    help = "minimum number of logical processors per node"
    type = str


class Reservation(Pragma):

    flags = ["--reservation"]
    dest = "--reservation"
    metavar = "NAME"
    help = "allocate resources from named reservation"
    type = str


class Tmp(Pragma):

    flags = ["--tmp"]
    dest = "--tmp"
    metavar = "MB"
    help = "minimum amount of temporary disk"
    type = str


class Nodelist(Pragma):

    flags = ["-w", "--nodelist"]
    dest = "--nodelist"
    metavar = "HOST"
    help = "request a specific list of hosts"
    nargs = "+"
    type = str


class Exclude(Pragma):

    flags = ["-x", "--exclude"]
    dest = "--exclude"
    metavar = "HOST"
    help = "exclude a specific list of hosts"
    nargs = "+"
    type = str


class Exclusive_user(Pragma):

    flags = ["--exclusive-user"]
    dest = "--exclusive_user"
    help = "allocate nodes in exclusive mode for cpu consumable resource"
    action = "store_true"
    type = str


class Exclusive_mcs(Pragma):

    flags = ["--exclusive-mcs"]
    dest = "--exclusive_mcs"
    help = "allocate nodes in exclusive mode when mcs plugin is enabled"
    action = "store_true"
    type = str


class Mem_per_cpu(Pragma):

    flags = ["--mem-per-cpu"]
    dest = "--mem_per_cpu"
    metavar = "MB"
    help = "maximum amount of real memory per allocated cpu"
    type = str


class Resv_ports(Pragma):

    flags = ["--resv-ports"]
    dest = "--resv_ports"
    help = "reserve communication ports"
    action = "store_true"
    type = str


class Sockets_per_node(Pragma):

    flags = ["--sockets-per-node"]
    dest = "--sockets_per_node"
    metavar = "S"
    help = "number of sockets per node to allocate"
    type = str


class Cores_per_socket(Pragma):

    flags = ["--cores-per-socket"]
    dest = "--cores_per_socket"
    metavar = "C"
    help = "number of cores per socket to allocate"
    example = "8"
    type = str


class Threads_per_core(Pragma):

    flags = ["--threads-per-core"]
    dest = "--threads_per_core"
    metavar = "T"
    help = "number of threads per core to allocate"
    example = "4"
    type = str


class Extra_node_info(Pragma):

    flags = ["-B", "--extra-node-info"]
    dest = "--extra_node_info"
    metavar = "S[:C[:T]]"
    help = "combine request of sockets, cores and threads"
    type = str


class Ntasks_per_core(Pragma):

    flags = ["--ntasks-per-core"]
    dest = "--ntasks_per_core"
    metavar = "N"
    help = "number of tasks to invoke on each core"
    example = "16"
    type = str


class Ntasks_per_socket(Pragma):

    flags = ["--ntasks-per-socket"]
    dest = "--ntasks_per_socket"
    metavar = "N"
    help = "number of tasks to invoke on each socket"
    example = "8"
    type = str


class Hint(Pragma):

    flags = ["--hint"]
    dest = "--hint"
    metavar = "HINT"
    help = "Bind tasks according to application hints"
    type = str


class Mem_bind(Pragma):

    flags = ["--mem-bind"]
    dest = "--mem_bind"
    metavar = "BIND"
    help = "Bind memory to locality domains"
    type = str


class Cpus_per_gpu(Pragma):

    flags = ["--cpus-per-gpu"]
    dest = "--cpus_per_gpu"
    metavar = "N"
    help = "number of CPUs required per allocated GPU"
    example = "4"
    type = str


class Gpus(Pragma):

    flags = ["-G", "--gpus"]
    dest = "--gpus"
    metavar = "N"
    help = "count of GPUs required for the job"
    example = "32"
    type = str


class Gpu_bind(Pragma):

    flags = ["--gpu-bind"]
    dest = "--gpu_bind"
    metavar = "..."
    help = "task to gpu binding options"
    type = str


class Gpu_freq(Pragma):

    flags = ["--gpu-freq"]
    dest = "--gpu_freq"
    metavar = "..."
    help = "frequency and voltage of GPUs"
    type = str


class Gpus_per_node(Pragma):

    flags = ["--gpus-per-node"]
    dest = "--gpus_per_node"
    metavar = "N"
    help = "number of GPUs required per allocated node"
    type = str


class Gpus_per_socket(Pragma):

    flags = ["--gpus-per-socket"]
    dest = "--gpus_per_socket"
    metavar = "N"
    help = "number of GPUs required per allocated socket"
    type = str


class Gpus_per_task(Pragma):

    flags = ["--gpus-per-task"]
    dest = "--gpus_per_task"
    metavar = "N"
    help = "number of GPUs required per spawned task"
    type = str


class Mem_per_gpu(Pragma):

    flags = ["--mem-per-gpu"]
    dest = "--mem_per_gpu"
    help = "real memory required per allocated GPU"
    example = "8GB"
    type = str


class Disable_stdout_job_summary(Pragma):

    flags = ["--disable-stdout-job-summary"]
    dest = "--disable_stdout_job_summary"
    help = "disable job summary in stdout file for the job"
    action = "store_true"
    type = str


class Nvmps(Pragma):

    flags = ["--nvmps"]
    dest = "--nvmps"
    help = "launching NVIDIA MPS for job"
    action = "store_true"
    type = str


pragma_dict = {}

for _, pragma_cls in list(globals().items()):
    if (
        isinstance(pragma_cls, type)
        and issubclass(pragma_cls, Pragma)
        and pragma_cls is not Pragma
    ):
        pragma_dict[pragma_cls.dest] = pragma_cls


if __name__ == "__main__":
    acc = Account("max")
    print(acc)
