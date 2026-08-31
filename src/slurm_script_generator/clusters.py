"""Per-cluster presets for ``slurm-template``'s ``--cluster`` flag.

Each preset fills in the handful of pragmas that are specific to one HPC
system's SLURM configuration — mainly ``--partition`` and ``--qos``, chosen
separately for CPU-only and GPU jobs — without touching anything the caller
already set explicitly. It also points at that system's own documentation,
since partition/QOS naming and limits are the kind of thing that changes
over time and should be double-checked there, not trusted blindly from here.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ClusterPreset:
    """Typical partition/QOS defaults for one HPC system."""

    doc_url: str
    cpu_partition: Optional[str] = None
    cpu_qos: Optional[str] = None
    gpu_partition: Optional[str] = None
    gpu_qos: Optional[str] = None
    notes: List[str] = field(default_factory=list)


# Values below are taken from each cluster's own SLURM documentation (see
# doc_url) at the time they were added — re-check there if a job is rejected,
# since partitions/QOS/limits do change.
CLUSTERS: Dict[str, ClusterPreset] = {
    "pitagora": ClusterPreset(
        doc_url="https://docs.hpc.cineca.it/hpc/pitagora.html#job-managing-and-slurm-partitions",
        cpu_partition="dcgp_fua_prod",
        cpu_qos="normal",
        gpu_partition="boost_fua_prod",
        gpu_qos="normal",
        notes=[
            "Production partitions on Pitagora need a budgeted --account; "
            "only ptgr_all_serial is budget-free.",
        ],
    ),
}


def apply_cluster(name: str, overrides: Dict[str, object], uses_gpu: bool) -> None:
    """Fill cluster-specific partition/QOS defaults into *overrides*, in place.

    Only sets a key that's still None, so a value the caller already passed
    explicitly (e.g. an explicit ``--partition``) always wins over the preset.

    Parameters
    ----------
    name : str
        A key in :data:`CLUSTERS`.
    overrides : dict
        The in-progress overrides dict to update in place.
    uses_gpu : bool
        Whether the job requests a GPU, to pick the GPU vs CPU partition/QOS.

    Raises
    ------
    KeyError
        If *name* is not a known cluster.
    """
    if name not in CLUSTERS:
        raise KeyError(
            f"Unknown cluster: {name!r}. Available: {', '.join(sorted(CLUSTERS))}"
        )
    preset = CLUSTERS[name]
    partition = preset.gpu_partition if uses_gpu else preset.cpu_partition
    qos = preset.gpu_qos if uses_gpu else preset.cpu_qos
    if overrides.get("partition") is None and partition is not None:
        overrides["partition"] = partition
    if overrides.get("qos") is None and qos is not None:
        overrides["qos"] = qos
