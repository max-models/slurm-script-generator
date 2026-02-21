import argparse

import slurm_script_generator.pragmas as pragmas
from slurm_script_generator.slurm_script import SlurmScript


def add_misc_options(parser: argparse.ArgumentParser) -> None:
    """Add miscellaneous SLURM script options to the argument parser.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The argument parser to which options are added.
    parser :
        argparse.ArgumentParser:
    parser: argparse.ArgumentParser :


    Returns
    -------

    """
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
        "--read-script",
        dest="read_script",
        type=str,
        default=None,
        metavar="SCRIPT_PATH",
        help="Path to a slurm script file to read and include pragmas and commands from (e.g. --read-script sbatch_script.sh)",
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

    parser.add_argument(
        "--no-header",
        dest="no_header",
        action="store_true",
        default=False,
        help="Do not include the header comment in the generated script",
    )

    parser.add_argument(
        "--submit",
        dest="submit",
        action="store_true",
        default=False,
        help="Submit the generated script to the scheduler (requires --output to be specified)",
    )


def main():
    """Main entry point for the SLURM script generator CLI.

    Parses command-line arguments, constructs a SlurmScript object, and handles input/output operations.

    Parameters
    ----------

    Returns
    -------

    """
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

    # Extract the no_header flag
    no_header = sbatch_args.no_header
    submit = sbatch_args.submit
    read_script = sbatch_args.read_script
    delattr(sbatch_args, "no_header")
    delattr(sbatch_args, "submit")
    delattr(sbatch_args, "read_script")

    # If a JSON input path is provided, load the SlurmScript from that JSON file.
    # Otherwise, create a new SlurmScript instance.
    if path_json_in is not None:
        slurm_script = SlurmScript.from_json(path=path_json_in)
    elif read_script is not None:
        slurm_script = SlurmScript.read_script(path=read_script)
    else:
        slurm_script = SlurmScript()

    # Convert the remaining arguments to pragmas or other SlurmScript parameters
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
            slurm_script.add_pragma(pragma=pragma)
        else:
            slurm_script.add_param(arg_varname, value)

    if path_json_out is not None:
        slurm_script.to_json(path=path_json_out)

    if submit:
        if not path_out:
            print("Error: --submit requires --output to be specified")
        else:
            slurm_script.submit_job(path=path_out)
    elif path_out:
        slurm_script.save(path=path_out, include_header=not no_header)
    else:
        print(slurm_script.to_string(include_header=not no_header))


if __name__ == "__main__":
    main()
