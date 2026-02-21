from typing import Any, Callable, List, Literal, Type

from slurm_script_generator.utils import add_line

PragmaTypes = Literal[
    "job_config",
    "time_and_priority",
    "io_and_directory",
    "notifications",
    "dependencies_and_arrays",
    "core_node_and_task_allocation",
    "cpu_topology_and_binding",
    "memory",
    "gpus",
    "generic_resources_and_licenses",
    "node_constraints_and_selection",
    "exclusivity_and_sharing",
    "execution_behavior_and_signals",
    "advanced_hardware_misc",
    "plugins",
]


class Pragma:
    """Base class representing a SLURM #SBATCH pragma."""

    arg_varname: str
    pragma_type: PragmaTypes
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
    pragma_id: int = 0

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


# --- 1. Job Identification & Basic Info (job_config) ---
class Job_name(Pragma):
    pragma_type = "job_config"
    arg_varname = "job_name"
    flags = ["-J", "--job-name"]
    dest = "--job-name"
    metavar = "NAME"
    help = "name of job"
    example = "my_job"
    type = str


class Account(Pragma):
    """This class represents the SLURM #SBATCH --account pragma."""

    pragma_type = "job_config"
    arg_varname = "account"
    flags = ["-A", "--account"]
    dest = "--account"
    metavar = "NAME"
    help = "charge job to specified account"
    example = "myacct"
    type = str


class Partition(Pragma):
    pragma_type = "job_config"
    arg_varname = "partition"
    flags = ["-p", "--partition"]
    dest = "--partition"
    metavar = "PARTITION"
    help = "partition requested"
    type = str


class Qos(Pragma):
    pragma_type = "job_config"
    arg_varname = "qos"
    flags = ["-q", "--qos"]
    dest = "--qos"
    metavar = "QOS"
    help = "quality of service"
    type = str


class Clusters(Pragma):
    pragma_type = "job_config"
    arg_varname = "clusters"
    flags = ["-M", "--clusters"]
    dest = "--clusters"
    metavar = "NAMES"
    help = "Comma separated list of clusters to issue commands to"
    type = str


class Reservation(Pragma):
    pragma_type = "job_config"
    arg_varname = "reservation"
    flags = ["--reservation"]
    dest = "--reservation"
    metavar = "NAME"
    help = "allocate resources from named reservation"
    type = str


class Wckey(Pragma):
    pragma_type = "job_config"
    arg_varname = "wckey"
    flags = ["--wckey"]
    dest = "--wckey"
    metavar = "WCKEY"
    help = "wckey to run job under"
    type = str


class Mcs_label(Pragma):
    pragma_type = "job_config"
    arg_varname = "mcs_label"
    flags = ["--mcs-label"]
    dest = "--mcs-label"
    metavar = "MCS"
    help = "mcs label if mcs plugin mcs/group is used"
    type = str


class Comment(Pragma):
    pragma_type = "job_config"
    arg_varname = "comment"
    flags = ["--comment"]
    dest = "--comment"
    metavar = "NAME"
    help = "arbitrary comment"
    type = str


# --- 2. Time & Priority (time_and_priority) ---
class Time(Pragma):
    pragma_type = "time_and_priority"
    arg_varname = "time"
    flags = ["-t", "--time"]
    dest = "--time"
    metavar = "MINUTES"
    help = "time limit"
    example = "00:45:00"
    type = str


class Time_min(Pragma):
    pragma_type = "time_and_priority"
    arg_varname = "time_min"
    flags = ["--time-min"]
    dest = "--time_min"
    metavar = "MINUTES"
    help = "minimum time limit (if distinct)"
    type = str


class Begin(Pragma):
    pragma_type = "time_and_priority"
    arg_varname = "begin"
    flags = ["-b", "--begin"]
    dest = "--begin"
    metavar = "TIME"
    help = "defer job until HH:MM MM/DD/YY"
    type = str


class Deadline(Pragma):
    pragma_type = "time_and_priority"
    arg_varname = "deadline"
    flags = ["--deadline"]
    dest = "--deadline"
    metavar = "TIME"
    help = "remove the job if no ending possible before this deadline"
    type = str


class Priority(Pragma):
    pragma_type = "time_and_priority"
    arg_varname = "priority"
    flags = ["--priority"]
    dest = "--priority"
    metavar = "VALUE"
    help = "set the priority of the job"
    type = str


