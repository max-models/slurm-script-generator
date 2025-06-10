import argparse

import slurm_script_generator.sbatch_parser as sbatch_parser


def add_misc_options(parser):

    parser.add_argument(
        "--line-length",
        dest="line_length",
        type=int,
        default=40,
        metavar="LINE_LENGHT",
        help="line length before start of comment",
    )

    parser.add_argument(
        "--modules",
        dest="modules",
        type=str,
        nargs="+",
        default=[],
        metavar="MODULES",
        help="Modules to load (e.g., --modules mod1 mod2 mod3)",
    )

    parser.add_argument(
        "--venv",
        dest="venv",
        type=str,
        default=None,
        metavar="VENV",
        help="virtual environment to load with `source VENV/bin/activate`",
    )

    parser.add_argument(
        "--printenv",
        action="store_true",
        dest="printenv",
        help="print all environment variables",
    )

    parser.add_argument(
        "--print-self",
        action="store_true",
        dest="printself",
        help="print the batch script in the batch script",
    )

    parser.add_argument(
        "--likwid",
        action="store_true",
        dest="likwid",
        help="Set up likwid environment variables",
    )

    return parser


def add_line(line, comment="", line_length=40):
    if len(line) > line_length:
        return f"{line} # {comment}\n"
    else:
        return f"{line} {' ' * (line_length - len(line))}# {comment}\n"


def main():
    parser = argparse.ArgumentParser(
        description="Slurm job submission options",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    sbatch_parser.add_slurm_options(parser=parser)

    slurm_options_dict = {}
    for action in parser._actions:
        slurm_options_dict[action.dest] = action.help

    add_misc_options(parser=parser)

    sbatch_args = parser.parse_args()

    line_length = sbatch_args.line_length

    # Default parameters for the batch script
    params = {
        "working_directory": "./",
        "job_name": "job_struphy",
        "output_file": "./job_struphy_%j.out",
        "error_file": "./job_struphy_%j.err",
        "nodes": 1,
        "ntasks_per_node": 72,
        "mail_user": "",
        "time": "00:10:00",
        "venv_path": "~/git_repos/env_struphy_devel",
        "partition": None,
        "ntasks_per_core": None,
        "cpus_per_task": None,
        "memory": "2GB",
        "module_setup": "module load anaconda/3/2023.03 gcc/12 openmpi/4.1 likwid/5.2",
        "likwid": False,
    }

    # Update params with any provided keyword arguments
    # params.update(kwargs)

    # Start generating the SLURM batch script
    script = "#!/bin/bash\n"
    script += "#" * (line_length + 2) + "\n"
    for arg in sbatch_args.__dict__:
        val = sbatch_args.__dict__[arg]
        if val is not None and val is not False:
            # print(f"{arg} {list(slurm_options_dict.keys()) = }")
            if arg in list(slurm_options_dict.keys()):
                script += add_line(
                    f"#SBATCH --{arg} {val}",
                    slurm_options_dict[arg],
                    line_length=line_length,
                )
    script += "#" * (line_length + 2) + "\n\n"

    if sbatch_args.printself:
        script += add_line(
            f"cat $0",
            "print this batch script",
            line_length=line_length,
        )

    # Load modules
    if len(sbatch_args.modules) > 0:
        script += add_line(
            "module purge",
            "Purge modules",
            line_length=line_length,
        )
        script += add_line(
            f"module load {' '.join(sbatch_args.modules)}",
            "modules",
            line_length=line_length,
        )
        script += add_line(
            "module list",
            "List loaded modules",
            line_length=line_length,
        )

    if sbatch_args.venv is not None:
        script += add_line(
            f"source {sbatch_args.venv}/bin/activate",
            "virtual environment",
            line_length=line_length,
        )

    if sbatch_args.printenv:
        script += add_line(
            "printenv",
            "print environment variables",
            line_length=line_length,
        )

    if sbatch_args.likwid:
        script += add_line(
            "LIKWID_PREFIX=$(realpath $(dirname $(which likwid-topology))/..)",
            "Set LIKWID prefix",
            line_length=line_length,
        )

        script += add_line(
            "export LD_LIBRARY_PATH=$LIKWID_PREFIX/lib",
            "Set LD_LIBRARY_PATH for LIKWID",
            line_length=line_length,
        )

        script += add_line(
            "likwid-topology > likwid-topology.txt",
            "Save LIKWID topology information",
            line_length=line_length,
        )
        script += add_line(
            "likwid-topology -g > likwid-topology-g.txt",
            "Save graphical LIKWID topology information",
            line_length=line_length,
        )

        script += "\n"

    return script
