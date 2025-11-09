import argparse
import json

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

    # Export parameters
    if sbatch_args.export_json:
        # print(f"Exporting setup to {sbatch_args.export_json}")
        with open(sbatch_args.export_json, "w") as f:
            json.dump(vars(sbatch_args), f, indent=2)

    # Read parameters
    if sbatch_args.input is not None:
        # print(f"Reading setup from {sbatch_args.input}")
        with open(sbatch_args.input, "r") as f:
            data = json.load(f)

        # Convert JSON dict to argparse.Namespace
        sbatch_args = argparse.Namespace(**data)

    args_dict = {}
    pragma_list = []
    for arg in sbatch_args.__dict__:
        val = sbatch_args.__dict__[arg]
        if val is not None and val is not False:
            if arg in list(pragma_dict.keys()):
                pragma_list.append(pragma_dict[arg](val))
            else:
                args_dict.update({arg: val})

    path_out = None
    if args_dict.get("output") is not None:
        path_out = args_dict.pop("output")

    slurm_script = SlurmScript(pragmas=pragma_list, **args_dict)

    if path_out:
        with open(path_out, "w") as f:
            f.write(str(slurm_script))
    else:
        print(slurm_script)


if __name__ == "__main__":
    main()