class Nice(Pragma):
    pragma_type = "time_and_priority"
    arg_varname = "nice"
    flags = ["--nice"]
    dest = "--nice"
    metavar = "VALUE"
    help = "decrease scheduling priority by value"
    example = "1"
    type = str


# --- 3. Standard IO & Directory (io_and_directory) ---
class Chdir(Pragma):
    pragma_type = "io_and_directory"
    arg_varname = "chdir"
    flags = ["-D", "--chdir"]
    dest = "--chdir"
    metavar = "PATH"
    help = "change working directory"
    type = str


class Stdout(Pragma):
    pragma_type = "io_and_directory"
    arg_varname = "stdout"
    flags = ["--stdout", "-o"]
    dest = "--stdout"
    metavar = "STDOUT"
    help = "File to redirect stdout (%x=jobname, %j=jobid)"
    example = "--stdout ./%x.%j.out"
    type = str


class Stderr(Pragma):
    pragma_type = "io_and_directory"
    arg_varname = "stderr"
    flags = ["--stderr", "-e"]
    dest = "--stderr"
    metavar = "STDERR"
    help = "File to redirect stderr (%x=jobname, %j=jobid)"
    example = "--stderr ./%x.%j.err"
    type = str


class Disable_stdout_job_summary(Pragma):
    pragma_type = "io_and_directory"
    arg_varname = "disable_stdout_job_summary"
    flags = ["--disable-stdout-job-summary"]
    dest = "--disable-stdout-job-summary"
    help = "disable job summary in stdout file for the job"
    action = "store_true"
    type = str


class Get_user_env(Pragma):
    pragma_type = "io_and_directory"
    arg_varname = "get_user_env"
    flags = ["--get-user-env"]
    dest = "--get-user-env"
    help = "used by Moab. See srun man page"
    action = "store_true"
    type = str


class Quiet(Pragma):
    pragma_type = "io_and_directory"
    arg_varname = "quiet"
    flags = ["-Q", "--quiet"]
    dest = "--quiet"
    help = "quiet mode (suppress informational messages)"
    action = "store_true"
    type = str


# --- 4. Notifications (notifications) ---
class Mail_user(Pragma):
    pragma_type = "notifications"
    arg_varname = "mail_user"
    flags = ["--mail-user"]
    dest = "--mail-user"
    metavar = "USER"
    help = "who to send email notification for job state changes"
    example = "example@email.com"
    type = str


class Mail_type(Pragma):
    pragma_type = "notifications"
    arg_varname = "mail_type"
    flags = ["--mail-type"]
    dest = "--mail-type"
    metavar = "TYPE"
    help = "notify on state change"
    example = "ALL"
    choices = ["NONE", "BEGIN", "END", "FAIL", "REQUEUE", "ALL"]
    type = str


class Bell(Pragma):
    pragma_type = "notifications"
    arg_varname = "bell"
    flags = ["--bell"]
    dest = "--bell"
    help = "ring the terminal bell when the job is allocated"
    action = "store_true"
    type = str


# --- 5. Dependencies & Job Arrays (dependencies_and_arrays) ---
class Dependency(Pragma):
    pragma_type = "dependencies_and_arrays"
    arg_varname = "dependency"
    flags = ["-d", "--dependency"]
    dest = "--dependency"
    metavar = "TYPE:JOBID[:TIME]"
    help = "defer job until condition on jobid is satisfied"
    type = str


class Array(Pragma):
    pragma_type = "dependencies_and_arrays"
    arg_varname = "array"
    flags = ["--array"]
    dest = "--array"
    metavar = "INDEXES"
    help = "submit a job array"
    type = str


