import os
from typing import List, Any
import json
from slurm_script_generator.pragmas import Pragma, PragmaFactory
from slurm_script_generator.utils import add_line


class SlurmScript:
    def __init__(
        self,
        account: str | None = None,
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
        nice: str | None = None,
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
        pragmas: List[Pragma] | None = None,
        printself: bool = False,
        modules: List[str] | None = None,
        venv: str | None = None,
        printenv: bool = False,
        likwid: bool = False,
        custom_command: str | None = None,
        custom_commands: list | None = None,
        inlined_script: str | None = None,
        inlined_scripts: list | None = None,
        vars: list | None = None,
        line_length: int = 40,
    ) -> None:

        if pragmas is None:
            pragmas = []
        self._pragmas = pragmas

        pragma_params = {
            "account": account,
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

        for name, param in pragma_params.items():
            if param is not None:
                pragma = PragmaFactory.create_pragma(name, param)
                self.add_pragma(pragma=pragma)
        self._printself = printself
        if modules is None:
            self._modules = []
        else:
            self._modules = modules
        self._venv = venv
        self._printenv = printenv
        self._likwid = likwid

        # Handle custom commands
        if custom_commands is None:
            custom_commands: list = []
        assert isinstance(custom_commands, list)
        if custom_command is not None:
            custom_commands.append(custom_command)
        self._custom_commands = custom_commands

        # Handle inlined scripts
        if inlined_scripts is None:
            inlined_scripts = []
        assert isinstance(inlined_scripts, list)
        if inlined_script is not None:
            inlined_scripts.append(inlined_script)

        for inlined_script in inlined_scripts:
            assert isinstance(inlined_script, str)
            assert os.path.isfile(
                inlined_script
            ), f"Inlined script '{inlined_script}' does not exist or is not a file."
            with open(inlined_script, "r") as f:
                for line in f.readlines():
                    self._custom_commands.append(line.strip())

        # Handle environment variables
        if vars is None:
            self._vars = []
        else:
            self._vars = vars
        self._line_length = line_length

    def add_pragma(self, pragma: Pragma) -> None:
        assert isinstance(pragma, Pragma)
        self._pragmas.append(pragma)

    def generate_script(self, line_length: int = 40) -> str:
        script_repr = "#!/bin/bash\n"
        script_repr += "#" * (line_length + 2) + "\n"
        for pragma in self.pragmas:
            script_repr += f"{pragma}"
        script_repr += "#" * (line_length + 2) + "\n"

        if self.printself:
            script_repr += add_line(
                f"cat $0",
                "print this batch script",
                line_length=line_length,
            )

        for var in self.vars:
            script_repr += add_line(
                f"export {var}",
                "Export environment variable",
                line_length=line_length,
            )

        # Load modules
        if len(self.modules) > 0:
            script_repr += add_line(
                "module purge",
                "Purge modules",
                line_length=line_length,
            )
            script_repr += add_line(
                f"module load {' '.join(self.modules)}",
                "modules",
                line_length=line_length,
            )
            script_repr += add_line(
                "module list",
                "List loaded modules",
                line_length=line_length,
            )

        if self.venv is not None:
            script_repr += add_line(
                f"source {self.venv}/bin/activate",
                "virtual environment",
                line_length=line_length,
            )

        if self.printenv:
            script_repr += add_line(
                "printenv",
                "print environment variables",
                line_length=line_length,
            )

        if self.likwid:
            script_repr += add_line(
                "LIKWID_PREFIX=$(realpath $(dirname $(which likwid-topology))/..)",
                "Set LIKWID prefix",
                line_length=line_length,
            )

            script_repr += add_line(
                "export LD_LIBRARY_PATH=$LIKWID_PREFIX/lib",
                "Set LD_LIBRARY_PATH for LIKWID",
                line_length=line_length,
            )

            script_repr += add_line(
                "likwid-topology > likwid-topology.txt",
                "Save LIKWID topology information",
                line_length=line_length,
            )
            script_repr += add_line(
                "likwid-topology -g > likwid-topology-g.txt",
                "Save graphical LIKWID topology information",
                line_length=line_length,
            )

            script_repr += "\n"

        if len(self.custom_commands) > 0:
            for custom_command in self.custom_commands:
                script_repr += add_line(
                    f"{custom_command}\n",
                    line_length=line_length,
                )

        return script_repr

    def to_dict(self) -> dict[str, Any]:
        return {
            "pragmas": [pragma.to_dict() for pragma in self.pragmas],
            "printself": self.printself,
            "modules": self.modules,
            "venv": self.venv,
            "printenv": self.printenv,
            "likwid": self.likwid,
            "custom_commands": self.custom_commands,
            "vars": self.vars,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SlurmScript":
        script = SlurmScript()
        for pragma in data.get("pragmas", []):
            print(f"Creating pragma from dict: {pragma}")
        script._pragmas = [
            PragmaFactory.create_pragma(
                key=list(pragma.keys())[0], value=list(pragma.values())[0]
            )
            for pragma in data.get("pragmas", [])
        ]
        script._printself = data.get("printself", False)
        script._modules = data.get("modules", [])
        script._venv = data.get("venv", None)
        script._printenv = data.get("printenv", False)
        script._likwid = data.get("likwid", False)
        script._custom_commands = data.get("custom_commands", [])
        script._vars = data.get("vars", [])
        return script

    def to_json(self, path: str) -> str:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
    
    @staticmethod
    def from_json(path: str) -> "SlurmScript":
        with open(path, "r") as f:
            data = json.load(f)
        return SlurmScript.from_dict(data)

    def __str__(self) -> str:
        return self.generate_script()

    @property
    def pragmas(self) -> List[Pragma]:
        return self._pragmas

    @property
    def printself(self) -> bool:
        return self._printself

    @property
    def modules(self) -> list:
        return self._modules

    @property
    def venv(self) -> str:
        return self._venv

    @property
    def printenv(self) -> bool:
        return self._printenv

    @property
    def likwid(self) -> bool:
        return self._likwid

    @property
    def custom_commands(self) -> list:
        return self._custom_commands

    # @property
    # def inlined_scripts(self) -> list:
    #     return self._inlined_scripts

    @property
    def vars(self) -> list:
        return self._vars


if __name__ == "__main__":
    import slurm_script_generator.pragmas as pragmas

    pragma = pragmas.Account("max")
    nodes = pragmas.Nodes(1)
    script = SlurmScript(
        account="max",
        nodes=1,
        printself=True,
        modules=["gcc/12", "openmpi/4.1"],
        venv="~/virtual_envs/env_slurm",
        custom_commands=["mpirun -n 4 ./bin > run.out"],
    )

    slurm_dict = script.to_dict()
    print(slurm_dict)

    script2 = SlurmScript.from_dict(slurm_dict)
    print(script2.to_json())
