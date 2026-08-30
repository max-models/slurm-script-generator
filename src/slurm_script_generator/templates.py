"""Built-in SLURM script templates for common job shapes.

Each template is a starting point, not a finished script: the placeholder
command(s) need to be replaced with your own, and the pragma defaults are
reasonable guesses that should be adjusted to the job at hand. Used by the
``slurm-template`` CLI (see :mod:`slurm_script_generator.slurm_template`).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from slurm_script_generator.slurm_script import SlurmScript


@dataclass
class Template:
    """A named starting point for a SLURM script."""

    description: str
    defaults: Dict[str, object] = field(default_factory=dict)
    commands: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)


TEMPLATES: Dict[str, Template] = {
    "cpu": Template(
        description="Single-node, single-task CPU job.",
        defaults=dict(
            job_name="cpu_job",
            nodes=1,
            ntasks=1,
            cpus_per_task=1,
            time="01:00:00",
        ),
        commands=["./my_program"],
    ),
    "openmp": Template(
        description="Single-node, multi-threaded (OpenMP) job.",
        defaults=dict(
            job_name="openmp_job",
            nodes=1,
            ntasks=1,
            cpus_per_task=8,
            time="01:00:00",
        ),
        commands=[
            "export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK",
            "./my_omp_program",
        ],
    ),
    "mpi": Template(
        description="Multi-node MPI job, one rank per node.",
        defaults=dict(
            job_name="mpi_job",
            nodes=4,
            ntasks_per_node=1,
            time="01:00:00",
        ),
        commands=["srun ./my_mpi_program"],
    ),
    "hybrid": Template(
        description=(
            "Hybrid MPI + OpenMP job (one rank per node, " "multiple threads per rank)."
        ),
        defaults=dict(
            job_name="hybrid_job",
            nodes=4,
            ntasks_per_node=1,
            cpus_per_task=8,
            time="01:00:00",
        ),
        commands=[
            "export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK",
            "srun ./my_hybrid_program",
        ],
    ),
    "gpu": Template(
        description="Single-node job with one GPU.",
        defaults=dict(
            job_name="gpu_job",
            nodes=1,
            ntasks=1,
            cpus_per_task=4,
            gpus=1,
            time="01:00:00",
        ),
        commands=["./my_gpu_program"],
    ),
    "array": Template(
        description=(
            "Job array (10 tasks); use $SLURM_ARRAY_TASK_ID to pick work per task."
        ),
        defaults=dict(
            job_name="array_job",
            array="1-10",
            nodes=1,
            ntasks=1,
            time="01:00:00",
        ),
        commands=["./my_program --task-id $SLURM_ARRAY_TASK_ID"],
    ),
}


def build_script(
    name: str,
    overrides: Optional[Dict[str, object]] = None,
    commands: Optional[List[str]] = None,
    modules: Optional[List[str]] = None,
) -> SlurmScript:
    """Build a :class:`SlurmScript` from a named template.

    Parameters
    ----------
    name : str
        A key in :data:`TEMPLATES`.
    overrides : dict, optional
        Pragma values to override the template defaults with. Keys with a
        None value are ignored, so callers can pass a full set of parsed
        CLI args without stripping the unset ones first.
    commands : list of str, optional
        Replace the template's placeholder command(s).
    modules : list of str, optional
        Replace the template's module list.

    Returns
    -------
    SlurmScript

    Raises
    ------
    KeyError
        If *name* is not a known template.
    """
    if name not in TEMPLATES:
        raise KeyError(
            f"Unknown template: {name!r}. Available: {', '.join(sorted(TEMPLATES))}"
        )
    template = TEMPLATES[name]
    kwargs = dict(template.defaults)
    for key, value in (overrides or {}).items():
        if value is not None:
            kwargs[key] = value
    kwargs["custom_commands"] = commands if commands else list(template.commands)
    kwargs["modules"] = modules if modules else list(template.modules)
    return SlurmScript(**kwargs)