# --- 6. Core Node & Task Allocation (core_node_and_task_allocation) ---
class Nodes(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "nodes"
    flags = ["-N", "--nodes"]
    dest = "--nodes"
    metavar = "NODES"
    help = "number of nodes on which to run"
    example = "2"
    type = int


class Ntasks(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "ntasks"
    flags = ["-n", "--ntasks"]
    dest = "--ntasks"
    metavar = "N"
    help = "number of processors required"
    example = "16"
    type = str


class Ntasks_per_node(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "ntasks_per_node"
    flags = ["--ntasks-per-node"]
    dest = "--ntasks-per-node"
    metavar = "N"
    help = "number of tasks to invoke on each node"
    example = "16"
    type = int


class Cpus_per_task(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "cpus_per_task"
    flags = ["-c", "--cpus-per-task"]
    dest = "--cpus-per-task"
    metavar = "NCPUS"
    help = "number of cpus required per task"
    example = "16"
    type = str


class Mincpus(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "mincpus"
    flags = ["--mincpus"]
    dest = "--mincpus"
    metavar = "N"
    help = "minimum number of logical processors per node"
    type = str


class Distribution(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "distribution"
    flags = ["-m", "--distribution"]
    dest = "--distribution"
    metavar = "TYPE"
    help = "distribution method for processes to nodes"
    choices = ["block", "cyclic", "arbitrary"]
    type = str


class Spread_job(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "spread_job"
    flags = ["--spread-job"]
    dest = "--spread-job"
    help = "spread job across as many nodes as possible"
    action = "store_true"
    type = str


class Use_min_nodes(Pragma):
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "use_min_nodes"
    flags = ["--use-min-nodes"]
    dest = "--use-min-nodes"
    help = "if a range of node counts is given, prefer the smaller count"
    action = "store_true"
    type = str


# --- 7. CPU Topology & Binding (cpu_topology_and_binding) ---
class Sockets_per_node(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "sockets_per_node"
    flags = ["--sockets-per-node"]
    dest = "--sockets-per-node"
    metavar = "S"
    help = "number of sockets per node to allocate"
    type = str


class Cores_per_socket(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "cores_per_socket"
    flags = ["--cores-per-socket"]
    dest = "--cores-per-socket"
    metavar = "C"
    help = "number of cores per socket to allocate"
    example = "8"
    type = str


class Threads_per_core(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "threads_per_core"
    flags = ["--threads-per-core"]
    dest = "--threads-per-core"
    metavar = "T"
    help = "number of threads per core to allocate"
    example = "4"
    type = str


class Ntasks_per_core(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "ntasks_per_core"
    flags = ["--ntasks-per-core"]
    dest = "--ntasks-per-core"
    metavar = "N"
    help = "number of tasks to invoke on each core"
    example = "16"
    type = str


class Ntasks_per_socket(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "ntasks_per_socket"
    flags = ["--ntasks-per-socket"]
    dest = "--ntasks-per-socket"
    metavar = "N"
    help = "number of tasks to invoke on each socket"
    example = "8"
    type = str


class Extra_node_info(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "extra_node_info"
    flags = ["-B", "--extra-node-info"]
    dest = "--extra-node-info"
    metavar = "S[:C[:T]]"
    help = "combine request of sockets, cores and threads"
    type = str


class Hint(Pragma):
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "hint"
    flags = ["--hint"]
    dest = "--hint"
    metavar = "HINT"
    help = "Bind tasks according to application hints"
    type = str


# --- 8. Memory (memory) ---
class Mem(Pragma):
    pragma_type = "memory"
    arg_varname = "mem"
    flags = ["--mem"]
    dest = "--mem"
    metavar = "MB"
    help = "minimum amount of real memory"
    example = "25GB"
    type = str


class Mem_per_cpu(Pragma):
    pragma_type = "memory"
    arg_varname = "mem_per_cpu"
    flags = ["--mem-per-cpu"]
    dest = "--mem-per-cpu"
    metavar = "MB"
    help = "maximum amount of real memory per allocated cpu"
    type = str


class Mem_bind(Pragma):
    pragma_type = "memory"
    arg_varname = "mem_bind"
    flags = ["--mem-bind"]
    dest = "--mem-bind"
    metavar = "BIND"
    help = "Bind memory to locality domains"
    type = str


class Oom_kill_step(Pragma):
    pragma_type = "memory"
    arg_varname = "oom_kill_step"
    flags = ["--oom-kill-step"]
    dest = "--oom-kill-step"
    metavar = "0|1"
    help = "set the OOMKillStep behaviour"
    nargs = "?"
    const = "1"
    type = str


# --- 9. GPUs (gpus) ---
class Gpus(Pragma):
    pragma_type = "gpus"
    arg_varname = "gpus"
    flags = ["-G", "--gpus"]
    dest = "--gpus"
    metavar = "N"
    help = "count of GPUs required for the job"
    example = "32"
    type = str


class Gpus_per_node(Pragma):
    pragma_type = "gpus"
    arg_varname = "gpus_per_node"
    flags = ["--gpus-per-node"]
    dest = "--gpus-per-node"
    metavar = "N"
    help = "number of GPUs required per allocated node"
    type = str


class Gpus_per_task(Pragma):
    pragma_type = "gpus"
    arg_varname = "gpus_per_task"
    flags = ["--gpus-per-task"]
    dest = "--gpus-per-task"
    metavar = "N"
    help = "number of GPUs required per spawned task"
    type = str


class Gpus_per_socket(Pragma):
    pragma_type = "gpus"
    arg_varname = "gpus_per_socket"
    flags = ["--gpus-per-socket"]
    dest = "--gpus-per-socket"
    metavar = "N"
    help = "number of GPUs required per allocated socket"
    type = str


class Cpus_per_gpu(Pragma):
    pragma_type = "gpus"
    arg_varname = "cpus_per_gpu"
    flags = ["--cpus-per-gpu"]
    dest = "--cpus-per-gpu"
    metavar = "N"
    help = "number of CPUs required per allocated GPU"
    example = "4"
    type = str


class Mem_per_gpu(Pragma):
    pragma_type = "gpus"
    arg_varname = "mem_per_gpu"
    flags = ["--mem-per-gpu"]
    dest = "--mem-per-gpu"
    help = "real memory required per allocated GPU"
    example = "8GB"
    type = str


class Gpu_bind(Pragma):
    pragma_type = "gpus"
    arg_varname = "gpu_bind"
    flags = ["--gpu-bind"]
    dest = "--gpu-bind"
    metavar = "..."
    help = "task to gpu binding options"
    type = str


class Gpu_freq(Pragma):
    pragma_type = "gpus"
    arg_varname = "gpu_freq"
    flags = ["--gpu-freq"]
    dest = "--gpu-freq"
    metavar = "..."
    help = "frequency and voltage of GPUs"
    type = str


class Nvmps(Pragma):
    pragma_type = "gpus"
    arg_varname = "nvmps"
    flags = ["--nvmps"]
    dest = "--nvmps"
    help = "launching NVIDIA MPS for job"
    action = "store_true"
    type = str


# --- 10. Generic Resources & Licenses (generic_resources_and_licenses) ---
class Gres(Pragma):
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "gres"
    flags = ["--gres"]
    dest = "--gres"
    metavar = "LIST"
    help = "required generic resources"
    type = str


class Gres_flags(Pragma):
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "gres_flags"
    flags = ["--gres-flags"]
    dest = "--gres-flags"
    metavar = "OPTS"
    help = "flags related to GRES management"
    type = str


class Tres_bind(Pragma):
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "tres_bind"
    flags = ["--tres-bind"]
    dest = "--tres-bind"
    metavar = "..."
    help = "task to tres binding options"
    type = str


class Tres_per_task(Pragma):
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "tres_per_task"
    flags = ["--tres-per-task"]
    dest = "--tres-per-task"
    metavar = "LIST"
    help = "list of tres required per task"
    type = str


class Licenses(Pragma):
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "licenses"
    flags = ["-L", "--licenses"]
    dest = "--licenses"
    metavar = "NAMES"
    help = "required license, comma separated"
    type = str


# --- 11. Node Constraints & Selection (node_constraints_and_selection) ---
class Constraint(Pragma):
    pragma_type = "node_constraints_and_selection"
    arg_varname = "constraint"
    flags = ["-C", "--constraint"]
    dest = "--constraint"
    metavar = "LIST"
    help = "specify a list of constraints"
    type = str


class Cluster_constraint(Pragma):
    pragma_type = "node_constraints_and_selection"
    arg_varname = "cluster_constraint"
    flags = ["--cluster-constraint"]
    dest = "--cluster-constraint"
    metavar = "LIST"
    help = "specify a list of cluster constraints"
    type = str


class Contiguous(Pragma):
    pragma_type = "node_constraints_and_selection"
    arg_varname = "contiguous"
    flags = ["--contiguous"]
    dest = "--contiguous"
    help = "demand a contiguous range of nodes"
    action = "store_true"
    type = str


class Nodelist(Pragma):
    pragma_type = "node_constraints_and_selection"
    arg_varname = "nodelist"
    flags = ["-w", "--nodelist"]
    dest = "--nodelist"
    metavar = "HOST"
    help = "request a specific list of hosts"
    nargs = "+"
    type = str


class Nodefile(Pragma):
    pragma_type = "node_constraints_and_selection"
    arg_varname = "nodefile"
    flags = ["-F", "--nodefile"]
    dest = "--nodefile"
    metavar = "FILENAME"
    help = "request a specific list of hosts"
    type = str


class Exclude(Pragma):
    pragma_type = "node_constraints_and_selection"
    arg_varname = "exclude"
    flags = ["-x", "--exclude"]
    dest = "--exclude"
    metavar = "HOST"
    help = "exclude a specific list of hosts"
    nargs = "+"
    type = str


# --- 12. Exclusivity & Sharing (exclusivity_and_sharing) ---
class Exclusive_user(Pragma):
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "exclusive_user"
    flags = ["--exclusive-user"]
    dest = "--exclusive-user"
    help = "allocate nodes in exclusive mode for cpu consumable resource"
    action = "store_true"
    type = str


class Exclusive_mcs(Pragma):
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "exclusive_mcs"
    flags = ["--exclusive-mcs"]
    dest = "--exclusive-mcs"
    help = "allocate nodes in exclusive mode when mcs plugin is enabled"
    action = "store_true"
    type = str


class Oversubscribe(Pragma):
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "oversubscribe"
    flags = ["-s", "--oversubscribe"]
    dest = "--oversubscribe"
    help = "oversubscribe resources with other jobs"
    action = "store_true"
    type = str


class Overcommit(Pragma):
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "overcommit"
    flags = ["-O", "--overcommit"]
    dest = "--overcommit"
    help = "overcommit resources"
    action = "store_true"
    type = str


# --- 13. Execution Behavior & Signals (execution_behavior_and_signals) ---
class Hold(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "hold"
    flags = ["-H", "--hold"]
    dest = "--hold"
    help = "submit job in held state"
    action = "store_true"
    type = str


class Immediate(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "immediate"
    flags = ["-I", "--immediate"]
    dest = "--immediate"
    metavar = "SECS"
    help = 'exit if resources not available in "secs"'
    nargs = "?"
    const = "0"
    type = str


class Reboot(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "reboot"
    flags = ["--reboot"]
    dest = "--reboot"
    help = "reboot compute nodes before starting job"
    action = "store_true"
    type = str


class Delay_boot(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "delay_boot"
    flags = ["--delay-boot"]
    dest = "--delay_boot"
    metavar = "MINS"
    help = "delay boot for desired node features"
    type = str


class No_kill(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "no_kill"
    flags = ["-k", "--no-kill"]
    dest = "--no-kill"
    help = "do not kill job on node failure"
    action = "store_true"
    type = str


class Kill_command(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "kill_command"
    flags = ["-K", "--kill-command"]
    dest = "--kill-command"
    metavar = "SIGNAL"
    help = "signal to send terminating job"
    nargs = "?"
    const = "TERM"
    type = str


class Signal(Pragma):
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "signal"
    flags = ["--signal"]
    dest = "--signal"
    metavar = "[R:]NUM[@TIME]"
    help = "send signal when time limit within time seconds"
    type = str


# --- 14. Advanced / Hardware / Misc (advanced_hardware_misc) ---
class Core_spec(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "core_spec"
    flags = ["-S", "--core-spec"]
    dest = "--core-spec"
    metavar = "CORES"
    help = "count of reserved cores"
    type = str


class Thread_spec(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "thread_spec"
    flags = ["--thread-spec"]
    dest = "--thread-spec"
    metavar = "THREADS"
    help = "count of reserved threads"
    type = str


class Cpu_freq(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "cpu_freq"
    flags = ["--cpu-freq"]
    dest = "--cpu-freq"
    metavar = "MIN[-MAX[:GOV]]"
    help = "requested cpu frequency (and governor)"
    type = str


class Tmp(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "tmp"
    flags = ["--tmp"]
    dest = "--tmp"
    metavar = "MB"
    help = "minimum amount of temporary disk"
    type = str


class Resv_ports(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "resv_ports"
    flags = ["--resv-ports"]
    dest = "--resv-ports"
    help = "reserve communication ports"
    action = "store_true"
    type = str


class Switches(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "switches"
    flags = ["--switches"]
    dest = "--switches"
    metavar = "MAX_SWITCHES[@MAX_TIME]"
    help = "optimum switches and max time to wait for optimum"
    type = str


class Power(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "power"
    flags = ["--power"]
    dest = "--power"
    metavar = "FLAGS"
    help = "power management options"
    type = str


class Profile(Pragma):
    pragma_type = "advanced_hardware_misc"
    arg_varname = "profile"
    flags = ["--profile"]
    dest = "--profile"
    metavar = "VALUE"
    help = "enable acct_gather_profile for detailed data"
    type = str


# --- 15. Plugins (Burst Buffer & Containers) ---
class Burst_buffer(Pragma):
    pragma_type = "plugins"
    arg_varname = "burst_buffer"
    flags = ["--bb"]
    dest = "--burst-buffer"
    metavar = "SPEC"
    help = "burst buffer specifications"
    type = str


class Bb_file(Pragma):
    pragma_type = "plugins"
    arg_varname = "bb_file"
    flags = ["--bbf"]
    dest = "--bb-file"
    metavar = "FILE_NAME"
    help = "burst buffer specification file"
    type = str


class Container(Pragma):
    pragma_type = "plugins"
    arg_varname = "container"
    flags = ["--container"]
    dest = "--container"
    metavar = "PATH"
    help = "Path to OCI container bundle"
    type = str


class Container_id(Pragma):
    pragma_type = "plugins"
    arg_varname = "container_id"
    flags = ["--container-id"]
    dest = "--container-id"
    metavar = "ID"
    help = "OCI container ID"
    type = str


pragmas_ordered: List[Type[Pragma]] = [
    # --- Job Identification & Basic Info ---
    Job_name,
    Account,
    Partition,
    Qos,
    Clusters,
    Reservation,
    Wckey,
    Mcs_label,
    Comment,
    # --- Time & Priority ---
    Time,
    Time_min,
    Begin,
    Deadline,
    Priority,
    Nice,
    # --- Standard IO & Directory ---
    Chdir,
    Stdout,
    Stderr,
    Disable_stdout_job_summary,
    Get_user_env,
    Quiet,
    # --- Notifications ---
    Mail_user,
    Mail_type,
    Bell,
    # --- Dependencies & Job Arrays ---
    Dependency,
    Array,
    # --- Core Node & Task Allocation ---
    Nodes,
    Ntasks,
    Ntasks_per_node,
    Cpus_per_task,
    Mincpus,
    Distribution,
    Spread_job,
    Use_min_nodes,
    # --- CPU Topology & Binding ---
    Sockets_per_node,
    Cores_per_socket,
    Threads_per_core,
    Ntasks_per_core,
    Ntasks_per_socket,
    Extra_node_info,
    Hint,
    # --- Memory ---
    Mem,
    Mem_per_cpu,
    Mem_bind,
    Oom_kill_step,
    # --- GPUs ---
    Gpus,
    Gpus_per_node,
    Gpus_per_task,
    Gpus_per_socket,
    Cpus_per_gpu,
    Mem_per_gpu,
    Gpu_bind,
    Gpu_freq,
    Nvmps,
    # --- Generic Resources (GRES/TRES) & Licenses ---
    Gres,
    Gres_flags,
    Tres_bind,
    Tres_per_task,
    Licenses,
    # --- Node Constraints & Specific Selection ---
    Constraint,
    Cluster_constraint,
    Contiguous,
    Nodelist,
    Nodefile,
    Exclude,
    # --- Exclusivity & Sharing ---
    Exclusive_user,
    Exclusive_mcs,
    Oversubscribe,
    Overcommit,
    # --- Execution Behavior & Signals ---
    Hold,
    Immediate,
    Reboot,
    Delay_boot,
    No_kill,
    Kill_command,
    Signal,
    # --- Advanced / Hardware / Misc ---
    Core_spec,
    Thread_spec,
    Cpu_freq,
    Tmp,
    Resv_ports,
    Switches,
    Power,
    Profile,
    # --- Plugins (Burst Buffer & Containers) ---
    Burst_buffer,
    Bb_file,
    Container,
    Container_id,
]


class PragmaFactory:
    pragmas = {pragma_cls.arg_varname: pragma_cls for pragma_cls in pragmas_ordered}

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

    # for pragma in PragmaFactory.pragmas.values():
    #     print(f"{pragma.__name__},")
