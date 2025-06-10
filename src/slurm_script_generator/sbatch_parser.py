#!/usr/bin/env python3
"""
Slurm Argument Parser
Generates a command-line parser for Slurm's salloc/sbatch options.
"""
import argparse


def add_slurm_options(parser):

    # Parallel run options
    parser.add_argument(
        "-A",
        "--account",
        dest="account",
        metavar="NAME",
        help="charge job to specified account",
    )
    parser.add_argument(
        "-b",
        "--begin",
        dest="begin",
        metavar="TIME",
        help="defer job until HH:MM MM/DD/YY",
    )
    parser.add_argument(
        "--bell",
        action="store_true",
        dest="bell",
        help="ring the terminal bell when the job is allocated",
    )
    parser.add_argument(
        "--no-bell",
        action="store_false",
        dest="bell",
        help="do NOT ring the terminal bell",
    )
    parser.add_argument(
        "--bb", dest="burst_buffer", metavar="SPEC", help="burst buffer specifications"
    )
    parser.add_argument(
        "--bbf",
        dest="bb_file",
        metavar="FILE_NAME",
        help="burst buffer specification file",
    )
    parser.add_argument(
        "-c",
        "--cpus-per-task",
        dest="cpus_per_task",
        type=int,
        metavar="NCPUS",
        help="number of cpus required per task",
    )
    parser.add_argument(
        "--comment", dest="comment", metavar="NAME", help="arbitrary comment"
    )
    parser.add_argument(
        "--container",
        dest="container",
        metavar="PATH",
        help="Path to OCI container bundle",
    )
    parser.add_argument(
        "--container-id", dest="container_id", metavar="ID", help="OCI container ID"
    )
    parser.add_argument(
        "--cpu-freq",
        dest="cpu_freq",
        metavar="MIN[-MAX[:GOV]]",
        help="requested cpu frequency (and governor)",
    )
    parser.add_argument(
        "--delay-boot",
        dest="delay_boot",
        type=int,
        metavar="MINS",
        help="delay boot for desired node features",
    )
    parser.add_argument(
        "-d",
        "--dependency",
        dest="dependency",
        metavar="TYPE:JOBID[:TIME]",
        help="defer job until condition on jobid is satisfied",
    )
    parser.add_argument(
        "--deadline",
        dest="deadline",
        metavar="TIME",
        help="remove the job if no ending possible before this deadline",
    )
    parser.add_argument(
        "-D", "--chdir", dest="chdir", metavar="PATH", help="change working directory"
    )
    parser.add_argument(
        "--get-user-env",
        action="store_true",
        dest="get_user_env",
        help="used by Moab. See srun man page",
    )
    parser.add_argument(
        "--gres",
        dest="gres",
        metavar="LIST",
        type=lambda s: s.split(","),
        help="required generic resources",
    )
    parser.add_argument(
        "--gres-flags",
        dest="gres_flags",
        metavar="OPTS",
        help="flags related to GRES management",
    )
    parser.add_argument(
        "-H",
        "--hold",
        action="store_true",
        dest="hold",
        help="submit job in held state",
    )
    parser.add_argument(
        "-I",
        "--immediate",
        nargs="?",
        const=0,
        dest="immediate",
        metavar="SECS",
        type=int,
        help='exit if resources not available in "secs"',
    )
    parser.add_argument(
        "-J", "--job-name", dest="job_name", metavar="NAME", help="name of job"
    )
    parser.add_argument(
        "-k",
        "--no-kill",
        action="store_true",
        dest="no_kill",
        help="do not kill job on node failure",
    )
    parser.add_argument(
        "-K",
        "--kill-command",
        nargs="?",
        const="TERM",
        dest="kill_command",
        metavar="SIGNAL",
        help="signal to send terminating job",
    )
    parser.add_argument(
        "-L",
        "--licenses",
        dest="licenses",
        metavar="NAMES",
        type=lambda s: s.split(","),
        help="required license, comma separated",
    )
    parser.add_argument(
        "-M",
        "--clusters",
        dest="clusters",
        metavar="NAMES",
        type=lambda s: s.split(","),
        help="Comma separated list of clusters to issue commands to",
    )
    parser.add_argument(
        "-m",
        "--distribution",
        dest="distribution",
        metavar="TYPE",
        choices=["block", "cyclic", "arbitrary"],
        help="distribution method for processes to nodes",
    )
    parser.add_argument(
        "--mail-type",
        dest="mail_type",
        metavar="TYPE",
        choices=["BEGIN", "END", "FAIL", "ALL"],
        help="notify on state change",
    )
    parser.add_argument(
        "--mail-user",
        dest="mail_user",
        metavar="USER",
        help="who to send email notification for job state changes",
    )
    parser.add_argument(
        "--mcs-label",
        dest="mcs_label",
        metavar="MCS",
        help="mcs label if mcs plugin mcs/group is used",
    )
    parser.add_argument(
        "-n",
        "--ntasks",
        dest="ntasks",
        type=int,
        metavar="N",
        help="number of processors required",
    )
    parser.add_argument(
        "--nice",
        nargs="?",
        const=0,
        dest="nice",
        type=int,
        metavar="VALUE",
        help="decrease scheduling priority by value",
    )
    parser.add_argument(
        "-N",
        "--nodes",
        dest="nodes",
        metavar="NODES",
        help="number of nodes on which to run",
    )
    parser.add_argument(
        "--ntasks-per-node",
        dest="ntasks_per_node",
        type=int,
        metavar="N",
        help="number of tasks to invoke on each node",
    )
    parser.add_argument(
        "--oom-kill-step",
        nargs="?",
        const=1,
        dest="oom_kill_step",
        type=int,
        metavar="0|1",
        help="set the OOMKillStep behaviour",
    )
    parser.add_argument(
        "-O",
        "--overcommit",
        action="store_true",
        dest="overcommit",
        help="overcommit resources",
    )
    parser.add_argument(
        "--power", dest="power", metavar="FLAGS", help="power management options"
    )
    parser.add_argument(
        "--priority",
        dest="priority",
        metavar="VALUE",
        type=int,
        help="set the priority of the job",
    )
    parser.add_argument(
        "--profile",
        dest="profile",
        metavar="VALUE",
        help="enable acct_gather_profile for detailed data",
    )
    parser.add_argument(
        "-p",
        "--partition",
        dest="partition",
        metavar="PARTITION",
        help="partition requested",
    )
    parser.add_argument(
        "-q", "--qos", dest="qos", metavar="QOS", help="quality of service"
    )
    parser.add_argument(
        "-Q",
        "--quiet",
        action="store_true",
        dest="quiet",
        help="quiet mode (suppress informational messages)",
    )
    parser.add_argument(
        "--reboot",
        action="store_true",
        dest="reboot",
        help="reboot compute nodes before starting job",
    )
    parser.add_argument(
        "-s",
        "--oversubscribe",
        action="store_true",
        dest="oversubscribe",
        help="oversubscribe resources with other jobs",
    )
    parser.add_argument(
        "--signal",
        dest="signal",
        metavar="[R:]NUM[@TIME]",
        help="send signal when time limit within time seconds",
    )
    parser.add_argument(
        "--spread-job",
        action="store_true",
        dest="spread_job",
        help="spread job across as many nodes as possible",
    )
    parser.add_argument(
        "--switches",
        dest="switches",
        metavar="MAX_SWITCHES[@MAX_TIME]",
        help="optimum switches and max time to wait for optimum",
    )
    parser.add_argument(
        "-S",
        "--core-spec",
        dest="core_spec",
        metavar="CORES",
        help="count of reserved cores",
    )
    parser.add_argument(
        "--thread-spec",
        dest="thread_spec",
        metavar="THREADS",
        help="count of reserved threads",
    )
    parser.add_argument(
        "-t", "--time", dest="time", metavar="MINUTES", type=int, help="time limit"
    )
    parser.add_argument(
        "--time-min",
        dest="time_min",
        metavar="MINUTES",
        type=int,
        help="minimum time limit (if distinct)",
    )
    parser.add_argument(
        "--tres-bind",
        dest="tres_bind",
        metavar="...",
        help="task to tres binding options",
    )
    parser.add_argument(
        "--tres-per-task",
        dest="tres_per_task",
        metavar="LIST",
        type=lambda s: s.split(","),
        help="list of tres required per task",
    )
    parser.add_argument(
        "--use-min-nodes",
        action="store_true",
        dest="use_min_nodes",
        help="if a range of node counts is given, prefer the smaller count",
    )
    # parser.add_argument(
    #     "-v",
    #     "--verbose",
    #     action="count",
    #     dest="verbose",
    #     default=0,
    #     help="verbose mode (multiple -v's increase verbosity)",
    # )
    parser.add_argument(
        "--wckey", dest="wckey", metavar="WCKEY", help="wckey to run job under"
    )

    # Constraint options
    parser.add_argument(
        "--cluster-constraint",
        dest="cluster_constraint",
        metavar="LIST",
        type=lambda s: s.split(","),
        help="specify a list of cluster constraints",
    )
    parser.add_argument(
        "--contiguous",
        action="store_true",
        dest="contiguous",
        help="demand a contiguous range of nodes",
    )
    parser.add_argument(
        "-C",
        "--constraint",
        dest="constraint",
        metavar="LIST",
        type=lambda s: s.split(","),
        help="specify a list of constraints",
    )
    parser.add_argument(
        "-F",
        "--nodefile",
        dest="nodefile",
        metavar="FILENAME",
        help="request a specific list of hosts",
    )
    parser.add_argument(
        "--mem",
        dest="mem",
        metavar="MB",
        type=int,
        help="minimum amount of real memory",
    )
    parser.add_argument(
        "--mincpus",
        dest="mincpus",
        metavar="N",
        type=int,
        help="minimum number of logical processors per node",
    )
    parser.add_argument(
        "--reservation",
        dest="reservation",
        metavar="NAME",
        help="allocate resources from named reservation",
    )
    parser.add_argument(
        "--tmp",
        dest="tmp",
        metavar="MB",
        type=int,
        help="minimum amount of temporary disk",
    )
    parser.add_argument(
        "-w",
        "--nodelist",
        dest="nodelist",
        nargs="+",
        metavar="HOST",
        help="request a specific list of hosts",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        dest="exclude",
        nargs="+",
        metavar="HOST",
        help="exclude a specific list of hosts",
    )

    # Consumable resources related options
    parser.add_argument(
        "--exclusive-user",
        action="store_true",
        dest="exclusive_user",
        help="allocate nodes in exclusive mode for cpu consumable resource",
    )
    parser.add_argument(
        "--exclusive-mcs",
        action="store_true",
        dest="exclusive_mcs",
        help="allocate nodes in exclusive mode when mcs plugin is enabled",
    )
    parser.add_argument(
        "--mem-per-cpu",
        dest="mem_per_cpu",
        metavar="MB",
        type=int,
        help="maximum amount of real memory per allocated cpu",
    )
    parser.add_argument(
        "--resv-ports",
        action="store_true",
        dest="resv_ports",
        help="reserve communication ports",
    )

    # Affinity/Multi-core options
    parser.add_argument(
        "--sockets-per-node",
        dest="sockets_per_node",
        metavar="S",
        type=int,
        help="number of sockets per node to allocate",
    )
    parser.add_argument(
        "--cores-per-socket",
        dest="cores_per_socket",
        metavar="C",
        type=int,
        help="number of cores per socket to allocate",
    )
    parser.add_argument(
        "--threads-per-core",
        dest="threads_per_core",
        metavar="T",
        type=int,
        help="number of threads per core to allocate",
    )
    parser.add_argument(
        "-B",
        "--extra-node-info",
        dest="extra_node_info",
        metavar="S[:C[:T]]",
        help="combine request of sockets, cores and threads",
    )
    parser.add_argument(
        "--ntasks-per-core",
        dest="ntasks_per_core",
        metavar="N",
        type=int,
        help="number of tasks to invoke on each core",
    )
    parser.add_argument(
        "--ntasks-per-socket",
        dest="ntasks_per_socket",
        metavar="N",
        type=int,
        help="number of tasks to invoke on each socket",
    )
    parser.add_argument(
        "--hint",
        dest="hint",
        metavar="HINT",
        help="Bind tasks according to application hints",
    )
    parser.add_argument(
        "--mem-bind",
        dest="mem_bind",
        metavar="BIND",
        help="Bind memory to locality domains",
    )

    # GPU scheduling options
    parser.add_argument(
        "--cpus-per-gpu",
        dest="cpus_per_gpu",
        metavar="N",
        type=int,
        help="number of CPUs required per allocated GPU",
    )
    parser.add_argument(
        "-G",
        "--gpus",
        dest="gpus",
        metavar="N",
        type=int,
        help="count of GPUs required for the job",
    )
    parser.add_argument(
        "--gpu-bind", dest="gpu_bind", metavar="...", help="task to gpu binding options"
    )
    parser.add_argument(
        "--gpu-freq",
        dest="gpu_freq",
        metavar="...",
        help="frequency and voltage of GPUs",
    )
    parser.add_argument(
        "--gpus-per-node",
        dest="gpus_per_node",
        metavar="N",
        type=int,
        help="number of GPUs required per allocated node",
    )
    parser.add_argument(
        "--gpus-per-socket",
        dest="gpus_per_socket",
        metavar="N",
        type=int,
        help="number of GPUs required per allocated socket",
    )
    parser.add_argument(
        "--gpus-per-task",
        dest="gpus_per_task",
        metavar="N",
        type=int,
        help="number of GPUs required per spawned task",
    )
    parser.add_argument(
        "--mem-per-gpu",
        dest="mem_per_gpu",
        type=str,
        help="real memory required per allocated GPU",
    )

    # Plugin options
    parser.add_argument(
        "--disable-stdout-job-summary",
        action="store_true",
        dest="disable_stdout_job_summary",
        help="disable job summary in stdout file for the job",
    )
    parser.add_argument(
        "--nvmps",
        action="store_true",
        dest="nvmps",
        help="launching NVIDIA MPS for job",
    )
