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
    pragma_id: int
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

    def __init__(self, value: str):
        """Initialize the Pragma with a value, converting it to the correct type if possible.

        Args:
            value: The value to set for this pragma.
        """
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
    """
    Represents the SLURM #SBATCH --job-name pragma.
    Sets a custom name for the submitted job, which appears in job listings and output files.
    Usage: --job-name <NAME>
    """

    pragma_id = 0
    pragma_type = "job_config"
    arg_varname = "job_name"
    flags = ["-J", "--job-name"]
    dest = "--job-name"
    metavar = "NAME"
    help = "name of job"
    example = "my_job"
    type = str


class Account(Pragma):
    """
    Represents the SLURM #SBATCH --account pragma.
    Specifies the account to charge for resource usage of the job.
    Usage: --account <ACCOUNT_NAME>
    """

    """This class represents the SLURM #SBATCH --account pragma."""

    pragma_id = 1
    pragma_type = "job_config"
    arg_varname = "account"
    flags = ["-A", "--account"]
    dest = "--account"
    metavar = "NAME"
    help = "charge job to specified account"
    example = "myacct"
    type = str


class Partition(Pragma):
    """
    Represents the SLURM #SBATCH --partition pragma.
    Requests a specific partition (queue) for job scheduling.
    Usage: --partition <PARTITION>
    """

    pragma_id = 2
    pragma_type = "job_config"
    arg_varname = "partition"
    flags = ["-p", "--partition"]
    dest = "--partition"
    metavar = "PARTITION"
    help = "partition requested"
    type = str


class Qos(Pragma):
    """
    Represents the SLURM #SBATCH --qos pragma.
    Sets the quality of service for the job, affecting priority and limits.
    Usage: --qos <QOS>
    """

    pragma_id = 3
    pragma_type = "job_config"
    arg_varname = "qos"
    flags = ["-q", "--qos"]
    dest = "--qos"
    metavar = "QOS"
    help = "quality of service"
    type = str


class Clusters(Pragma):
    """
    Represents the SLURM #SBATCH --clusters pragma.
    Specifies a comma-separated list of clusters to issue commands to, for multi-cluster environments.
    Usage: --clusters <CLUSTER1,CLUSTER2,...>
    """

    pragma_id = 4
    pragma_type = "job_config"
    arg_varname = "clusters"
    flags = ["-M", "--clusters"]
    dest = "--clusters"
    metavar = "NAMES"
    help = "Comma separated list of clusters to issue commands to"
    type = str


class Reservation(Pragma):
    """
    Represents the SLURM #SBATCH --reservation pragma.
    Allocates resources from a named reservation, useful for reserved compute time or special projects.
    Usage: --reservation <RESERVATION_NAME>
    """

    pragma_id = 5
    pragma_type = "job_config"
    arg_varname = "reservation"
    flags = ["--reservation"]
    dest = "--reservation"
    metavar = "NAME"
    help = "allocate resources from named reservation"
    type = str


class Wckey(Pragma):
    """
    Represents the SLURM #SBATCH --wckey pragma.
    Runs the job under a specified workload key (wckey) for accounting or tracking purposes.
    Usage: --wckey <WCKEY>
    """

    pragma_id = 6
    pragma_type = "job_config"
    arg_varname = "wckey"
    flags = ["--wckey"]
    dest = "--wckey"
    metavar = "WCKEY"
    help = "wckey to run job under"
    type = str


class Mcs_label(Pragma):
    """
    Represents the SLURM #SBATCH --mcs-label pragma.
    Sets an MCS label if the mcs plugin is enabled, for group-based resource allocation.
    Usage: --mcs-label <LABEL>
    """

    pragma_id = 7
    pragma_type = "job_config"
    arg_varname = "mcs_label"
    flags = ["--mcs-label"]
    dest = "--mcs-label"
    metavar = "MCS"
    help = "mcs label if mcs plugin mcs/group is used"
    type = str


class Comment(Pragma):
    """
    Represents the SLURM #SBATCH --comment pragma.
    Adds an arbitrary comment to the job for annotation or tracking.
    Usage: --comment <TEXT>
    """

    pragma_id = 8
    pragma_type = "job_config"
    arg_varname = "comment"
    flags = ["--comment"]
    dest = "--comment"
    metavar = "NAME"
    help = "arbitrary comment"
    type = str


# --- 2. Time & Priority (time_and_priority) ---
class Time(Pragma):
    """
    Represents the SLURM #SBATCH --time pragma.
    Sets the maximum walltime for the job in minutes or HH:MM:SS format.
    Usage: --time <DURATION>
    """

    pragma_id = 0
    pragma_type = "time_and_priority"
    arg_varname = "time"
    flags = ["-t", "--time"]
    dest = "--time"
    metavar = "MINUTES"
    help = "time limit"
    example = "00:45:00"
    type = str


