import json
import os
import subprocess
from importlib.metadata import version
from typing import Any, List

from slurm_script_generator.pragmas import Pragma, PragmaFactory, PragmaTypes
from slurm_script_generator.utils import add_line


class SlurmScript:
    """
    Class representing a Slurm batch script with pragmas, modules, and custom commands.

    Parameters
    ----------
    account : str, optional
        The account to charge for the job.
    array : str, optional
        The job array specification.
    begin : str, optional
        The time to begin the job.
    bell : str, optional
        Ring terminal bell when job is allocated.
    burst_buffer : str, optional
        Burst buffer specifications.
    bb_file : str, optional
        Burst buffer specification file.
    cpus_per_task : int, optional
        Number of CPUs required per task.
    comment : str, optional
        Arbitrary comment for the job.
    container : str, optional
        Path to OCI container bundle.
    container_id : str, optional
        OCI container ID.
    cpu_freq : str, optional
        Requested CPU frequency and governor.
    delay_boot : str, optional
        Delay boot for desired node features.
    dependency : str, optional
        Job dependency specification.
    deadline : str, optional
        Remove job if no ending possible before deadline.
    chdir : str, optional
        Change working directory for the job.
    get_user_env : str, optional
        Used by Moab for environment setup.
    gres : str, optional
        Required generic resources.
    gres_flags : str, optional
        Flags related to GRES management.
    hold : str, optional
        Submit job in held state.
    immediate : str, optional
        Exit if resources not available within seconds.
    job_name : str, optional
        Name of the job.
    no_kill : str, optional
        Do not kill job on node failure.
    kill_command : str, optional
        Signal to send terminating job.
    licenses : str, optional
        Required licenses, comma separated.
    clusters : str, optional
        Comma separated list of clusters.
    distribution : str, optional
        Distribution method for processes.
    mail_type : str, optional
        Notify on state change.
    mail_user : str, optional
        Email for job state changes.
    mcs_label : str, optional
        MCS label if mcs plugin is used.
    ntasks : str, optional
        Number of processors required.
    nice : str, optional
        Decrease scheduling priority by value.
    nodes : int, optional
        Number of nodes to allocate.
    ntasks_per_node : int, optional
        Number of tasks to invoke on each node.
    oom_kill_step : str, optional
        Set OOMKillStep behaviour.
    overcommit : str, optional
        Overcommit resources.
    power : str, optional
        Power management options.
    priority : str, optional
        Set job priority.
    profile : str, optional
        Enable acct_gather_profile for detailed data.
    partition : str, optional
        Partition requested.
    qos : str, optional
        Quality of service.
    quiet : str, optional
        Suppress informational messages.
    reboot : str, optional
        Reboot compute nodes before starting job.
    oversubscribe : str, optional
        Oversubscribe resources with other jobs.
    signal : str, optional
        Send signal when time limit within seconds.
    spread_job : str, optional
        Spread job across as many nodes as possible.
    stderr : str, optional
        Redirect stderr to file.
    stdout : str, optional
        Redirect stdout to file.
    switches : str, optional
        Optimum switches and max wait time.
    core_spec : str, optional
        Count of reserved cores.
    thread_spec : str, optional
        Count of reserved threads.
    time : str, optional
        Time limit for the job.
    time_min : str, optional
        Minimum time limit.
    tres_bind : str, optional
        Task to TRES binding options.
    tres_per_task : str, optional
        TRES required per task.
    use_min_nodes : str, optional
        Prefer smaller node count.
    wckey : str, optional
        Wckey to run job under.
    cluster_constraint : str, optional
        List of cluster constraints.
    contiguous : str, optional
        Demand contiguous range of nodes.
    constraint : str, optional
        List of constraints.
    nodefile : str, optional
        Request specific list of hosts from file.
    mem : str, optional
        Minimum real memory required.
    mincpus : str, optional
        Minimum logical processors per node.
    reservation : str, optional
        Allocate resources from named reservation.
    tmp : str, optional
        Minimum temporary disk required.
    nodelist : str, optional
        Request specific list of hosts.
    exclude : str, optional
        Exclude specific list of hosts.
    exclusive_user : str, optional
        Allocate nodes in exclusive mode.
    exclusive_mcs : str, optional
        Exclusive mode when mcs plugin enabled.
    mem_per_cpu : str, optional
        Real memory per allocated CPU.
    resv_ports : str, optional
        Reserve communication ports.
    sockets_per_node : int, optional
        Number of sockets per node to allocate.
    cores_per_socket : int, optional
        Number of cores per socket to allocate.
    threads_per_core : int, optional
        Number of threads per core to allocate.
    extra_node_info : str, optional
        Combine sockets, cores, threads.
    ntasks_per_core : int, optional
        Number of tasks per core.
    ntasks_per_socket : int, optional
        Number of tasks per socket.
    hint : str, optional
        Application binding hints.
    mem_bind : str, optional
        Bind memory to locality domains.
    cpus_per_gpu : int, optional
        Number of CPUs required per allocated GPU.
    gpus : str, optional
        Count of GPUs required.
    gpu_bind : str, optional
        Task to GPU binding options.
    gpu_freq : str, optional
        Frequency and voltage of GPUs.
    gpus_per_node : str, optional
        GPUs per allocated node.
    gpus_per_socket : str, optional
        GPUs per allocated socket.
    gpus_per_task : str, optional
        GPUs per spawned task.
    mem_per_gpu : str, optional
        Real memory per allocated GPU.
    disable_stdout_job_summary : str, optional
        Disable job summary in stdout file.
    nvmps : str, optional
        Launch NVIDIA MPS for job.
    pragmas : List[Pragma], optional
        List of pragmas to add to the script.
    modules : List[str], optional
        List of modules to load in the script.
    custom_command : str, optional
        Custom command to run in the script.
    custom_commands : list, optional
        List of custom commands to run in the script.
    inlined_script : str, optional
        Inline script to include in the batch script.
    inlined_scripts : list, optional
        List of inline scripts to include in the batch script.
    line_length : int, optional
        Line length for formatting output.
    """

    def __init__(
        self,
        account: str | None = None,
        array: str | None = None,
        begin: str | None = None,
        bell: str | None = None,
        burst_buffer: str | None = None,
        bb_file: str | None = None,
        cpus_per_task: int | None = None,
        comment: str | None = None,
        container: str | None = None,
        container_id: str | None = None,
        cpu_freq: str | None = None,
        delay_boot: str | None = None,
        dependency: str | None = None,
        deadline: str | None = None,
        chdir: str | None = None,
        get_user_env: str | None = None,
        gres: str | None = None,
        gres_flags: str | None = None,
        hold: str | None = None,
        immediate: str | None = None,
        job_name: str | None = None,
        no_kill: str | None = None,
        kill_command: str | None = None,
        licenses: str | None = None,
        clusters: str | None = None,
        distribution: str | None = None,
        mail_type: str | None = None,
        mail_user: str | None = None,
        mcs_label: str | None = None,
        ntasks: str | None = None,
        nice: int | None = None,
        nodes: int | None = None,
        ntasks_per_node: int | None = None,
        oom_kill_step: str | None = None,
        overcommit: str | None = None,
        power: str | None = None,
        priority: str | None = None,
        profile: str | None = None,
        partition: str | None = None,
        qos: str | None = None,
        quiet: str | None = None,
        reboot: str | None = None,
        oversubscribe: str | None = None,
        signal: str | None = None,
        spread_job: str | None = None,
        stderr: str | None = None,
        stdout: str | None = None,
        switches: str | None = None,
        core_spec: str | None = None,
        thread_spec: str | None = None,
        time: str | None = None,
        time_min: str | None = None,
        tres_bind: str | None = None,
        tres_per_task: str | None = None,
        use_min_nodes: str | None = None,
        wckey: str | None = None,
        cluster_constraint: str | None = None,
        contiguous: str | None = None,
        constraint: str | None = None,
        nodefile: str | None = None,
        mem: str | None = None,
        mincpus: str | None = None,
        reservation: str | None = None,
        tmp: str | None = None,
        nodelist: str | None = None,
        exclude: str | None = None,
        exclusive_user: str | None = None,
        exclusive_mcs: str | None = None,
        mem_per_cpu: str | None = None,
        resv_ports: str | None = None,
        sockets_per_node: int | None = None,
        cores_per_socket: int | None = None,
        threads_per_core: int | None = None,
        extra_node_info: str | None = None,
        ntasks_per_core: int | None = None,
        ntasks_per_socket: int | None = None,
        hint: str | None = None,
        mem_bind: str | None = None,
        cpus_per_gpu: int | None = None,
        gpus: str | None = None,
        gpu_bind: str | None = None,
        gpu_freq: str | None = None,
        gpus_per_node: str | None = None,
        gpus_per_socket: str | None = None,
        gpus_per_task: str | None = None,
        mem_per_gpu: str | None = None,
        disable_stdout_job_summary: str | None = None,
        nvmps: str | None = None,
        # List of pragmas to add to the script
        pragmas: List[Pragma] | None = None,
        # Non-pragma parameters
        modules: List[str] | None = None,
        custom_command: str | None = None,
        custom_commands: list | None = None,
        inlined_script: str | None = None,
        inlined_scripts: list | None = None,
        line_length: int = 54,
    ) -> None:

        # Set default values for non-pragma parameters
        self._modules = []
        self._custom_commands = []
        self._line_length = line_length
        self._pragma_dict = {
            "job_config": [],
            "time_and_priority": [],
            "io_and_directory": [],
            "notifications": [],
            "dependencies_and_arrays": [],
            "core_node_and_task_allocation": [],
            "cpu_topology_and_binding": [],
            "memory": [],
            "gpus": [],
            "generic_resources_and_licenses": [],
            "node_constraints_and_selection": [],
            "exclusivity_and_sharing": [],
            "execution_behavior_and_signals": [],
            "advanced_hardware_misc": [],
            "plugins": [],
        }

        # Pragma dict for creating pragmas from individual parameters
        pragma_params = {
            "account": account,
            "array": array,
            "begin": begin,
            "bell": bell,
            "burst_buffer": burst_buffer,
            "bb_file": bb_file,
            "cpus_per_task": cpus_per_task,
            "comment": comment,
            "container": container,
            "container_id": container_id,
            "cpu_freq": cpu_freq,
            "delay_boot": delay_boot,
            "dependency": dependency,
            "deadline": deadline,
            "chdir": chdir,
            "get_user_env": get_user_env,
            "gres": gres,
            "gres_flags": gres_flags,
            "hold": hold,
            "immediate": immediate,
            "job_name": job_name,
            "no_kill": no_kill,
            "kill_command": kill_command,
            "licenses": licenses,
            "clusters": clusters,
            "distribution": distribution,
            "mail_type": mail_type,
            "mail_user": mail_user,
            "mcs_label": mcs_label,
            "ntasks": ntasks,
            "nice": nice,
            "nodes": nodes,
            "ntasks_per_node": ntasks_per_node,
            "oom_kill_step": oom_kill_step,
            "overcommit": overcommit,
            "power": power,
            "priority": priority,
            "profile": profile,
            "partition": partition,
            "qos": qos,
            "quiet": quiet,
            "reboot": reboot,
            "oversubscribe": oversubscribe,
            "signal": signal,
            "spread_job": spread_job,
            "stderr": stderr,
            "stdout": stdout,
            "switches": switches,
            "core_spec": core_spec,
            "thread_spec": thread_spec,
            "time": time,
            "time_min": time_min,
            "tres_bind": tres_bind,
            "tres_per_task": tres_per_task,
            "use_min_nodes": use_min_nodes,
            "wckey": wckey,
            "cluster_constraint": cluster_constraint,
            "contiguous": contiguous,
            "constraint": constraint,
            "nodefile": nodefile,
            "mem": mem,
            "mincpus": mincpus,
            "reservation": reservation,
            "tmp": tmp,
            "nodelist": nodelist,
            "exclude": exclude,
            "exclusive_user": exclusive_user,
            "exclusive_mcs": exclusive_mcs,
            "mem_per_cpu": mem_per_cpu,
            "resv_ports": resv_ports,
            "sockets_per_node": sockets_per_node,
            "cores_per_socket": cores_per_socket,
            "threads_per_core": threads_per_core,
            "extra_node_info": extra_node_info,
            "ntasks_per_core": ntasks_per_core,
            "ntasks_per_socket": ntasks_per_socket,
            "hint": hint,
            "mem_bind": mem_bind,
            "cpus_per_gpu": cpus_per_gpu,
            "gpus": gpus,
            "gpu_bind": gpu_bind,
            "gpu_freq": gpu_freq,
            "gpus_per_node": gpus_per_node,
            "gpus_per_socket": gpus_per_socket,
            "gpus_per_task": gpus_per_task,
            "mem_per_gpu": mem_per_gpu,
            "disable_stdout_job_summary": disable_stdout_job_summary,
            "nvmps": nvmps,
        }

        # Add pragmas from list
        self.add_pragmas(pragmas=pragmas)

        # Add pragmas from individual parameters
        for name, param in pragma_params.items():
            if param is not None:
                pragma = PragmaFactory.create_pragma(name, param)
                self.add_pragma(pragma=pragma)

        # Handle modules
        self.add_modules(modules=modules)

        # Handle custom commands
        self.add_custom_command(command=custom_command)
        self.add_custom_commands(commands=custom_commands)

        # Handle inlined scripts
        self.add_inlined_script(path=inlined_script)
        self.add_inlined_scripts(paths=inlined_scripts)

    def add_custom_command(self, command: str) -> None:
        """
        Add a single custom command to the script.

        Parameters
        ----------
        command : str
            The custom command to add.

        Returns
        -------
        None
        """
        if command is None:
            return
        assert isinstance(command, str)
        self._custom_commands.append(command)

    def add_custom_commands(self, commands: List[str] | None) -> None:
        """
        Add multiple custom commands to the script.

        Parameters
        ----------
        commands : list of str, optional
            List of custom commands to add.

        Returns
        -------
        None
        """
        if commands is None:
            return
        assert isinstance(commands, list)
        for command in commands:
            self.add_custom_command(command=command)

    # Modules
    def add_module(self, module: str) -> None:
        """
        Add a single module to the script.

        Parameters
        ----------
        module : str
            The module to add.

        Returns
        -------
        None
        """
        if module is None:
            return
        assert isinstance(module, str)
        if module not in self._modules:
            self._modules.append(module)

    def add_modules(self, modules: List[str] | None) -> None:
        """
        Add multiple modules to the script.

        Parameters
        ----------
        modules : list of str, optional
            List of modules to add.

        Returns
        -------
        None
        """
        if modules is None:
            return
        assert isinstance(modules, list)
        for module in modules:
            self.add_module(module)

    # Inlined scripts
    def add_inlined_script(self, path: str) -> None:
        """
        Add lines from an inlined script file to the custom commands.

        Parameters
        ----------
        path : str
            Path to the script file to inline.

        Returns
        -------
        None
        """
        if path is None:
            return
        assert isinstance(path, str)
        assert os.path.isfile(
            path
        ), f"Inlined script '{path}' does not exist or is not a file."
        with open(path, "r") as f:
            for line in f.readlines():
                self._custom_commands.append(line.strip())

    def add_inlined_scripts(self, paths: List[str] | None) -> None:
        """
        Add lines from multiple inlined script files to the custom commands.

        Parameters
        ----------
        paths : list of str, optional
            List of script file paths to inline.

        Returns
        -------
        None
        """
        if paths is None:
            return
        assert isinstance(paths, list)
        for path in paths:
            self.add_inlined_script(path)

    # Pragmas
    def add_pragma(self, pragma: Pragma) -> None:
        """
        Add a Pragma object to the script, replacing any existing pragma with the same destination.

        Parameters
        ----------
        pragma : Pragma
            The Pragma object to add.

        Returns
        -------
        None
        """
        assert isinstance(pragma, Pragma)
        pragma_type: PragmaTypes = pragma.pragma_type
        # Check if pragma with same dest already exists and replace it
        for i, existing_pragma in enumerate(self._pragma_dict[pragma_type]):
            if existing_pragma.dest == pragma.dest:
                self._pragma_dict[pragma_type][i] = pragma
                return
        self._pragma_dict[pragma_type].append(pragma)

    def add_pragmas(self, pragmas: List[Pragma] | None) -> None:
        """
        Add multiple Pragma objects to the script.

        Parameters
        ----------
        pragmas : list of Pragma, optional
            List of Pragma objects to add.

        Returns
        -------
        None
        """
        if pragmas is None:
            return
        assert isinstance(pragmas, list)
        for pragma in pragmas:
            self.add_pragma(pragma=pragma)

    def add_param(self, key: str, value: Any) -> None:
        """
        Add a non-pragma parameter to the script.

        Parameters
        ----------
        key : str
            The parameter key.
        value : Any
            The parameter value.

        Returns
        -------
        None
        """
        assert not isinstance(key, Pragma), "Use add_pragma() to add Pragma instances"

        if key == "line_length":
            self._line_length = value
        elif key == "modules":
            self._modules = value
        elif key == "custom_commands":
            self._custom_commands = value
        elif key == "inline_script":
            self.add_inlined_script(value)
        elif key == "inlined_scripts":
            self.add_inlined_scripts(value)
        else:
            raise ValueError(f"Unknown parameter key: {key}")

    def generate_script(
        self, line_length: int = 54, include_header: bool = False
    ) -> str:
        script_str = "#!/bin/bash\n"

        # Add header
        SLURM_SCRIPT_HEADER = f"""########################################################
#            This script was generated using           #
#             slurm-script-generator v{version("slurm-script-generator")}            #
# https://github.com/max-models/slurm-script-generator #
#      `pip install slurm-script-generator=={version("slurm-script-generator")}`     #
########################################################\n
"""
        if include_header:
            script_str += SLURM_SCRIPT_HEADER

        # Add sbatch pragmas
        line_separator = "#" * (line_length + 2) + "\n"
        script_str += add_line(line_separator)

        # Loop over pragmas (ordered by pragma_id)
        itype = 0
        for pragma_type in self._pragma_dict:
            pragmas = self._pragma_dict[pragma_type]
            if len(pragmas) > 0:
                if itype > 0:
                    script_str += add_line("#", "", line_length=line_length)
                script_str += add_line(
                    f"# Pragmas for {pragma_type.replace('_', ' ').title()}",
                    comment="",
                    line_length=line_length,
                )
                for pragma in sorted(pragmas, key=lambda p: p.pragma_id):
                    script_str += f"{pragma}"
                itype += 1
        script_str += add_line(line_separator)

        # Load modules
        if len(self.modules) > 0:
            script_str += add_line(
                "module purge",
                "Purge modules",
                line_length=line_length,
            )
            script_str += add_line(
                f"module load {' '.join(self.modules)}",
                "modules",
                line_length=line_length,
            )
            script_str += add_line(
                "module list",
                "List loaded modules",
                line_length=line_length,
            )

        if len(self.custom_commands) > 0:
            for custom_command in self.custom_commands:
                script_str += add_line(
                    f"{custom_command}\n",
                    line_length=line_length,
                )

        return script_str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the SlurmScript instance to a dictionary representation.
        Returns:
            dict[str, Any]: Dictionary with keys 'pragmas', 'modules', and 'custom_commands'.
        """
        return {
            "pragmas": {pragma.arg_varname: pragma.value for pragma in self.pragmas},
            "modules": self.modules,
            "custom_commands": self.custom_commands,
        }

    def save(self, path: str, include_header: bool = True) -> None:
        """
        Save the generated SLURM script to a file.
        Args:
            path (str): Path to save the script file.
            include_header (bool): Whether to include the script header.
        """
        with open(path, "w") as f:
            f.write(
                self.generate_script(
                    line_length=self.line_length,
                    include_header=include_header,
                ),
            )

    def submit_job(self, path: str) -> None:
        """
        Submit the SLURM script as a job using sbatch.
        Args:
            path (str): Path to the script file to submit.
        Raises:
            RuntimeError: If sbatch fails to submit the job.
        """
        self.save(path)
        result = subprocess.run(["sbatch", path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"sbatch failed: {result.stderr.strip()}")
        print(result.stdout.strip())

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SlurmScript":
        """
        Create a SlurmScript instance from a dictionary.
        Args:
            data (dict[str, Any]): Dictionary with keys 'pragmas', 'modules', and 'custom_commands'.
        Returns:
            SlurmScript: The constructed SlurmScript object.
        """
        script = SlurmScript()
        # for pragma in data.get("pragmas", []):
        #     print(f"Creating pragma from dict: {pragma}")
        for key, value in data.get("pragmas", {}).items():
            pragma = PragmaFactory.create_pragma(key=key, value=value)
            script.add_pragma(pragma=pragma)
        script._modules = data.get("modules", [])
        script._custom_commands = data.get("custom_commands", [])
        return script

    @staticmethod
    def read_script(path: str, verbose: bool = False) -> "SlurmScript":
        """
        Read a SLURM script from a file and parse it into a SlurmScript instance.
        Args:
            path (str): Path to the script file.
            verbose (bool): If True, print parsing details.
        Returns:
            SlurmScript: The parsed SlurmScript object.
        """
        with open(path, "r") as f:
            script_str = f.read()
        return SlurmScript.from_script(script_str, verbose=verbose)

    @staticmethod
    def from_script(script: str, verbose: bool = False) -> "SlurmScript":
        """
        Parse a SLURM script string and create a SlurmScript instance.
        Args:
            script (str): SLURM script content.
            verbose (bool): If True, print parsing details.
        Returns:
            SlurmScript: The constructed SlurmScript object.
        """
        lines = script.splitlines()
        pragmas = []
        modules = []
        custom_commands = []
        for line in lines:
            if verbose:
                print(f"Processing line: '{line}'")
            line = line.strip()

            if line.startswith("#SBATCH"):
                if verbose:
                    print(f"Found SBATCH pragma line: '{line}'")
                pragma_line = line[len("#SBATCH") :].strip()
                if verbose:
                    print(f"Extracted pragma line: '{pragma_line}'")

                # Split on = or whitespace
                if "=" in pragma_line:
                    key, value = pragma_line.split("=", 1)
                else:
                    key, value = pragma_line.split(None, 1)
                if verbose:
                    print(f"Extracted key='{key}', value='{value}'")
                flag = key.strip().split()[0]
                # key = key.strip().lstrip("-").replace("-", "_")
                value = value.strip()
                # Extract comment if present
                if "#" in value:
                    value, comment = value.split("#", 1)
                    value = value.strip()
                    comment = comment.strip()
                else:
                    comment = None
                if verbose:
                    print(f"Parsing pragma: {flag = }, {value = }")
                pragmas.append(PragmaFactory.flag_to_pragma(flag, value))
            elif line.startswith("#") or line == "":
                continue
            elif line.startswith("module load"):
                modules.extend(line[len("module load") :].strip().split())
            elif line.startswith("module purge") or line.startswith("module list"):
                continue
            else:
                custom_commands.append(line)
        return SlurmScript(
            pragmas=pragmas, modules=modules, custom_commands=custom_commands
        )

    def to_json(self, path: str) -> None:
        """
        Save the SlurmScript instance as a JSON file.
        Args:
            path (str): Path to save the JSON file.
        """
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def from_json(path: str) -> "SlurmScript":
        """
        Load a SlurmScript instance from a JSON file.
        Args:
            path (str): Path to the JSON file.
        Returns:
            SlurmScript: The constructed SlurmScript object.
        """
        with open(path, "r") as f:
            data = json.load(f)
        return SlurmScript.from_dict(data)

    def __eq__(self, value: object) -> bool:
        """
        Compare two SlurmScript instances for equality.
        Args:
            value (object): The object to compare.
        Returns:
            bool: True if equal, False otherwise.
        """
        if not isinstance(value, SlurmScript):
            return False
        return self.to_dict() == value.to_dict()

    def to_string(self, include_header: bool = True) -> str:
        """
        Generate the SLURM script as a string.
        Args:
            include_header (bool): Whether to include the script header.
        Returns:
            str: The generated script string.
        """
        return self.generate_script(include_header=include_header)

    def __str__(self) -> str:
        """
        Return the string representation of the SLurmScript instance.
        Returns:
            str: The generated script string with header.
        """
        return self.to_string(include_header=True)

    def __repr__(self) -> str:
        """
        Return the official string representation of the SlurmScript instance.
        Returns:
            str: The formatted representation of the SlurmScript object.
        """
        script_repr = "SlurmScript(\n"
        for pragma in self.pragmas:
            script_repr += f"    {pragma.arg_varname}={repr(pragma.value)},\n"
        if len(self.modules) > 0:
            script_repr += f"    modules={repr(self.modules)},\n"
        if len(self.custom_commands) > 0:
            script_repr += f"    custom_commands={repr(self.custom_commands)},\n"
        script_repr += ")"
        return script_repr

    @property
    def line_length(self) -> int:
        """
        Get the maximum line length for the script.
        Returns:
            int: The line length value.
        """
        return self._line_length

    @property
    def pragmas(self) -> List[Pragma]:
        """
        Get the list of Pragma objects in the script.
        Returns:
            List[Pragma]: List of all Pragma instances.
        """
        pragma_list = []
        for pragma_type in self._pragma_dict:
            pragma_list.extend(self._pragma_dict[pragma_type])
        return pragma_list

    @property
    def modules(self) -> List[str]:
        """
        Get the list of modules to load in the script.
        Returns:
            List[str]: List of module names.
        """
        return self._modules

    @property
    def custom_commands(self) -> List[str]:
        """
        Get the list of custom commands to run in the script.
        Returns:
            List[str]: List of custom command strings.
        """
        return self._custom_commands

    # @property
    # def inlined_scripts(self) -> list:
    #     return self._inlined_scripts


if __name__ == "__main__":
    import slurm_script_generator.pragmas as pragmas

    pragma = pragmas.Account("max")
    nodes = pragmas.Nodes(1)
    script = SlurmScript(
        account="max",
        nodes=1,
        modules=["gcc/12", "openmpi/4.1"],
        custom_commands=[
            "source ~/virtual_envs/env_slurm/bin/activate",
            "mpirun -n 4 ./bin > run.out",
        ],
    )

    slurm_dict = script.to_dict()
    print(slurm_dict)

    script2 = SlurmScript.from_dict(slurm_dict)
    script2.to_json("script2.json")
