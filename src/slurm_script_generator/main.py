import argparse
import json

from slurm_script_generator.slurm_script import SlurmScript
from slurm_script_generator.utils import add_line
import slurm_script_generator.pragmas as pragmas


def add_misc_options(parser: argparse.ArgumentParser) -> None:

    parser.add_argument(
        "--line-length",
        dest="line_length",
        type=int,
        default=None,
        metavar="LINE_LENGTH",
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
        "--custom-command",
        dest="custom_command",
        type=str,
        default=None,
        metavar="COMMAND",
        help="Add a custom command at the end of the script (e.g. --custom-command 'mpirun -n 8 ./bin > run.out')",
    )

    parser.add_argument(
        "--custom-commands",
        dest="custom_commands",
        type=str,
        nargs="+",
        default=[],
        metavar="COMMAND",
        help="Add custom commands at the end of the script (e.g. --custom-commands '# Run simulation' 'mpirun -n 8 ./bin > run.out')",
    )

    parser.add_argument(
        "--inline-script",
        dest="inlined_script",
        type=str,
        default=None,
        metavar="COMMAND",
        help="Inline script to add at the end of the script (e.g. --inline-script script.sh)",
    )

    parser.add_argument(
        "--inline-scripts",
        dest="inlined_scripts",
        type=str,
        nargs="+",
        default=[],
        metavar="COMMAND",
        help="Add inline scripts at the end of the script (e.g. --inline-scripts script1.sh script2.sh)",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Slurm job submission options",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    pragma_dict = {}

    # Add each pragma as an argument to the parser
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
                    dest=pragma_cls.arg_varname,
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
                    dest=pragma_cls.arg_varname,
                    help=pragma_cls.help,
                    action=pragma_cls.action,
                    default=pragma_cls.default,
                )

    # Add the other options
    add_misc_options(parser=parser)

    # Parse the arguments
    sbatch_args = parser.parse_args()

    # Extract the paths for JSON input/output and the output script
    path_json_out = sbatch_args.export_json
    path_json_in = sbatch_args.input
    path_out = sbatch_args.output
    delattr(sbatch_args, "export_json")
    delattr(sbatch_args, "input")
    delattr(sbatch_args, "output")

    # If a JSON input path is provided, load the SlurmScript from that JSON file.
    # Otherwise, create a new SlurmScript instance.
    if path_json_in is not None:
        slurm_script = SlurmScript.from_json(path=path_json_in)
    else:
        slurm_script = SlurmScript()

    # Convert the remaining arguments to pragmas or other SlurmScript parameters
    args_dict = {}
    pragma_list = []
    for arg_varname in vars(sbatch_args):
        value = getattr(sbatch_args, arg_varname)
        # print(f"Processing argument {arg_varname} with value {value}")
        if value is None:
            continue
        if value is False:
            continue
        if isinstance(value, list) and len(value) == 0:
            continue
        if pragmas.PragmaFactory.is_valid_pragma_key(arg_varname):
            pragma = pragmas.PragmaFactory.create_pragma(
                key=arg_varname,
                value=value,
            )
            print(pragma)
            slurm_script.add_pragma(pragma=pragma)
        else:
            args_dict.update({arg_varname: value})
    print(args_dict)

    if path_json_out is not None:
        slurm_script.to_json(path=path_json_out)

    if path_out:
        with open(path_out, "w") as f:
            f.write(str(slurm_script))
    else:
        print(slurm_script)


if __name__ == "__main__":
    main()