class Time_min(Pragma):
    """
    Represents the SLURM #SBATCH --time-min pragma.
    Specifies the minimum walltime for the job, if distinct from the maximum.
    Usage: --time-min <DURATION>
    """

    pragma_id = 1
    pragma_type = "time_and_priority"
    arg_varname = "time_min"
    flags = ["--time-min"]
    dest = "--time_min"
    metavar = "MINUTES"
    help = "minimum time limit (if distinct)"
    type = str


class Begin(Pragma):
    """
    Represents the SLURM #SBATCH --begin pragma.
    Defers job start until a specified time (absolute or relative).
    Usage: --begin <TIME>
    """

    pragma_id = 2
    pragma_type = "time_and_priority"
    arg_varname = "begin"
    flags = ["-b", "--begin"]
    dest = "--begin"
    metavar = "TIME"
    help = "defer job until HH:MM MM/DD/YY"
    type = str


class Deadline(Pragma):
    """
    Represents the SLURM #SBATCH --deadline pragma.
    Removes the job if it cannot finish before the specified deadline.
    Usage: --deadline <TIME>
    """

    pragma_id = 3
    pragma_type = "time_and_priority"
    arg_varname = "deadline"
    flags = ["--deadline"]
    dest = "--deadline"
    metavar = "TIME"
    help = "remove the job if no ending possible before this deadline"
    type = str


class Priority(Pragma):
    """
    Represents the SLURM #SBATCH --priority pragma.
    Sets the priority value for the job, influencing scheduling order.
    Usage: --priority <VALUE>
    """

    pragma_id = 4
    pragma_type = "time_and_priority"
    arg_varname = "priority"
    flags = ["--priority"]
    dest = "--priority"
    metavar = "VALUE"
    help = "set the priority of the job"
    type = str


class Nice(Pragma):
    """
    Represents the SLURM #SBATCH --nice pragma.
    Decreases the job's scheduling priority by the specified value.
    Usage: --nice <VALUE>
    """

    pragma_id = 5
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
    """
    Represents the SLURM #SBATCH --chdir pragma.
    Changes the working directory for the job before execution.
    Usage: --chdir <PATH>
    """

    pragma_id = 0
    pragma_type = "io_and_directory"
    arg_varname = "chdir"
    flags = ["-D", "--chdir"]
    dest = "--chdir"
    metavar = "PATH"
    help = "change working directory"
    type = str


class Stdout(Pragma):
    """
    Represents the SLURM #SBATCH --stdout pragma.
    Redirects job standard output to a specified file, supporting job and jobname variables.
    Usage: --stdout <FILE>
    """

    pragma_id = 1
    pragma_type = "io_and_directory"
    arg_varname = "stdout"
    flags = ["--stdout", "-o"]
    dest = "--stdout"
    metavar = "STDOUT"
    help = "File to redirect stdout (%%x=jobname, %%j=jobid)"
    example = "--stdout ./%x.%j.out"
    type = str


class Stderr(Pragma):
    """
    Represents the SLURM #SBATCH --stderr pragma.
    Redirects job standard error to a specified file, supporting job and jobname variables.
    Usage: --stderr <FILE>
    """

    pragma_id = 2
    pragma_type = "io_and_directory"
    arg_varname = "stderr"
    flags = ["--stderr", "-e"]
    dest = "--stderr"
    metavar = "STDERR"
    help = "File to redirect stderr (%%x=jobname, %%j=jobid)"
    example = "--stderr ./%x.%j.err"
    type = str


class Disable_stdout_job_summary(Pragma):
    """
    Represents the SLURM #SBATCH --disable-stdout-job-summary pragma.
    Disables the job summary in the stdout file for the job.
    Usage: --disable-stdout-job-summary
    """

    pragma_id = 3
    pragma_type = "io_and_directory"
    arg_varname = "disable_stdout_job_summary"
    flags = ["--disable-stdout-job-summary"]
    dest = "--disable-stdout-job-summary"
    help = "disable job summary in stdout file for the job"
    action = "store_true"
    type = str


class Get_user_env(Pragma):
    """
    Represents the SLURM #SBATCH --get-user-env pragma.
    Used by Moab for environment setup; see srun man page for details.
    Usage: --get-user-env
    """

    pragma_id = 4
    pragma_type = "io_and_directory"
    arg_varname = "get_user_env"
    flags = ["--get-user-env"]
    dest = "--get-user-env"
    help = "used by Moab. See srun man page"
    action = "store_true"
    type = str


class Quiet(Pragma):
    """
    Represents the SLURM #SBATCH --quiet pragma.
    Suppresses informational messages during job submission.
    Usage: --quiet
    """

    pragma_id = 5
    pragma_type = "io_and_directory"
    arg_varname = "quiet"
    flags = ["-Q", "--quiet"]
    dest = "--quiet"
    help = "quiet mode (suppress informational messages)"
    action = "store_true"
    type = str


