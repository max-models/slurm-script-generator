"""Turn a batch script into an interactive allocation.

``slurm-alloc job.sh`` reads the ``#SBATCH`` pragmas out of a script and starts
``salloc`` with the same resource request, so the job can be debugged
interactively on the nodes it would have run on. With ``--run`` the body of the
script is executed inside the allocation instead of dropping into a shell.
"""

import argparse
import os
import shlex
import subprocess
import sys
import tempfile
from typing import List, Tuple

from slurm_script_generator.pragmas import Pragma
from slurm_script_generator.slurm_script import SlurmScript

# Long options accepted by salloc (SLURM 25.05). Pragmas whose flag is not in
# here are dropped, since passing them would make salloc exit with a usage
# error. Kept as an allowlist so that sbatch-only options in a script are
# reported rather than silently forwarded.
SALLOC_OPTIONS = frozenset(
    {
        "--account",
        "--acctg-freq",
        "--bb",
        "--bbf",
        "--begin",
        "--bell",
        "--chdir",
        "--cluster-constraint",
        "--clusters",
        "--comment",
        "--consolidate-segments",
        "--constraint",
        "--container",
        "--container-id",
        "--container-type",
        "--contiguous",
        "--core-spec",
        "--cores-per-socket",
        "--cpu-freq",
        "--cpus-per-gpu",
        "--cpus-per-task",
        "--deadline",
        "--delay-boot",
        "--dependency",
        "--distribution",
        "--exclude",
        "--exclusive",
        "--extra",
        "--extra-node-info",
        "--gpu-bind",
        "--gpu-freq",
        "--gpus",
        "--gpus-per-node",
        "--gpus-per-socket",
        "--gpus-per-task",
        "--gres",
        "--gres-flags",
        "--hint",
        "--hold",
        "--immediate",
        "--job-name",
        "--kill-command",
        "--licenses",
        "--mail-type",
        "--mail-user",
        "--mcs-label",
        "--mem",
        "--mem-bind",
        "--mem-per-cpu",
        "--mem-per-gpu",
        "--mem-update",
        "--mincpus",
        "--network",
        "--nice",
        "--no-bell",
        "--no-kill",
        "--no-shell",
        "--nodefile",
        "--nodelist",
        "--nodes",
        "--ntasks",
        "--ntasks-per-core",
        "--ntasks-per-gpu",
        "--ntasks-per-node",
        "--ntasks-per-socket",
        "--oom-kill-step",
        "--overcommit",
        "--oversubscribe",
        "--partition",
        "--prefer",
        "--priority",
        "--profile",
        "--qos",
        "--quiet",
        "--reboot",
        "--reservation",
        "--resources",
        "--resv-ports",
        "--segment",
        "--signal",
        "--sockets-per-node",
        "--spread-job",
        "--spread-segments",
        "--stepmgr",
        "--switches",
        "--thread-spec",
        "--threads-per-core",
        "--time",
        "--time-min",
        "--tmp",
        "--tres-bind",
        "--tres-per-task",
        "--use-min-nodes",
        "--verbose",
        "--wait-all-nodes",
        "--wckey",
        "--x11",
    }
)


def pragma_to_salloc_arg(pragma: Pragma) -> str:
    """Render a pragma as a single salloc command-line argument.

    Args:
        pragma: The pragma to render.

    Returns:
        Either ``"--flag"`` for a valueless switch or ``"--flag=value"``.
    """
    if getattr(pragma, "is_flag", False) or pragma.value is True:
        return pragma.dest
    return f"{pragma.dest}={pragma.value}"


def salloc_args(script: SlurmScript) -> Tuple[List[str], List[str]]:
    """Split a script's pragmas into salloc arguments and dropped options.

    Args:
        script: The parsed batch script.

    Returns:
        A tuple of (arguments to pass to salloc, flags salloc does not accept).
    """
    args: List[str] = []
    dropped: List[str] = []
    for pragma in script.pragmas:
        if pragma.dest in SALLOC_OPTIONS:
            args.append(pragma_to_salloc_arg(pragma))
        else:
            dropped.append(pragma.dest)
    return args, dropped


def script_body(text: str) -> str:
    """Extract the commands of a batch script, dropping shebang and pragmas.

    The body is taken verbatim rather than rebuilt from the parsed script, so
    that comments, quoting and here-documents survive untouched.

    Args:
        text: The full text of the batch script.

    Returns:
        The remaining lines, with leading and trailing blank lines removed.
    """
    lines = [
        line
        for line in text.splitlines()
        if not line.startswith("#!") and not line.strip().startswith("#SBATCH")
    ]
    return "\n".join(lines).strip("\n")


def build_command(
    path: str, run: bool = False, extra_args: List[str] | None = None
) -> Tuple[List[str], str | None]:
    """Build the salloc command for a batch script.

    Args:
        path: Path to the batch script.
        run: Whether to execute the script's commands in the allocation
            instead of starting an interactive shell.
        extra_args: Additional arguments to append to the salloc invocation.

    Returns:
        A tuple of (command as an argument list, the body to run or None).
    """
    with open(path, "r") as f:
        text = f.read()

    script = SlurmScript.from_script(text)
    args, dropped = salloc_args(script)
    if dropped:
        print(
            f"Ignoring options that salloc does not accept: {' '.join(dropped)}",
            file=sys.stderr,
        )

    command = ["salloc", *args, *(extra_args or [])]
    body = script_body(text) if run else None
    return command, body


def main(argv: List[str] | None = None) -> int:
    """Entry point for the ``slurm-alloc`` command-line tool.

    Args:
        argv: Arguments to parse, defaulting to the process arguments.

    Returns:
        The exit code of salloc.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    # Split off pass-through arguments ourselves: argparse.REMAINDER would
    # swallow our own options when they follow the script path.
    if "--" in argv:
        separator = argv.index("--")
        argv, extra_args = argv[:separator], argv[separator + 1 :]
    else:
        extra_args = []

    parser = argparse.ArgumentParser(
        prog="slurm-alloc",
        description=(
            "Start an interactive allocation from the #SBATCH pragmas of a "
            "batch script."
        ),
        epilog=(
            "Arguments after '--' are passed straight to salloc, e.g. "
            "slurm-alloc job.sh -- --x11"
        ),
    )
    parser.add_argument("script", metavar="SCRIPT", help="Path to the batch script.")
    parser.add_argument(
        "--run",
        "-r",
        action="store_true",
        help=(
            "Run the script's commands in the allocation instead of starting "
            "an interactive shell."
        ),
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Print the salloc command instead of running it.",
    )
    args = parser.parse_args(argv)

    if not os.path.isfile(args.script):
        parser.error(f"No such script: {args.script}")

    command, body = build_command(args.script, run=args.run, extra_args=extra_args)

    if body is not None and not body.strip():
        print(
            f"Nothing to run: '{args.script}' has no commands after its pragmas.",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        if body is None:
            print(shlex.join(command))
        else:
            print(shlex.join([*command, "bash", "<script>"]))
            print("\n# <script> would contain:")
            print(f"#!/bin/bash\n{body}")
        return 0

    body_path = None
    try:
        if body is not None:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".sh", prefix="slurm-alloc-", delete=False
            ) as tmp:
                tmp.write(f"#!/bin/bash\n{body}\n")
                body_path = tmp.name
            command += ["bash", body_path]

        try:
            return subprocess.run(command).returncode
        except FileNotFoundError:
            print(
                "salloc not found: is SLURM available on this machine?",
                file=sys.stderr,
            )
            return 127
    finally:
        if body_path is not None:
            os.unlink(body_path)


if __name__ == "__main__":
    sys.exit(main())
