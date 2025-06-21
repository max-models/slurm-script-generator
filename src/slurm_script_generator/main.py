import argparse
import json

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
        "--vars",
        dest="vars",
        type=str,
        nargs="+",
        default=[],
        metavar="ENVIRONMENT_VARS",
        help="Environment variables to export (e.g., --vars VAR1=a VAR2=b)",
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

    parser.add_argument(
        "--input",
        dest="input",
        type=str,
        default=None,
        metavar="INPUT_PATH",
        help="path to input json file",
    )

    parser.add_argument(
        "--output",
        dest="output",
        type=str,
        default=None,
        metavar="OUTPUT_PATH",
        help="json path to save slurm batch script to",
    )

    parser.add_argument(
        "--export-json",
        dest="export_json",
        type=str,
        default=None,
        metavar="JSON_PATH",
        help="path to export yaml for generating the slurm script to",
    )
    return parser


def add_line(line, comment="", line_length=40):
    if len(line) > line_length:
        return f"{line} # {comment}\n"
    else:
        return f"{line} {' ' * (line_length - len(line))}# {comment}\n"


def export_json(args_dict, path):
    with open(path, "w") as f:
        json.dump(args_dict, f)


def read_yaml(path):
    with open(path, "r") as f:
        return json.load(f)


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

    if sbatch_args.input is not None:
        args_dict = read_yaml(sbatch_args.input)
    else:
        args_dict = {}
    for arg in sbatch_args.__dict__:
        val = sbatch_args.__dict__[arg]
        if val is not None and val is not False:
            if isinstance(val, list) and len(val) == 0:
                continue
            args_dict.update({arg: val})

    line_length = args_dict.get("line_length", 60)

    # Start generating the SLURM batch script
    script = "#!/bin/bash\n"
    script += "#" * (line_length + 2) + "\n"

    for arg_help in slurm_options_dict.items():
        arg = arg_help[0]
        help = arg_help[1]
        val = args_dict.get(arg)
        if val is not None and val is not False:
            script += add_line(
                f"#SBATCH --{arg} {val}",
                help,
                line_length=line_length,
            )
    script += "#" * (line_length + 2) + "\n\n"

    vars = args_dict.get("vars", [])
    if len(vars) > 0:
        for var in vars:
            script += add_line(
                f"export {var}",
                "Set environment variable",
                line_length=line_length,
            )

    if args_dict.get("printself", False):
        script += add_line(
            f"cat $0",
            "print this batch script",
            line_length=line_length,
        )

    # Load modules
    if len(args_dict.get("modules", [])) > 0:
        script += add_line(
            "module purge",
            "Purge modules",
            line_length=line_length,
        )
        script += add_line(
            f"module load {' '.join(args_dict.get('modules'))}",
            "modules",
            line_length=line_length,
        )
        script += add_line(
            "module list",
            "List loaded modules",
            line_length=line_length,
        )

    if args_dict.get("venv", None) is not None:
        script += add_line(
            f"source {args_dict.get('venv')}/bin/activate",
            "virtual environment",
            line_length=line_length,
        )

    if args_dict.get("printenv", False):
        script += add_line(
            "printenv",
            "print environment variables",
            line_length=line_length,
        )

    if args_dict.get("likwid", False):
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
    if args_dict.get("export_json", None) is not None:
        path = args_dict.pop("export_json")
        export_json(args_dict=args_dict, path=path)
    if args_dict.get("output") is not None:
        with open(args_dict.get("output"), "w") as f:
            f.write(script)
    else:
        print(script)