# --- 4. Notifications (notifications) ---
class Mail_user(Pragma):
    """
    Represents the SLURM #SBATCH --mail-user pragma.
    Specifies the email address to receive job state notifications.
    Usage: --mail-user <EMAIL>
    """

    pragma_id = 0
    pragma_type = "notifications"
    arg_varname = "mail_user"
    flags = ["--mail-user"]
    dest = "--mail-user"
    metavar = "USER"
    help = "who to send email notification for job state changes"
    example = "example@email.com"
    type = str


class Mail_type(Pragma):
    """
    Represents the SLURM #SBATCH --mail-type pragma.
    Sets which job state changes trigger email notifications (e.g., BEGIN, END, FAIL).
    Usage: --mail-type <TYPE>
    """

    pragma_id = 1
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
    """
    Represents the SLURM #SBATCH --bell pragma.
    Rings the terminal bell when the job is allocated.
    Usage: --bell
    """

    pragma_id = 2
    pragma_type = "notifications"
    arg_varname = "bell"
    flags = ["--bell"]
    dest = "--bell"
    help = "ring the terminal bell when the job is allocated"
    action = "store_true"
    type = str


# --- 5. Dependencies & Job Arrays (dependencies_and_arrays) ---
class Dependency(Pragma):
    """
    Represents the SLURM #SBATCH --dependency pragma.
    Defers job start until a condition on another job ID is satisfied (e.g., after, afterok).
    Usage: --dependency <TYPE:JOBID[:TIME]>
    """

    pragma_id = 0
    pragma_type = "dependencies_and_arrays"
    arg_varname = "dependency"
    flags = ["-d", "--dependency"]
    dest = "--dependency"
    metavar = "TYPE:JOBID[:TIME]"
    help = "defer job until condition on jobid is satisfied"
    type = str


class Array(Pragma):
    """
    Represents the SLURM #SBATCH --array pragma.
    Submits a job array, allowing multiple similar jobs to be managed together.
    Usage: --array <INDEXES>
    """

    pragma_id = 1
    pragma_type = "dependencies_and_arrays"
    arg_varname = "array"
    flags = ["--array"]
    dest = "--array"
    metavar = "INDEXES"
    help = "submit a job array"
    type = str


# --- 6. Core Node & Task Allocation (core_node_and_task_allocation) ---
class Nodes(Pragma):
    """
    Represents the SLURM #SBATCH --nodes pragma.
    Specifies the number of nodes to allocate for the job.
    Usage: --nodes <COUNT>
    """

    pragma_id = 0
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "nodes"
    flags = ["-N", "--nodes"]
    dest = "--nodes"
    metavar = "NODES"
    help = "number of nodes on which to run"
    example = "2"
    type = int


class Ntasks(Pragma):
    """
    Represents the SLURM #SBATCH --ntasks pragma.
    Sets the total number of tasks (processes) to run for the job.
    Usage: --ntasks <COUNT>
    """

    pragma_id = 1
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "ntasks"
    flags = ["-n", "--ntasks"]
    dest = "--ntasks"
    metavar = "N"
    help = "number of processors required"
    example = "16"
    type = str


class Ntasks_per_node(Pragma):
    """
    Represents the SLURM #SBATCH --ntasks-per-node pragma.
    Specifies the number of tasks to invoke on each node.
    Usage: --ntasks-per-node <COUNT>
    """

    pragma_id = 2
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "ntasks_per_node"
    flags = ["--ntasks-per-node"]
    dest = "--ntasks-per-node"
    metavar = "N"
    help = "number of tasks to invoke on each node"
    example = "16"
    type = int


class Cpus_per_task(Pragma):
    """
    Represents the SLURM #SBATCH --cpus-per-task pragma.
    Sets the number of CPUs required per task.
    Usage: --cpus-per-task <COUNT>
    """

    pragma_id = 3
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "cpus_per_task"
    flags = ["-c", "--cpus-per-task"]
    dest = "--cpus-per-task"
    metavar = "NCPUS"
    help = "number of cpus required per task"
    example = "16"
    type = str


class Mincpus(Pragma):
    """
    Represents the SLURM #SBATCH --mincpus pragma.
    Specifies the minimum number of logical processors per node.
    Usage: --mincpus <COUNT>
    """

    pragma_id = 4
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "mincpus"
    flags = ["--mincpus"]
    dest = "--mincpus"
    metavar = "N"
    help = "minimum number of logical processors per node"
    type = str


class Distribution(Pragma):
    """
    Represents the SLURM #SBATCH --distribution pragma.
    Sets the distribution method for processes across nodes (block, cyclic, arbitrary).
    Usage: --distribution <TYPE>
    """

    pragma_id = 5
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "distribution"
    flags = ["-m", "--distribution"]
    dest = "--distribution"
    metavar = "TYPE"
    help = "distribution method for processes to nodes"
    choices = ["block", "cyclic", "arbitrary"]
    type = str


