"""Generate a SLURM batch script from a built-in template.

``slurm-template <template> -o job.sh`` writes a ready-to-edit script for a
common job shape (single CPU task, OpenMP, MPI, hybrid MPI+OpenMP, GPU, or a
job array) instead of building one pragma-by-pragma with
``generate-slurm-script``. Run ``slurm-template --list`` to see what's
available.
"""

import argparse
import sys
from typing import List, Optional

from slurm_script_generator.clusters import CLUSTERS, apply_cluster
from slurm_script_generator.templates import TEMPLATES, build_script


def _list_templates() -> str:
    width = max(len(name) for name in TEMPLATES)
    lines = ["Available templates:", ""]
    for name in sorted(TEMPLATES):
        lines.append(f"  {name.ljust(width)}  {TEMPLATES[name].description}")
    return "\n".join(lines)


def _list_clusters() -> str:
    width = max(len(name) for name in CLUSTERS)
    lines = ["Available clusters:", ""]
    for name in sorted(CLUSTERS):
        lines.append(f"  {name.ljust(width)}  {CLUSTERS[name].doc_url}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> None:
    """Entry point for the ``slurm-template`` command-line tool."""
    parser = argparse.ArgumentParser(
        prog="slurm-template",
        description="Generate a SLURM batch script from a built-in template.",
    )
    parser.add_argument(
        "template",
        nargs="?",
        metavar="TEMPLATE",
        help="Template to use (see --list).",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available templates and exit."
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default=None,
        help="Path to save the generated script to. Prints to stdout if omitted.",
    )
    parser.add_argument("--job-name", "-J", metavar="NAME", default=None)
    parser.add_argument("--account", "-A", metavar="ACCOUNT", default=None)
    parser.add_argument("--partition", "-p", metavar="PARTITION", default=None)
    parser.add_argument("--qos", "-q", metavar="QOS", default=None)
    parser.add_argument(
        "--time",
        "-t",
        metavar="TIME",
        default=None,
        help="Wall-clock time limit, e.g. 01:00:00.",
    )
    parser.add_argument("--nodes", "-N", metavar="N", type=int, default=None)
    parser.add_argument("--ntasks", "-n", metavar="N", type=int, default=None)
    parser.add_argument(
        "--ntasks-per-node", metavar="N", type=int, default=None
    )
    parser.add_argument("--cpus-per-task", "-c", metavar="N", type=int, default=None)
    parser.add_argument("--mem", metavar="MEM", default=None, help="e.g. 16G")
    parser.add_argument("--gpus", "-g", metavar="N", default=None)
    parser.add_argument(
        "--array", "-a", metavar="RANGE", default=None, help="e.g. 1-10"
    )
    parser.add_argument(
        "--cluster",
        metavar="NAME",
        default=None,
        help=(
            "Fill in this cluster's typical --partition/--qos (see "
            "--list-clusters); explicit --partition/--qos still win."
        ),
    )
    parser.add_argument(
        "--list-clusters",
        action="store_true",
        help="List clusters known to --cluster and exit.",
    )
    parser.add_argument(
        "--command",
        "-C",
        metavar="CMD",
        action="append",
        default=None,
        help="Replace the template's placeholder command(s); repeatable.",
    )
    parser.add_argument(
        "--modules",
        metavar="MODULE",
        nargs="+",
        default=None,
        help="Replace the template's module list.",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Submit the generated script to the scheduler (requires --output).",
    )

    args = parser.parse_args(argv)

    if args.list:
        print(_list_templates())
        return
    if args.list_clusters:
        print(_list_clusters())
        return
    if args.template is None:
        parser.error("the following arguments are required: TEMPLATE (or pass --list)")
    if args.template not in TEMPLATES:
        parser.error(
            f"Unknown template: {args.template!r}. "
            f"Available: {', '.join(sorted(TEMPLATES))}"
        )
    if args.cluster is not None and args.cluster not in CLUSTERS:
        parser.error(
            f"Unknown cluster: {args.cluster!r}. "
            f"Available: {', '.join(sorted(CLUSTERS))}"
        )

    overrides = {
        "job_name": args.job_name,
        "account": args.account,
        "partition": args.partition,
        "qos": args.qos,
        "time": args.time,
        "nodes": args.nodes,
        "ntasks": args.ntasks,
        "ntasks_per_node": args.ntasks_per_node,
        "cpus_per_task": args.cpus_per_task,
        "mem": args.mem,
        "gpus": args.gpus,
        "array": args.array,
    }

    commands = args.command if args.command else list(TEMPLATES[args.template].commands)

    if args.cluster is not None:
        uses_gpu = args.template == "gpu" or overrides.get("gpus") is not None
        apply_cluster(args.cluster, overrides, uses_gpu)
        preset = CLUSTERS[args.cluster]
        cluster_comments = [f"# Cluster: {args.cluster} — see {preset.doc_url}"]
        cluster_comments += [f"# {note}" for note in preset.notes]
        commands = cluster_comments + commands

    script = build_script(
        args.template,
        overrides=overrides,
        commands=commands,
        modules=args.modules,
    )

    if args.submit:
        if not args.output:
            parser.error("--submit requires --output to be specified")
        script.submit_job(path=args.output)
    elif args.output:
        script.save(path=args.output, verbose=True)
    else:
        print(script.to_string())


if __name__ == "__main__":
    sys.exit(main())
