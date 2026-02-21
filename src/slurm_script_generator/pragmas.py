from typing import Any, Callable, List, Type

from slurm_script_generator.utils import add_line


class Pragma:
    """Base class representing a SLURM #SBATCH pragma."""

    arg_varname: str
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
        # Convert value to the correct type if 'type' attribute is set
        # if hasattr(self, "type") and self.type is not None:
        #     try:
        #         self.value = self.type(value)
        #     except Exception:
        #         self.value = value
        # else:
        #     self.value = value
        self.value = value

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Pragma):
            return False
        return self.dest == value.dest and self.value == value.value

    def __str__(self) -> str:
        return add_line(
            f"#SBATCH {self.dest.replace('_', '-')}={self.value}", comment=self.help
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def to_dict(self) -> dict[str, Any]:
        return {self.arg_varname: self.value}


class Account(Pragma):
    """This class represents the SLURM #SBATCH --account pragma,
    which specifies the account to charge for a job.

    args:
        value (str): The name of the account to charge for the job.
    """

    arg_varname = "account"
    flags = ["-A", "--account"]
    dest = "--account"
    metavar = "NAME"
    help = "charge job to specified account"
    example = "myacct"
    type = str


class Begin(Pragma):
    arg_varname = "begin"
    flags = ["-b", "--begin"]
    dest = "--begin"
    metavar = "TIME"
    help = "defer job until HH:MM MM/DD/YY"
    type = str


class Array(Pragma):
    arg_varname = "array"
    flags = ["--array"]
    dest = "--array"
    metavar = "INDEXES"
    help = "submit a job array"
    type = str


class Bell(Pragma):
    arg_varname = "bell"
    flags = ["--bell"]
    dest = "--bell"
    help = "ring the terminal bell when the job is allocated"
    action = "store_true"
    type = str


class Burst_buffer(Pragma):
    arg_varname = "burst_buffer"
    flags = ["--bb"]
    dest = "--burst_buffer"
    metavar = "SPEC"
    help = "burst buffer specifications"
    type = str


class Bb_file(Pragma):
    arg_varname = "bb_file"
    flags = ["--bbf"]
    dest = "--bb_file"
    metavar = "FILE_NAME"
    help = "burst buffer specification file"
    type = str


class Cpus_per_task(Pragma):
    arg_varname = "cpus_per_task"
    flags = ["-c", "--cpus-per-task"]
    dest = "--cpus_per_task"
    metavar = "NCPUS"
    help = "number of cpus required per task"
    example = "16"
    type = str


class Comment(Pragma):
    arg_varname = "comment"
    flags = ["--comment"]
    dest = "--comment"
    metavar = "NAME"
    help = "arbitrary comment"
    type = str


class Container(Pragma):
    arg_varname = "container"
    flags = ["--container"]
    dest = "--container"
    metavar = "PATH"
    help = "Path to OCI container bundle"
    type = str


class Container_id(Pragma):
    arg_varname = "container_id"
    flags = ["--container-id"]
    dest = "--container_id"
    metavar = "ID"
    help = "OCI container ID"
    type = str


class Cpu_freq(Pragma):
    arg_varname = "cpu_freq"
    flags = ["--cpu-freq"]
    dest = "--cpu_freq"
    metavar = "MIN[-MAX[:GOV]]"
    help = "requested cpu frequency (and governor)"
    type = str


class Delay_boot(Pragma):
    arg_varname = "delay_boot"
    flags = ["--delay-boot"]
    dest = "--delay_boot"
    metavar = "MINS"
    help = "delay boot for desired node features"
    type = str


class Dependency(Pragma):
    arg_varname = "dependency"
    flags = ["-d", "--dependency"]
    dest = "--dependency"
    metavar = "TYPE:JOBID[:TIME]"
    help = "defer job until condition on jobid is satisfied"
    type = str


class Deadline(Pragma):
    arg_varname = "deadline"
    flags = ["--deadline"]
    dest = "--deadline"
    metavar = "TIME"
    help = "remove the job if no ending possible before this deadline"
    type = str


class Chdir(Pragma):
    arg_varname = "chdir"
    flags = ["-D", "--chdir"]
    dest = "--chdir"
    metavar = "PATH"
    help = "change working directory"
    type = str


class Get_user_env(Pragma):
    arg_varname = "get_user_env"
    flags = ["--get-user-env"]
    dest = "--get_user_env"
    help = "used by Moab. See srun man page"
    action = "store_true"
    type = str


class Gres(Pragma):
    arg_varname = "gres"
    flags = ["--gres"]
    dest = "--gres"
    metavar = "LIST"
    help = "required generic resources"
    type = str


class Gres_flags(Pragma):
    arg_varname = "gres_flags"
    flags = ["--gres-flags"]
    dest = "--gres_flags"
    metavar = "OPTS"
    help = "flags related to GRES management"
    type = str


class Hold(Pragma):
    arg_varname = "hold"
    flags = ["-H", "--hold"]
    dest = "--hold"
    help = "submit job in held state"
    action = "store_true"
    type = str


class Immediate(Pragma):
    arg_varname = "immediate"
    flags = ["-I", "--immediate"]
    dest = "--immediate"
    metavar = "SECS"
    help = 'exit if resources not available in "secs"'
    nargs = "?"
    const = "0"
    type = str


class Job_name(Pragma):
    arg_varname = "job_name"
    flags = ["-J", "--job-name"]
    dest = "--job_name"
    metavar = "NAME"
    help = "name of job"
    example = "my_job"
    type = str


class No_kill(Pragma):
    arg_varname = "no_kill"
    flags = ["-k", "--no-kill"]
    dest = "--no_kill"
    help = "do not kill job on node failure"
    action = "store_true"
    type = str


class Kill_command(Pragma):
    arg_varname = "kill_command"
    flags = ["-K", "--kill-command"]
    dest = "--kill_command"
    metavar = "SIGNAL"
    help = "signal to send terminating job"
    nargs = "?"
    const = "TERM"
    type = str


class Licenses(Pragma):
    arg_varname = "licenses"
    flags = ["-L", "--licenses"]
    dest = "--licenses"
    metavar = "NAMES"
    help = "required license, comma separated"
    type = str


class Clusters(Pragma):
    arg_varname = "clusters"
    flags = ["-M", "--clusters"]
    dest = "--clusters"
    metavar = "NAMES"
    help = "Comma separated list of clusters to issue commands to"
    type = str


class Distribution(Pragma):
    arg_varname = "distribution"
    flags = ["-m", "--distribution"]
    dest = "--distribution"
    metavar = "TYPE"
    help = "distribution method for processes to nodes"
    choices = ["block", "cyclic", "arbitrary"]
    type = str


class Mail_type(Pragma):
    arg_varname = "mail_type"
    flags = ["--mail-type"]
    dest = "--mail_type"
    metavar = "TYPE"
    help = "notify on state change"
    example = "ALL"
    choices = ["NONE", "BEGIN", "END", "FAIL", "REQUEUE", "ALL"]
    type = str


class Mail_user(Pragma):
    arg_varname = "mail_user"
    flags = ["--mail-user"]
    dest = "--mail_user"
    metavar = "USER"
    help = "who to send email notification for job state changes"
    example = "example@email.com"
    type = str


class Mcs_label(Pragma):
    arg_varname = "mcs_label"
    flags = ["--mcs-label"]
    dest = "--mcs_label"
    metavar = "MCS"
    help = "mcs label if mcs plugin mcs/group is used"
    type = str


class Ntasks(Pragma):
    arg_varname = "ntasks"
    flags = ["-n", "--ntasks"]
    dest = "--ntasks"
    metavar = "N"
    help = "number of processors required"
    example = "16"
    type = str


class Nice(Pragma):
    arg_varname = "nice"
    flags = ["--nice"]
    dest = "--nice"
    metavar = "VALUE"
    help = "decrease scheduling priority by value"
    example = "1"
    type = str


class Nodes(Pragma):
    """
    This class represents the SLURM #SBATCH --nodes pragma,
    which specifies the number of nodes to allocate for a job.

    args:
        value (int): The number of nodes to allocate for the job.
    """

    arg_varname = "nodes"
    flags = ["-N", "--nodes"]
    dest = "--nodes"
    metavar = "NODES"
    help = "number of nodes on which to run"
    example = "2"
    type = int


class Ntasks_per_node(Pragma):
    """
    This class represents the SLURM #SBATCH --ntasks-per-node pragma,
    which specifies the number of tasks to invoke on each node.
    """

    arg_varname = "ntasks_per_node"
    flags = ["--ntasks-per-node"]
    dest = "--ntasks_per_node"
    metavar = "N"
    help = "number of tasks to invoke on each node"
    example = "16"
    type = int


class Oom_kill_step(Pragma):
    arg_varname = "oom_kill_step"
    flags = ["--oom-kill-step"]
    dest = "--oom_kill_step"
    metavar = "0|1"
    help = "set the OOMKillStep behaviour"
    nargs = "?"
    const = "1"
    type = str


class Overcommit(Pragma):
    arg_varname = "overcommit"
    flags = ["-O", "--overcommit"]
    dest = "--overcommit"
    help = "overcommit resources"
    action = "store_true"
    type = str


class Power(Pragma):
    arg_varname = "power"
    flags = ["--power"]
    dest = "--power"
    metavar = "FLAGS"
    help = "power management options"
    type = str


class Priority(Pragma):
    arg_varname = "priority"
    flags = ["--priority"]
    dest = "--priority"
    metavar = "VALUE"
    help = "set the priority of the job"
    type = str


class Profile(Pragma):
    arg_varname = "profile"
    flags = ["--profile"]
    dest = "--profile"
    metavar = "VALUE"
    help = "enable acct_gather_profile for detailed data"
    type = str


class Partition(Pragma):
    arg_varname = "partition"
    flags = ["-p", "--partition"]
    dest = "--partition"
    metavar = "PARTITION"
    help = "partition requested"
    type = str


class Qos(Pragma):
    arg_varname = "qos"
    flags = ["-q", "--qos"]
    dest = "--qos"
    metavar = "QOS"
    help = "quality of service"
    type = str


class Quiet(Pragma):
    arg_varname = "quiet"
    flags = ["-Q", "--quiet"]
    dest = "--quiet"
    help = "quiet mode (suppress informational messages)"
    action = "store_true"
    type = str


class Reboot(Pragma):
    arg_varname = "reboot"
    flags = ["--reboot"]
    dest = "--reboot"
    help = "reboot compute nodes before starting job"
    action = "store_true"
    type = str


class Oversubscribe(Pragma):
    arg_varname = "oversubscribe"
    flags = ["-s", "--oversubscribe"]
    dest = "--oversubscribe"
    help = "oversubscribe resources with other jobs"
    action = "store_true"
    type = str


class Signal(Pragma):
    arg_varname = "signal"
    flags = ["--signal"]
    dest = "--signal"
    metavar = "[R:]NUM[@TIME]"
    help = "send signal when time limit within time seconds"
    type = str


class Spread_job(Pragma):
    arg_varname = "spread_job"
    flags = ["--spread-job"]
    dest = "--spread_job"
    help = "spread job across as many nodes as possible"
    action = "store_true"
    type = str


class Stderr(Pragma):
    arg_varname = "stderr"
    flags = ["--stderr", "-e"]
    dest = "-e"
    metavar = "STDERR"
    help = "File to redirect stderr (%%x=jobname, %%j=jobid)"
    example = "--stderr ./%x.%j.err"
    type = str


class Stdout(Pragma):
    arg_varname = "stdout"
    flags = ["--stdout", "-o"]
    dest = "-o"
    metavar = "STDOUT"
    help = "File to redirect stdout (%%x=jobname, %%j=jobid)"
    example = "--stdout ./%x.%j.out"
    type = str


class Switches(Pragma):
    arg_varname = "switches"
    flags = ["--switches"]
    dest = "--switches"
    metavar = "MAX_SWITCHES[@MAX_TIME]"
    help = "optimum switches and max time to wait for optimum"
    type = str


class Core_spec(Pragma):
    arg_varname = "core_spec"
    flags = ["-S", "--core-spec"]
    dest = "--core_spec"
    metavar = "CORES"
    help = "count of reserved cores"
    type = str


class Thread_spec(Pragma):
    arg_varname = "thread_spec"
    flags = ["--thread-spec"]
    dest = "--thread_spec"
    metavar = "THREADS"
    help = "count of reserved threads"
    type = str


class Time(Pragma):
    arg_varname = "time"
    flags = ["-t", "--time"]
    dest = "--time"
    metavar = "MINUTES"
    help = "time limit"
    example = "00:45:00"
    type = str


class Time_min(Pragma):
    arg_varname = "time_min"
    flags = ["--time-min"]
    dest = "--time_min"
    metavar = "MINUTES"
    help = "minimum time limit (if distinct)"
    type = str


class Tres_bind(Pragma):
    arg_varname = "tres_bind"
    flags = ["--tres-bind"]
    dest = "--tres_bind"
    metavar = "..."
    help = "task to tres binding options"
    type = str


class Tres_per_task(Pragma):
    arg_varname = "tres_per_task"
    flags = ["--tres-per-task"]
    dest = "--tres_per_task"
    metavar = "LIST"
    help = "list of tres required per task"
    type = str


class Use_min_nodes(Pragma):
    arg_varname = "use_min_nodes"
    flags = ["--use-min-nodes"]
    dest = "--use_min_nodes"
    help = "if a range of node counts is given, prefer the smaller count"
    action = "store_true"
    type = str


class Wckey(Pragma):
    arg_varname = "wckey"
    flags = ["--wckey"]
    dest = "--wckey"
    metavar = "WCKEY"
    help = "wckey to run job under"
    type = str


class Cluster_constraint(Pragma):
    arg_varname = "cluster_constraint"
    flags = ["--cluster-constraint"]
    dest = "--cluster_constraint"
    metavar = "LIST"
    help = "specify a list of cluster constraints"
    type = str


class Contiguous(Pragma):
    arg_varname = "contiguous"
    flags = ["--contiguous"]
    dest = "--contiguous"
    help = "demand a contiguous range of nodes"
    action = "store_true"
    type = str


class Constraint(Pragma):
    arg_varname = "constraint"
    flags = ["-C", "--constraint"]
    dest = "--constraint"
    metavar = "LIST"
    help = "specify a list of constraints"
    type = str


class Nodefile(Pragma):
    arg_varname = "nodefile"
    flags = ["-F", "--nodefile"]
    dest = "--nodefile"
    metavar = "FILENAME"
    help = "request a specific list of hosts"
    type = str


class Mem(Pragma):
    arg_varname = "mem"
    flags = ["--mem"]
    dest = "--mem"
    metavar = "MB"
    help = "minimum amount of real memory"
    example = "25GB"
    type = str


class Mincpus(Pragma):
    arg_varname = "mincpus"
    flags = ["--mincpus"]
    dest = "--mincpus"
    metavar = "N"
    help = "minimum number of logical processors per node"
    type = str


class Reservation(Pragma):
    arg_varname = "reservation"
    flags = ["--reservation"]
    dest = "--reservation"
    metavar = "NAME"
    help = "allocate resources from named reservation"
    type = str


class Tmp(Pragma):
    arg_varname = "tmp"
    flags = ["--tmp"]
    dest = "--tmp"
    metavar = "MB"
    help = "minimum amount of temporary disk"
    type = str


class Nodelist(Pragma):
    arg_varname = "nodelist"
    flags = ["-w", "--nodelist"]
    dest = "--nodelist"
    metavar = "HOST"
    help = "request a specific list of hosts"
    nargs = "+"
    type = str


class Exclude(Pragma):
    arg_varname = "exclude"
    flags = ["-x", "--exclude"]
    dest = "--exclude"
    metavar = "HOST"
    help = "exclude a specific list of hosts"
    nargs = "+"
    type = str


class Exclusive_user(Pragma):
    arg_varname = "exclusive_user"
    flags = ["--exclusive-user"]
    dest = "--exclusive_user"
    help = "allocate nodes in exclusive mode for cpu consumable resource"
    action = "store_true"
    type = str


class Exclusive_mcs(Pragma):
    arg_varname = "exclusive_mcs"
    flags = ["--exclusive-mcs"]
    dest = "--exclusive_mcs"
    help = "allocate nodes in exclusive mode when mcs plugin is enabled"
    action = "store_true"
    type = str


class Mem_per_cpu(Pragma):
    arg_varname = "mem_per_cpu"
    flags = ["--mem-per-cpu"]
    dest = "--mem_per_cpu"
    metavar = "MB"
    help = "maximum amount of real memory per allocated cpu"
    type = str


class Resv_ports(Pragma):
    arg_varname = "resv_ports"
    flags = ["--resv-ports"]
    dest = "--resv_ports"
    help = "reserve communication ports"
    action = "store_true"
    type = str


class Sockets_per_node(Pragma):
    arg_varname = "sockets_per_node"
    flags = ["--sockets-per-node"]
    dest = "--sockets_per_node"
    metavar = "S"
    help = "number of sockets per node to allocate"
    type = str


class Cores_per_socket(Pragma):
    arg_varname = "cores_per_socket"
    flags = ["--cores-per-socket"]
    dest = "--cores_per_socket"
    metavar = "C"
    help = "number of cores per socket to allocate"
    example = "8"
    type = str


class Threads_per_core(Pragma):
    arg_varname = "threads_per_core"
    flags = ["--threads-per-core"]
    dest = "--threads_per_core"
    metavar = "T"
    help = "number of threads per core to allocate"
    example = "4"
    type = str


class Extra_node_info(Pragma):
    arg_varname = "extra_node_info"
    flags = ["-B", "--extra-node-info"]
    dest = "--extra_node_info"
    metavar = "S[:C[:T]]"
    help = "combine request of sockets, cores and threads"
    type = str


class Ntasks_per_core(Pragma):
    arg_varname = "ntasks_per_core"
    flags = ["--ntasks-per-core"]
    dest = "--ntasks_per_core"
    metavar = "N"
    help = "number of tasks to invoke on each core"
    example = "16"
    type = str


class Ntasks_per_socket(Pragma):
    arg_varname = "ntasks_per_socket"
    flags = ["--ntasks-per-socket"]
    dest = "--ntasks_per_socket"
    metavar = "N"
    help = "number of tasks to invoke on each socket"
    example = "8"
    type = str


class Hint(Pragma):
    arg_varname = "hint"
    flags = ["--hint"]
    dest = "--hint"
    metavar = "HINT"
    help = "Bind tasks according to application hints"
    type = str


class Mem_bind(Pragma):
    arg_varname = "mem_bind"
    flags = ["--mem-bind"]
    dest = "--mem_bind"
    metavar = "BIND"
    help = "Bind memory to locality domains"
    type = str


class Cpus_per_gpu(Pragma):
    arg_varname = "cpus_per_gpu"
    flags = ["--cpus-per-gpu"]
    dest = "--cpus_per_gpu"
    metavar = "N"
    help = "number of CPUs required per allocated GPU"
    example = "4"
    type = str


class Gpus(Pragma):
    arg_varname = "gpus"
    flags = ["-G", "--gpus"]
    dest = "--gpus"
    metavar = "N"
    help = "count of GPUs required for the job"
    example = "32"
    type = str


class Gpu_bind(Pragma):
    arg_varname = "gpu_bind"
    flags = ["--gpu-bind"]
    dest = "--gpu_bind"
    metavar = "..."
    help = "task to gpu binding options"
    type = str


class Gpu_freq(Pragma):
    arg_varname = "gpu_freq"
    flags = ["--gpu-freq"]
    dest = "--gpu_freq"
    metavar = "..."
    help = "frequency and voltage of GPUs"
    type = str


class Gpus_per_node(Pragma):
    arg_varname = "gpus_per_node"
    flags = ["--gpus-per-node"]
    dest = "--gpus_per_node"
    metavar = "N"
    help = "number of GPUs required per allocated node"
    type = str


class Gpus_per_socket(Pragma):
    arg_varname = "gpus_per_socket"
    flags = ["--gpus-per-socket"]
    dest = "--gpus_per_socket"
    metavar = "N"
    help = "number of GPUs required per allocated socket"
    type = str


class Gpus_per_task(Pragma):
    arg_varname = "gpus_per_task"
    flags = ["--gpus-per-task"]
    dest = "--gpus_per_task"
    metavar = "N"
    help = "number of GPUs required per spawned task"
    type = str


class Mem_per_gpu(Pragma):
    arg_varname = "mem_per_gpu"
    flags = ["--mem-per-gpu"]
    dest = "--mem_per_gpu"
    help = "real memory required per allocated GPU"
    example = "8GB"
    type = str


class Disable_stdout_job_summary(Pragma):
    arg_varname = "disable_stdout_job_summary"
    flags = ["--disable-stdout-job-summary"]
    dest = "--disable_stdout_job_summary"
    help = "disable job summary in stdout file for the job"
    action = "store_true"
    type = str


class Nvmps(Pragma):
    arg_varname = "nvmps"
    flags = ["--nvmps"]
    dest = "--nvmps"
    help = "launching NVIDIA MPS for job"
    action = "store_true"
    type = str


class PragmaFactory:
    pragmas = {
        pragma_cls.arg_varname: pragma_cls
        for _, pragma_cls in list(globals().items())
        if (
            isinstance(pragma_cls, type)
            and issubclass(pragma_cls, Pragma)
            and pragma_cls is not Pragma
        )
    }

    @staticmethod
    def is_valid_pragma_key(key: str) -> bool:
        return key in PragmaFactory.pragmas

    @staticmethod
    def create_pragma(key: str, value: str) -> Pragma:
        if key not in PragmaFactory.pragmas:
            raise ValueError(f"Unknown pragma key: {key}")
        return PragmaFactory.pragmas[key](value)

    @staticmethod
    def flag_to_pragma(flag: str, value: str) -> Pragma | None:
        for pragma_cls in PragmaFactory.pragmas.values():
            if flag in pragma_cls.flags:
                return pragma_cls(value=value)
        raise ValueError(f"Unknown pragma flag: {flag}")

    @staticmethod
    def get_pragma_cls(key: str) -> Type[Pragma]:
        if key not in PragmaFactory.pragmas:
            raise ValueError(f"Unknown pragma key: {key}")
        return PragmaFactory.pragmas[key]


if __name__ == "__main__":
    acc = Account("max")
    print(acc.to_dict())