class Spread_job(Pragma):
    """
    Represents the SLURM #SBATCH --spread-job pragma.
    Spreads the job across as many nodes as possible.
    Usage: --spread-job
    """

    pragma_id = 6
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "spread_job"
    flags = ["--spread-job"]
    dest = "--spread-job"
    help = "spread job across as many nodes as possible"
    action = "store_true"
    type = str


class Use_min_nodes(Pragma):
    """
    Represents the SLURM #SBATCH --use-min-nodes pragma.
    If a range of node counts is given, prefers the smaller count for allocation.
    Usage: --use-min-nodes
    """

    pragma_id = 7
    pragma_type = "core_node_and_task_allocation"
    arg_varname = "use_min_nodes"
    flags = ["--use-min-nodes"]
    dest = "--use-min-nodes"
    help = "if a range of node counts is given, prefer the smaller count"
    action = "store_true"
    type = str


# --- 7. CPU Topology & Binding (cpu_topology_and_binding) ---
class Sockets_per_node(Pragma):
    """
    Represents the SLURM #SBATCH --sockets-per-node pragma.
    Specifies the number of sockets per node to allocate.
    Usage: --sockets-per-node <COUNT>
    """

    pragma_id = 0
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "sockets_per_node"
    flags = ["--sockets-per-node"]
    dest = "--sockets-per-node"
    metavar = "S"
    help = "number of sockets per node to allocate"
    type = str


class Cores_per_socket(Pragma):
    """
    Represents the SLURM #SBATCH --cores-per-socket pragma.
    Sets the number of cores per socket to allocate.
    Usage: --cores-per-socket <COUNT>
    """

    pragma_id = 1
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "cores_per_socket"
    flags = ["--cores-per-socket"]
    dest = "--cores-per-socket"
    metavar = "C"
    help = "number of cores per socket to allocate"
    example = "8"
    type = str


class Threads_per_core(Pragma):
    """
    Represents the SLURM #SBATCH --threads-per-core pragma.
    Specifies the number of threads per core to allocate.
    Usage: --threads-per-core <COUNT>
    """

    pragma_id = 2
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "threads_per_core"
    flags = ["--threads-per-core"]
    dest = "--threads-per-core"
    metavar = "T"
    help = "number of threads per core to allocate"
    example = "4"
    type = str


class Ntasks_per_core(Pragma):
    """
    Represents the SLURM #SBATCH --ntasks-per-core pragma.
    Sets the number of tasks to invoke on each core.
    Usage: --ntasks-per-core <COUNT>
    """

    pragma_id = 3
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "ntasks_per_core"
    flags = ["--ntasks-per-core"]
    dest = "--ntasks-per-core"
    metavar = "N"
    help = "number of tasks to invoke on each core"
    example = "16"
    type = str


class Ntasks_per_socket(Pragma):
    """
    Represents the SLURM #SBATCH --ntasks-per-socket pragma.
    Specifies the number of tasks to invoke on each socket.
    Usage: --ntasks-per-socket <COUNT>
    """

    pragma_id = 4
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "ntasks_per_socket"
    flags = ["--ntasks-per-socket"]
    dest = "--ntasks-per-socket"
    metavar = "N"
    help = "number of tasks to invoke on each socket"
    example = "8"
    type = str


class Extra_node_info(Pragma):
    """
    Represents the SLURM #SBATCH --extra-node-info pragma.
    Combines requests for sockets, cores, and threads in a single specification.
    Usage: --extra-node-info <S[:C[:T]]>
    """

    pragma_id = 5
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "extra_node_info"
    flags = ["-B", "--extra-node-info"]
    dest = "--extra-node-info"
    metavar = "S[:C[:T]]"
    help = "combine request of sockets, cores and threads"
    type = str


class Hint(Pragma):
    """
    Represents the SLURM #SBATCH --hint pragma.
    Provides application binding hints to optimize task placement.
    Usage: --hint <HINT>
    """

    pragma_id = 6
    pragma_type = "cpu_topology_and_binding"
    arg_varname = "hint"
    flags = ["--hint"]
    dest = "--hint"
    metavar = "HINT"
    help = "Bind tasks according to application hints"
    type = str


# --- 8. Memory (memory) ---
class Mem(Pragma):
    """
    Represents the SLURM #SBATCH --mem pragma.
    Sets the minimum amount of real memory required for the job.
    Usage: --mem <SIZE>
    """

    pragma_id = 0
    pragma_type = "memory"
    arg_varname = "mem"
    flags = ["--mem"]
    dest = "--mem"
    metavar = "MB"
    help = "minimum amount of real memory"
    example = "25GB"
    type = str


class Mem_per_cpu(Pragma):
    """
    Represents the SLURM #SBATCH --mem-per-cpu pragma.
    Specifies the maximum amount of real memory per allocated CPU.
    Usage: --mem-per-cpu <SIZE>
    """

    pragma_id = 1
    pragma_type = "memory"
    arg_varname = "mem_per_cpu"
    flags = ["--mem-per-cpu"]
    dest = "--mem-per-cpu"
    metavar = "MB"
    help = "maximum amount of real memory per allocated cpu"
    type = str


