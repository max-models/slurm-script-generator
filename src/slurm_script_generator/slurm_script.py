import json
from typing import List

from slurm_script_generator.pragmas import Pragma
from slurm_script_generator.utils import add_line


class SlurmScript:
    def __init__(
        self,
        pragmas: List[Pragma],
        printself: bool = False,
        modules: List[str] | None = None,
        venv: str | None = None,
        printenv: bool = False,
        likwid: bool = False,
        custom_command: str | None = None,
        vars: list | None = None,
        line_length: int = 40,
    ) -> None:

        self._pragmas = pragmas
        self._printself = printself
        if modules is None:
            self._modules = []
        else:
            self._modules = modules
        self._venv = venv
        self._printenv = printenv
        self._likwid = likwid
        self._custom_command = custom_command
        if vars is None:
            self._vars = []
        else:
            self._vars = vars
        self._line_length = line_length

    def add_pragma(self, pragma) -> None:
        assert isinstance(pragma, Pragma)
        self._pragmas.append(pragma)

    def generate_script(self, line_length=40) -> str:
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

        if self.custom_command is not None:
            script_repr += add_line(
                self.custom_command,
                line_length=line_length,
            )

        return script_repr

    def __repr__(self) -> str:
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
    def custom_command(self) -> str:
        return self._custom_command

    @property
    def vars(self) -> list:
        return self._vars


if __name__ == "__main__":
    import slurm_script_generator.pragmas as pragmas

    pragma_classes = []
    for _, cls in pragmas.__dict__.items():
        if isinstance(cls, type) and issubclass(cls, Pragma) and cls != Pragma:
            pragma_classes.append(cls.__name__)
    print(pragma_classes)

    pragma = pragmas.Account("max")
    nodes = pragmas.Nodes(1)
    script = SlurmScript([pragma, nodes])
    print(script)
