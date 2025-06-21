from argparse import ArgumentParser
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


@dataclass
class Flag:
    name: str
    help: str


@dataclass
class Pragma:
    flags: List[Flag]  # e.g. ['-A', '--account']
    dest: str  # e.g. 'account'
    help: Optional[str] = ""  # e.g. 'charge job to specified account'
    nargs: Optional[str] = None
    const: Optional[int] = None
    choices: Optional[list] = None
    metavar: Optional[str] = None  # e.g. 'NAME'
    action: Optional[str] = None  # e.g. 'store_true', 'store_false'
    default: Optional[str] = None  # Optional default value
    type: Optional[Callable[[str], Any]] = str  # e.g. str, int, float, etc.
    env_var: Optional[str] = None  # Environment variable

    def add_argument_to_parser(self, parser: ArgumentParser):

        kwargs = {
            "dest": self.dest,
            "type": self.type,
            "default": self.default,
            "help": self.help,
        }
        parser.add_argument(
            self.flags[0].name,
            **kwargs,
        )

    @property
    def sbatch_flag(self):
        return self.dest.replace("_", "-")


def register_to_parser(parser, pragma: Pragma):
    kwargs = {"dest": pragma.dest, "help": pragma.help}
    if pragma.metavar:
        kwargs["metavar"] = pragma.metavar
    if pragma.action:
        kwargs["action"] = pragma.action
    if pragma.default:
        kwargs["default"] = pragma.default

    parser.add_argument(*pragma.flags, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Slurm job submission options",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p = Pragma(flags=["--nodes"], dest="nodes", help="Number of nodes", type=str)

    register_to_parser(parser, p)

    sbatch_args = parser.parse_args()

    print(p)