class Mem_bind(Pragma):
    """
    Represents the SLURM #SBATCH --mem-bind pragma.
    Binds memory to locality domains for performance optimization.
    Usage: --mem-bind <BIND>
    """

    pragma_id = 2
    pragma_type = "memory"
    arg_varname = "mem_bind"
    flags = ["--mem-bind"]
    dest = "--mem-bind"
    metavar = "BIND"
    help = "Bind memory to locality domains"
    type = str


class Oom_kill_step(Pragma):
    """
    Represents the SLURM #SBATCH --oom-kill-step pragma.
    Sets the OOMKillStep behavior for jobs that exceed memory limits.
    Usage: --oom-kill-step <0|1>
    """

    pragma_id = 3
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
    """
    Represents the SLURM #SBATCH --gpus pragma.
    Specifies the number of GPUs required for the job.
    Usage: --gpus <COUNT>
    """

    pragma_id = 0
    pragma_type = "gpus"
    arg_varname = "gpus"
    flags = ["-G", "--gpus"]
    dest = "--gpus"
    metavar = "N"
    help = "count of GPUs required for the job"
    example = "32"
    type = str


class Gpus_per_node(Pragma):
    """
    Represents the SLURM #SBATCH --gpus-per-node pragma.
    Sets the number of GPUs required per allocated node.
    Usage: --gpus-per-node <COUNT>
    """

    pragma_id = 1
    pragma_type = "gpus"
    arg_varname = "gpus_per_node"
    flags = ["--gpus-per-node"]
    dest = "--gpus-per-node"
    metavar = "N"
    help = "number of GPUs required per allocated node"
    type = str


class Gpus_per_task(Pragma):
    """
    Represents the SLURM #SBATCH --gpus-per-task pragma.
    Specifies the number of GPUs required per spawned task.
    Usage: --gpus-per-task <COUNT>
    """

    pragma_id = 2
    pragma_type = "gpus"
    arg_varname = "gpus_per_task"
    flags = ["--gpus-per-task"]
    dest = "--gpus-per-task"
    metavar = "N"
    help = "number of GPUs required per spawned task"
    type = str


class Gpus_per_socket(Pragma):
    """
    Represents the SLURM #SBATCH --gpus-per-socket pragma.
    Sets the number of GPUs required per allocated socket.
    Usage: --gpus-per-socket <COUNT>
    """

    pragma_id = 3
    pragma_type = "gpus"
    arg_varname = "gpus_per_socket"
    flags = ["--gpus-per-socket"]
    dest = "--gpus-per-socket"
    metavar = "N"
    help = "number of GPUs required per allocated socket"
    type = str


class Cpus_per_gpu(Pragma):
    """
    Represents the SLURM #SBATCH --cpus-per-gpu pragma.
    Specifies the number of CPUs required per allocated GPU.
    Usage: --cpus-per-gpu <COUNT>
    """

    pragma_id = 4
    pragma_type = "gpus"
    arg_varname = "cpus_per_gpu"
    flags = ["--cpus-per-gpu"]
    dest = "--cpus-per-gpu"
    metavar = "N"
    help = "number of CPUs required per allocated GPU"
    example = "4"
    type = str


class Mem_per_gpu(Pragma):
    """
    Represents the SLURM #SBATCH --mem-per-gpu pragma.
    Sets the real memory required per allocated GPU.
    Usage: --mem-per-gpu <SIZE>
    """

    pragma_id = 5
    pragma_type = "gpus"
    arg_varname = "mem_per_gpu"
    flags = ["--mem-per-gpu"]
    dest = "--mem-per-gpu"
    help = "real memory required per allocated GPU"
    example = "8GB"
    type = str


class Gpu_bind(Pragma):
    """
    Represents the SLURM #SBATCH --gpu-bind pragma.
    Specifies task-to-GPU binding options for optimal placement.
    Usage: --gpu-bind <OPTIONS>
    """

    pragma_id = 6
    pragma_type = "gpus"
    arg_varname = "gpu_bind"
    flags = ["--gpu-bind"]
    dest = "--gpu-bind"
    metavar = "..."
    help = "task to gpu binding options"
    type = str


class Gpu_freq(Pragma):
    """
    Represents the SLURM #SBATCH --gpu-freq pragma.
    Sets the frequency and voltage of GPUs for the job.
    Usage: --gpu-freq <OPTIONS>
    """

    pragma_id = 7
    pragma_type = "gpus"
    arg_varname = "gpu_freq"
    flags = ["--gpu-freq"]
    dest = "--gpu-freq"
    metavar = "..."
    help = "frequency and voltage of GPUs"
    type = str


