import argparse
import json

# import slurm_script_generator.sbatch_parser as sbatch_parser
# from slurm_script_generator import slurm_script
# from slurm_script_generator.sbatch import register_to_parser
from slurm_script_generator.slurm_script import SlurmScript
from slurm_script_generator.utils import add_line


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

    parser.add_argument(
        "--command",
        dest="custom_command",
        type=str,
        default=None,
        metavar="COMMAND",
        help="Add a custom command at the end of the script (e.g. mpirun -n 8 ./bin > run.out)",
    )

    return parser


def export_json(args_dict, path):
    with open(path, "w") as f:
        json.dump(args_dict, f)


def read_yaml(path):
    with open(path, "r") as f:
        return json.load(f)


# def generate_script(args_dict, print_script=True):

#     line_length = args_dict.get("line_length", 60)

#     # Start generating the SLURM batch script
#     script = "#!/bin/bash\n"
#     script += "#" * (line_length + 2) + "\n"

#     for pragma in sbatch_parser.pragmas:
#         # print(f"{pragma.dest = } {list(args_dict.keys()) = }")
#         if pragma.dest in list(args_dict.keys()):
#             # print(f"{pragma.dest = }")
#             val = args_dict.get(pragma.dest)
#             if val not in [None, False]:
#                 script += add_line(
#                     f"#SBATCH {pragma.sbatch_flag}={val}",
#                     pragma.help,
#                     line_length=line_length,
#                 )
#     script += "#" * (line_length + 2) + "\n\n"

#     vars = args_dict.get("vars", [])
#     if len(vars) > 0:
#         for var in vars:
#             script += add_line(
#                 f"export {var}",
#                 "Set environment variable",
#                 line_length=line_length,
#             )

#     if args_dict.get("printself", False):
#         script += add_line(
#             f"cat $0",
#             "print this batch script",
#             line_length=line_length,
#         )

#     # Load modules
#     if len(args_dict.get("modules", [])) > 0:
#         script += add_line(
#             "module purge",
#             "Purge modules",
#             line_length=line_length,
#         )
#         script += add_line(
#             f"module load {' '.join(args_dict.get('modules'))}",
#             "modules",
#             line_length=line_length,
#         )
#         script += add_line(
#             "module list",
#             "List loaded modules",
#             line_length=line_length,
#         )

#     if args_dict.get("venv", None) is not None:
#         script += add_line(
#             f"source {args_dict.get('venv')}/bin/activate",
#             "virtual environment",
#             line_length=line_length,
#         )

#     if args_dict.get("printenv", False):
#         script += add_line(
#             "printenv",
#             "print environment variables",
#             line_length=line_length,
#         )

#     if args_dict.get("likwid", False):
#         script += add_line(
#             "LIKWID_PREFIX=$(realpath $(dirname $(which likwid-topology))/..)",
#             "Set LIKWID prefix",
#             line_length=line_length,
#         )

#         script += add_line(
#             "export LD_LIBRARY_PATH=$LIKWID_PREFIX/lib",
#             "Set LD_LIBRARY_PATH for LIKWID",
#             line_length=line_length,
#         )

#         script += add_line(
#             "likwid-topology > likwid-topology.txt",
#             "Save LIKWID topology information",
#             line_length=line_length,
#         )
#         script += add_line(
#             "likwid-topology -g > likwid-topology-g.txt",
#             "Save graphical LIKWID topology information",
#             line_length=line_length,
#         )

#         script += "\n"

#     if args_dict.get("custom_command", None) is not None:
#         script += add_line(
#             args_dict.get("custom_command"),
#             line_length=line_length,
#         )

#     if args_dict.get("export_json", None) is not None:
#         path = args_dict.pop("export_json")
#         export_json(args_dict=args_dict, path=path)
#     if args_dict.get("output") is not None:
#         with open(args_dict.get("output"), "w") as f:
#             f.write(script)

#     if print_script:
#         print(script)

#     return script


def main():
    parser = argparse.ArgumentParser(
        description="Slurm job submission options",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    import slurm_script_generator.pragmas as pragmas

    pragma_dict = {}

    for _, pragma_cls in pragmas.__dict__.items():
        if (
            isinstance(pragma_cls, type)
            and issubclass(pragma_cls, pragmas.Pragma)
            and pragma_cls != pragmas.Pragma
        ):
            # print(f"{pragma_cls = }")
            pragma_dict[pragma_cls.dest] = pragma_cls
            if pragma_cls.action is None:
                parser.add_argument(
                    *pragma_cls.flags,
                    dest=pragma_cls.dest,
                    metavar=pragma_cls.metavar,
                    help=pragma_cls.help,
                    type=pragma_cls.type,
                    nargs=pragma_cls.nargs,
                    choices=pragma_cls.choices,
                    default=pragma_cls.default,
                )
            else:
                parser.add_argument(
                    *pragma_cls.flags,
                    dest=pragma_cls.dest,
                    help=pragma_cls.help,
                    action=pragma_cls.action,
                    default=pragma_cls.default,
                )

    add_misc_options(parser=parser)

    sbatch_args = parser.parse_args()

    if sbatch_args.input is None:
        args_dict = {}
    else:
        args_dict = read_yaml(sbatch_args.input)

    pragma_list = []
    for arg in sbatch_args.__dict__:
        val = sbatch_args.__dict__[arg]
        if val is not None and val is not False:
            if arg in list(pragma_dict.keys()):
                pragma_list.append(pragma_dict[arg](val))
            else:
                # if isinstance(val, list) and len(val) == 0:
                #     continue
                # print(arg, val)
                args_dict.update({arg: val})

    path_export = None
    if args_dict.get("export_json", None) is not None:
        path_export = args_dict.pop("export_json")
        # export_json(args_dict=args_dict, path=path)

    path_out = None
    if args_dict.get("output") is not None:
        path_out = args_dict.pop("output")

    slurm_script = SlurmScript(pragmas=pragma_list, **args_dict)

    # if path_export:
    #     slurm_script.export_json(path_export)

    if path_out:
        with open(path_out, "w") as f:
            f.write(str(slurm_script))
    else:
        print(slurm_script)


if __name__ == "__main__":
    main()