class Nvmps(Pragma):
    """
    Represents the SLURM #SBATCH --nvmps pragma.
    Launches NVIDIA MPS (Multi-Process Service) for the job.
    Usage: --nvmps
    """

    pragma_id = 8
    pragma_type = "gpus"
    arg_varname = "nvmps"
    flags = ["--nvmps"]
    dest = "--nvmps"
    help = "launching NVIDIA MPS for job"
    action = "store_true"
    type = str


# --- 10. Generic Resources & Licenses (generic_resources_and_licenses) ---
class Gres(Pragma):
    """
    Represents the SLURM #SBATCH --gres pragma.
    Specifies required generic resources (e.g., GPUs, licenses).
    Usage: --gres <LIST>
    """

    pragma_id = 0
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "gres"
    flags = ["--gres"]
    dest = "--gres"
    metavar = "LIST"
    help = "required generic resources"
    type = str


class Gres_flags(Pragma):
    """
    Represents the SLURM #SBATCH --gres-flags pragma.
    Sets flags related to GRES (Generic Resource) management.
    Usage: --gres-flags <OPTIONS>
    """

    pragma_id = 1
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "gres_flags"
    flags = ["--gres-flags"]
    dest = "--gres-flags"
    metavar = "OPTS"
    help = "flags related to GRES management"
    type = str


class Tres_bind(Pragma):
    """
    Represents the SLURM #SBATCH --tres-bind pragma.
    Specifies task-to-TRES binding options for resource allocation.
    Usage: --tres-bind <OPTIONS>
    """

    pragma_id = 2
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "tres_bind"
    flags = ["--tres-bind"]
    dest = "--tres-bind"
    metavar = "..."
    help = "task to tres binding options"
    type = str


class Tres_per_task(Pragma):
    """
    Represents the SLURM #SBATCH --tres-per-task pragma.
    Sets the list of TRES (Trackable Resources) required per task.
    Usage: --tres-per-task <LIST>
    """

    pragma_id = 3
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "tres_per_task"
    flags = ["--tres-per-task"]
    dest = "--tres-per-task"
    metavar = "LIST"
    help = "list of tres required per task"
    type = str


class Licenses(Pragma):
    """
    Represents the SLURM #SBATCH --licenses pragma.
    Specifies required licenses for the job, comma separated.
    Usage: --licenses <NAMES>
    """

    pragma_id = 4
    pragma_type = "generic_resources_and_licenses"
    arg_varname = "licenses"
    flags = ["-L", "--licenses"]
    dest = "--licenses"
    metavar = "NAMES"
    help = "required license, comma separated"
    type = str


# --- 11. Node Constraints & Selection (node_constraints_and_selection) ---
class Constraint(Pragma):
    """
    Represents the SLURM #SBATCH --constraint pragma.
    Specifies a list of constraints for node selection.
    Usage: --constraint <LIST>
    """

    pragma_id = 0
    pragma_type = "node_constraints_and_selection"
    arg_varname = "constraint"
    flags = ["-C", "--constraint"]
    dest = "--constraint"
    metavar = "LIST"
    help = "specify a list of constraints"
    type = str


class Cluster_constraint(Pragma):
    """
    Represents the SLURM #SBATCH --cluster-constraint pragma.
    Specifies a list of cluster constraints for node selection.
    Usage: --cluster-constraint <LIST>
    """

    pragma_id = 1
    pragma_type = "node_constraints_and_selection"
    arg_varname = "cluster_constraint"
    flags = ["--cluster-constraint"]
    dest = "--cluster-constraint"
    metavar = "LIST"
    help = "specify a list of cluster constraints"
    type = str


class Contiguous(Pragma):
    """
    Represents the SLURM #SBATCH --contiguous pragma.
    Demands a contiguous range of nodes for the job.
    Usage: --contiguous
    """

    pragma_id = 2
    pragma_type = "node_constraints_and_selection"
    arg_varname = "contiguous"
    flags = ["--contiguous"]
    dest = "--contiguous"
    help = "demand a contiguous range of nodes"
    action = "store_true"
    type = str


class Nodelist(Pragma):
    """
    Represents the SLURM #SBATCH --nodelist pragma.
    Requests a specific list of hosts for job execution.
    Usage: --nodelist <HOSTS>
    """

    pragma_id = 3
    pragma_type = "node_constraints_and_selection"
    arg_varname = "nodelist"
    flags = ["-w", "--nodelist"]
    dest = "--nodelist"
    metavar = "HOST"
    help = "request a specific list of hosts"
    nargs = "+"
    type = str


class Nodefile(Pragma):
    """
    Represents the SLURM #SBATCH --nodefile pragma.
    Requests a specific list of hosts from a file for job execution.
    Usage: --nodefile <FILENAME>
    """

    pragma_id = 4
    pragma_type = "node_constraints_and_selection"
    arg_varname = "nodefile"
    flags = ["-F", "--nodefile"]
    dest = "--nodefile"
    metavar = "FILENAME"
    help = "request a specific list of hosts"
    type = str


class Exclude(Pragma):
    """
    Represents the SLURM #SBATCH --exclude pragma.
    Excludes a specific list of hosts from job allocation.
    Usage: --exclude <HOSTS>
    """

    pragma_id = 5
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
    """
    Represents the SLURM #SBATCH --exclusive-user pragma.
    Allocates nodes in exclusive mode for CPU consumable resources.
    Usage: --exclusive-user
    """

    pragma_id = 0
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "exclusive_user"
    flags = ["--exclusive-user"]
    dest = "--exclusive-user"
    help = "allocate nodes in exclusive mode for cpu consumable resource"
    action = "store_true"
    type = str


class Exclusive_mcs(Pragma):
    """
    Represents the SLURM #SBATCH --exclusive-mcs pragma.
    Allocates nodes in exclusive mode when the mcs plugin is enabled.
    Usage: --exclusive-mcs
    """

    pragma_id = 1
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "exclusive_mcs"
    flags = ["--exclusive-mcs"]
    dest = "--exclusive-mcs"
    help = "allocate nodes in exclusive mode when mcs plugin is enabled"
    action = "store_true"
    type = str


class Oversubscribe(Pragma):
    """
    Represents the SLURM #SBATCH --oversubscribe pragma.
    Allows resources to be oversubscribed with other jobs.
    Usage: --oversubscribe
    """

    pragma_id = 2
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "oversubscribe"
    flags = ["-s", "--oversubscribe"]
    dest = "--oversubscribe"
    help = "oversubscribe resources with other jobs"
    action = "store_true"
    type = str


class Overcommit(Pragma):
    """
    Represents the SLURM #SBATCH --overcommit pragma.
    Allows resources to be overcommitted for the job.
    Usage: --overcommit
    """

    pragma_id = 3
    pragma_type = "exclusivity_and_sharing"
    arg_varname = "overcommit"
    flags = ["-O", "--overcommit"]
    dest = "--overcommit"
    help = "overcommit resources"
    action = "store_true"
    type = str


# --- 13. Execution Behavior & Signals (execution_behavior_and_signals) ---
class Hold(Pragma):
    """
    Represents the SLURM #SBATCH --hold pragma.
    Submits the job in a held state, preventing immediate execution.
    Usage: --hold
    """

    pragma_id = 0
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "hold"
    flags = ["-H", "--hold"]
    dest = "--hold"
    help = "submit job in held state"
    action = "store_true"
    type = str


class Immediate(Pragma):
    """
    Represents the SLURM #SBATCH --immediate pragma.
    Exits if resources are not available within the specified seconds.
    Usage: --immediate [SECS]
    """

    pragma_id = 1
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
    """
    Represents the SLURM #SBATCH --reboot pragma.
    Reboots compute nodes before starting the job.
    Usage: --reboot
    """

    pragma_id = 2
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "reboot"
    flags = ["--reboot"]
    dest = "--reboot"
    help = "reboot compute nodes before starting job"
    action = "store_true"
    type = str


class Delay_boot(Pragma):
    """
    Represents the SLURM #SBATCH --delay-boot pragma.
    Delays node boot for desired features before job execution.
    Usage: --delay-boot <MINS>
    """

    pragma_id = 3
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "delay_boot"
    flags = ["--delay-boot"]
    dest = "--delay_boot"
    metavar = "MINS"
    help = "delay boot for desired node features"
    type = str


class No_kill(Pragma):
    """
    Represents the SLURM #SBATCH --no-kill pragma.
    Prevents job termination on node failure.
    Usage: --no-kill
    """

    pragma_id = 4
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "no_kill"
    flags = ["-k", "--no-kill"]
    dest = "--no-kill"
    help = "do not kill job on node failure"
    action = "store_true"
    type = str


class Kill_command(Pragma):
    """
    Represents the SLURM #SBATCH --kill-command pragma.
    Specifies the signal to send when terminating the job.
    Usage: --kill-command [SIGNAL]
    """

    pragma_id = 5
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
    """
    Represents the SLURM #SBATCH --signal pragma.
    Sends a signal when the time limit is within the specified seconds.
    Usage: --signal [R:]NUM[@TIME]
    """

    pragma_id = 6
    pragma_type = "execution_behavior_and_signals"
    arg_varname = "signal"
    flags = ["--signal"]
    dest = "--signal"
    metavar = "[R:]NUM[@TIME]"
    help = "send signal when time limit within time seconds"
    type = str


# --- 14. Advanced / Hardware / Misc (advanced_hardware_misc) ---
class Core_spec(Pragma):
    """
    Represents the SLURM #SBATCH --core-spec pragma.
    Sets the count of reserved cores for the job.
    Usage: --core-spec <CORES>
    """

    pragma_id = 0
    pragma_type = "advanced_hardware_misc"
    arg_varname = "core_spec"
    flags = ["-S", "--core-spec"]
    dest = "--core-spec"
    metavar = "CORES"
    help = "count of reserved cores"
    type = str


class Thread_spec(Pragma):
    """
    Represents the SLURM #SBATCH --thread-spec pragma.
    Sets the count of reserved threads for the job.
    Usage: --thread-spec <THREADS>
    """

    pragma_id = 1
    pragma_type = "advanced_hardware_misc"
    arg_varname = "thread_spec"
    flags = ["--thread-spec"]
    dest = "--thread-spec"
    metavar = "THREADS"
    help = "count of reserved threads"
    type = str


class Cpu_freq(Pragma):
    """
    Represents the SLURM #SBATCH --cpu-freq pragma.
    Requests CPU frequency and governor settings for the job.
    Usage: --cpu-freq <MIN[-MAX[:GOV]]>
    """

    pragma_id = 2
    pragma_type = "advanced_hardware_misc"
    arg_varname = "cpu_freq"
    flags = ["--cpu-freq"]
    dest = "--cpu-freq"
    metavar = "MIN[-MAX[:GOV]]"
    help = "requested cpu frequency (and governor)"
    type = str


class Tmp(Pragma):
    """
    Represents the SLURM #SBATCH --tmp pragma.
    Sets the minimum amount of temporary disk required for the job.
    Usage: --tmp <SIZE>
    """

    pragma_id = 3
    pragma_type = "advanced_hardware_misc"
    arg_varname = "tmp"
    flags = ["--tmp"]
    dest = "--tmp"
    metavar = "MB"
    help = "minimum amount of temporary disk"
    type = str


class Resv_ports(Pragma):
    """
    Represents the SLURM #SBATCH --resv-ports pragma.
    Reserves communication ports for the job.
    Usage: --resv-ports
    """

    pragma_id = 4
    pragma_type = "advanced_hardware_misc"
    arg_varname = "resv_ports"
    flags = ["--resv-ports"]
    dest = "--resv-ports"
    help = "reserve communication ports"
    action = "store_true"
    type = str


class Switches(Pragma):
    """
    Represents the SLURM #SBATCH --switches pragma.
    Sets optimum switches and maximum wait time for optimum.
    Usage: --switches <MAX_SWITCHES[@MAX_TIME]>
    """

    pragma_id = 5
    pragma_type = "advanced_hardware_misc"
    arg_varname = "switches"
    flags = ["--switches"]
    dest = "--switches"
    metavar = "MAX_SWITCHES[@MAX_TIME]"
    help = "optimum switches and max time to wait for optimum"
    type = str


class Power(Pragma):
    """
    Represents the SLURM #SBATCH --power pragma.
    Sets power management options for the job.
    Usage: --power <FLAGS>
    """

    pragma_id = 6
    pragma_type = "advanced_hardware_misc"
    arg_varname = "power"
    flags = ["--power"]
    dest = "--power"
    metavar = "FLAGS"
    help = "power management options"
    type = str


class Profile(Pragma):
    """
    Represents the SLURM #SBATCH --profile pragma.
    Enables acct_gather_profile for detailed job data collection.
    Usage: --profile <VALUE>
    """

    pragma_id = 7
    pragma_type = "advanced_hardware_misc"
    arg_varname = "profile"
    flags = ["--profile"]
    dest = "--profile"
    metavar = "VALUE"
    help = "enable acct_gather_profile for detailed data"
    type = str


# --- 15. Plugins (Burst Buffer & Containers) ---
class Burst_buffer(Pragma):
    """
    Represents the SLURM #SBATCH --bb pragma.
    Specifies burst buffer specifications for the job.
    Usage: --bb <SPEC>
    """

    pragma_id = 0
    pragma_type = "plugins"
    arg_varname = "burst_buffer"
    flags = ["--bb"]
    dest = "--burst-buffer"
    metavar = "SPEC"
    help = "burst buffer specifications"
    type = str


class Bb_file(Pragma):
    """
    Represents the SLURM #SBATCH --bbf pragma.
    Specifies a burst buffer specification file for the job.
    Usage: --bbf <FILE_NAME>
    """

    pragma_id = 1
    pragma_type = "plugins"
    arg_varname = "bb_file"
    flags = ["--bbf"]
    dest = "--bb-file"
    metavar = "FILE_NAME"
    help = "burst buffer specification file"
    type = str


class Container(Pragma):
    """
    Represents the SLURM #SBATCH --container pragma.
    Specifies the path to an OCI container bundle for the job.
    Usage: --container <PATH>
    """

    pragma_id = 2
    pragma_type = "plugins"
    arg_varname = "container"
    flags = ["--container"]
    dest = "--container"
    metavar = "PATH"
    help = "Path to OCI container bundle"
    type = str


class Container_id(Pragma):
    """
    Represents the SLURM #SBATCH --container-id pragma.
    Specifies the OCI container ID for the job.
    Usage: --container-id <ID>
    """

    pragma_id = 3
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
