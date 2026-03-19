import fnmatch
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

# SLURM job state codes
JOB_STATES = {
    "BF": "Boot Fail",
    "CA": "Cancelled",
    "CD": "Completed",
    "CF": "Configuring",
    "CG": "Completing",
    "DL": "Deadline",
    "F": "Failed",
    "NF": "Node Fail",
    "OOM": "Out of Memory",
    "PD": "Pending",
    "PR": "Preempted",
    "R": "Running",
    "RD": "Resv Del Hold",
    "RF": "Requeue Fed",
    "RH": "Requeue Hold",
    "RQ": "Requeued",
    "RS": "Resizing",
    "RV": "Revoked",
    "SI": "Signaling",
    "SE": "Special Exit",
    "SO": "Stage Out",
    "ST": "Stopped",
    "S": "Suspended",
    "TO": "Timeout",
}

# States that mean the job is still alive in the queue
ACTIVE_STATES = {"R", "PD", "CG", "CF", "RQ", "RS", "SI", "SO", "ST", "S", "RH", "RF"}

# squeue --format codes and matching field names
_SEPARATOR = "\x1f"  # ASCII unit separator — won't appear in job fields
_FORMAT_CODES = ["%i", "%u", "%j", "%t", "%P", "%D", "%C", "%M", "%l", "%r", "%Q"]
_FORMAT_STR = _SEPARATOR.join(_FORMAT_CODES)


@dataclass
class SQueueJob:
    """A single job entry from the SLURM queue."""

    job_id: int
    user: str
    name: str
    state: str
    partition: str
    num_nodes: int
    num_cpus: int
    time_used: str
    time_limit: str
    reason: str
    priority: int

    @property
    def is_running(self) -> bool:
        return self.state == "R"

    @property
    def is_pending(self) -> bool:
        return self.state == "PD"

    @property
    def is_active(self) -> bool:
        return self.state in ACTIVE_STATES

    @property
    def state_name(self) -> str:
        return JOB_STATES.get(self.state, self.state)

    def wait_until_done(
        self,
        poll_interval: float = 30.0,
        timeout: Optional[float] = None,
        verbose: bool = True,
    ) -> None:
        """Block until this specific job leaves the active queue.

        Parameters
        ----------
        poll_interval : float
            Seconds between queue polls. Defaults to 30.
        timeout : float, optional
            Maximum seconds to wait before raising ``TimeoutError``.
        verbose : bool
            Print progress messages. Defaults to True.
        """
        SQueue().wait_until_done(
            job_id=self.job_id,
            poll_interval=poll_interval,
            timeout=timeout,
            verbose=verbose,
        )

    def __repr__(self) -> str:
        return (
            f"SQueueJob(job_id={self.job_id}, user={self.user!r}, "
            f"name={self.name!r}, state={self.state!r}({self.state_name}), "
            f"partition={self.partition!r})"
        )


def _parse_int(s: str, default: int = 0) -> int:
    try:
        return int(s.strip())
    except ValueError:
        return default


class SQueue:
    """Interface to the SLURM job queue via ``squeue``.

    Parameters
    ----------
    user : str, optional
        If given, only fetch jobs belonging to this user by default.

    Examples
    --------
    >>> q = SQueue()
    >>> q.summary()
    {'total_jobs': 42, 'running': 30, 'pending': 12, 'users': {...}, 'by_state': {...}}

    >>> q.wait_until_done(job_name='training_*')
    >>> q.wait_until_done(job_id=12345)
    >>> q.wait_until_done(user='alice')
    """

    def __init__(self, user: Optional[str] = None) -> None:
        self._default_user = user
        self._jobs: List[SQueueJob] = []
        self.refresh()

    # ------------------------------------------------------------------
    # Fetching
    # ------------------------------------------------------------------

    def refresh(self) -> "SQueue":
        """Re-run ``squeue`` and update the cached job list.

        Returns
        -------
        SQueue
            self, for chaining.
        """
        cmd = ["squeue", f"--format={_FORMAT_STR}", "--noheader"]
        if self._default_user:
            cmd += ["--user", self._default_user]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"squeue failed: {result.stderr.strip()}")

        self._jobs = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(_SEPARATOR)
            if len(parts) < len(_FORMAT_CODES):
                continue
            try:
                job = SQueueJob(
                    job_id=_parse_int(parts[0]),
                    user=parts[1].strip(),
                    name=parts[2].strip(),
                    state=parts[3].strip(),
                    partition=parts[4].strip(),
                    num_nodes=_parse_int(parts[5]),
                    num_cpus=_parse_int(parts[6]),
                    time_used=parts[7].strip(),
                    time_limit=parts[8].strip(),
                    reason=parts[9].strip(),
                    priority=_parse_int(parts[10]),
                )
                self._jobs.append(job)
            except (ValueError, IndexError):
                continue
        return self

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def jobs(
        self,
        job_name: Optional[str] = None,
        job_id: Optional[int | str] = None,
        user: Optional[str] = None,
        state: Optional[str] = None,
    ) -> List[SQueueJob]:
        """Return jobs matching the given criteria.

        Parameters
        ----------
        job_name : str, optional
            Job name or glob pattern (e.g. ``'train_*'``).
        job_id : int or str, optional
            Exact job ID.
        user : str, optional
            Username to filter by.
        state : str, optional
            SLURM state code, e.g. ``'R'`` or ``'PD'``.

        Returns
        -------
        list of SQueueJob
        """
        result = list(self._jobs)
        if job_id is not None:
            result = [j for j in result if j.job_id == int(job_id)]
        if user is not None:
            result = [j for j in result if j.user == user]
        if state is not None:
            result = [j for j in result if j.state == state]
        if job_name is not None:
            result = [j for j in result if fnmatch.fnmatch(j.name, job_name)]
        return result

    def running_jobs(self) -> List[SQueueJob]:
        """Return all jobs currently in the R (Running) state."""
        return [j for j in self._jobs if j.is_running]

    def pending_jobs(self) -> List[SQueueJob]:
        """Return all jobs currently in the PD (Pending) state."""
        return [j for j in self._jobs if j.is_pending]

    # ------------------------------------------------------------------
    # Waiting
    # ------------------------------------------------------------------

    def wait_until_done(
        self,
        job_name: Optional[str] = None,
        job_id: Optional[int | str] = None,
        user: Optional[str] = None,
        poll_interval: float = 30.0,
        timeout: Optional[float] = None,
        verbose: bool = True,
    ) -> None:
        """Block until all matching jobs leave the active queue.

        Supports glob patterns in *job_name* (``*`` and ``?`` wildcards).
        At least one filter argument must be provided.

        Parameters
        ----------
        job_name : str, optional
            Job name or glob pattern, e.g. ``'train_*'``.
        job_id : int or str, optional
            A specific job ID to wait for.
        user : str, optional
            Wait for all jobs belonging to this user to finish.
        poll_interval : float
            Seconds between queue polls. Defaults to 30.
        timeout : float, optional
            Maximum seconds to wait before raising ``TimeoutError``.
        verbose : bool
            Print progress messages. Defaults to True.

        Raises
        ------
        ValueError
            If no filter is specified.
        TimeoutError
            If *timeout* is exceeded before all jobs finish.
        """
        if job_name is None and job_id is None and user is None:
            raise ValueError("Specify at least one of: job_name, job_id, user")

        start = time.monotonic()
        while True:
            self.refresh()
            active = [
                j
                for j in self.jobs(job_name=job_name, job_id=job_id, user=user)
                if j.is_active
            ]
            if not active:
                if verbose:
                    print("All matching jobs have finished.")
                return

            if timeout is not None and (time.monotonic() - start) > timeout:
                ids = [j.job_id for j in active]
                raise TimeoutError(
                    f"Timed out after {timeout}s. Still active job IDs: {ids}"
                )

            if verbose:
                ids = [j.job_id for j in active]
                print(
                    f"Waiting — {len(active)} job(s) still active {ids}. "
                    f"Polling again in {poll_interval}s."
                )
            time.sleep(poll_interval)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def users(self) -> List[str]:
        """Return a sorted list of unique users with jobs in the queue."""
        return sorted(set(j.user for j in self._jobs))

    def jobs_by_user(self) -> Dict[str, List[SQueueJob]]:
        """Return a mapping of username -> list of their jobs."""
        result: Dict[str, List[SQueueJob]] = {}
        for job in self._jobs:
            result.setdefault(job.user, []).append(job)
        return result

    def jobs_by_state(self) -> Dict[str, List[SQueueJob]]:
        """Return a mapping of state code -> list of jobs in that state."""
        result: Dict[str, List[SQueueJob]] = {}
        for job in self._jobs:
            result.setdefault(job.state, []).append(job)
        return result

    def summary(self) -> dict:
        """Return a summary dict with total counts, per-user counts, and per-state counts.

        Returns
        -------
        dict
            Keys: ``total_jobs``, ``running``, ``pending``,
            ``users`` (dict of user -> job count),
            ``by_state`` (dict of state code -> job count).
        """
        by_state = self.jobs_by_state()
        by_user = self.jobs_by_user()
        return {
            "total_jobs": len(self._jobs),
            "running": len(by_state.get("R", [])),
            "pending": len(by_state.get("PD", [])),
            "users": {u: len(jobs) for u, jobs in sorted(by_user.items())},
            "by_state": {s: len(jobs) for s, jobs in sorted(by_state.items())},
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._jobs)

    def __iter__(self):
        return iter(self._jobs)

    def __str__(self) -> str:
        if not self._jobs:
            return "SLURM Queue  ·  empty"

        total_running = sum(1 for j in self._jobs if j.is_running)
        total_pending = sum(1 for j in self._jobs if j.is_pending)
        total_nodes = sum(j.num_nodes for j in self._jobs if j.is_running)
        total_cpus = sum(j.num_cpus for j in self._jobs if j.is_running)

        # Build per-user stats
        rows = []
        for user, jobs in self.jobs_by_user().items():
            running = [j for j in jobs if j.is_running]
            pending = [j for j in jobs if j.is_pending]
            nodes = sum(j.num_nodes for j in running)
            cpus = sum(j.num_cpus for j in running)
            rows.append((user, len(jobs), len(running), len(pending), nodes, cpus))

        # Heaviest users (by running nodes, then running jobs) first
        rows.sort(key=lambda r: (-r[4], -r[2], -r[1]))

        headers = ["User", "Jobs", "Running", "Pending", "Nodes (R)", "CPUs (R)"]
        totals = [
            "TOTAL",
            str(len(self._jobs)),
            str(total_running),
            str(total_pending),
            str(total_nodes),
            str(total_cpus),
        ]

        # Column widths: user left-aligned, rest right-aligned
        str_rows = [
            [r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5])] for r in rows
        ]
        widths = [
            max(
                len(headers[i]),
                len(totals[i]),
                max((len(r[i]) for r in str_rows), default=0),
            )
            for i in range(len(headers))
        ]

        def fmt_row(vals: list, bold_first: bool = False) -> str:
            cells = [vals[0].ljust(widths[0])]
            for i in range(1, len(vals)):
                cells.append(vals[i].rjust(widths[i]))
            return "  " + "   ".join(cells)

        table_width = sum(widths) + 3 * (len(widths) - 1) + 2
        title = f"SLURM Queue  ·  {len(self._jobs)} jobs total  ·  {total_running} running  ·  {total_pending} pending"
        width = max(table_width, len(title))
        bar_heavy = "═" * width
        bar_light = "─" * width

        lines = [
            title,
            bar_heavy,
            fmt_row(headers),
            bar_light,
            *[fmt_row(r) for r in str_rows],
            bar_light,
            fmt_row(totals),
            bar_heavy,
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        s = self.summary()
        return (
            f"SQueue(total={s['total_jobs']}, running={s['running']}, "
            f"pending={s['pending']}, users={list(s['users'].keys())})"
        )


def _fmt_job_table(jobs: List[SQueueJob]) -> str:
    """Format a list of jobs as an aligned table string."""
    if not jobs:
        return "  (no jobs)"
    headers = ["JobID", "User", "Job Name", "State", "Partition", "Nodes", "CPUs", "Used", "Limit"]
    rows = [
        [
            str(j.job_id),
            j.user,
            j.name,
            j.state_name,
            j.partition,
            str(j.num_nodes),
            str(j.num_cpus),
            j.time_used,
            j.time_limit,
        ]
        for j in jobs
    ]
    widths = [
        max(len(headers[i]), max(len(r[i]) for r in rows))
        for i in range(len(headers))
    ]

    def fmt(vals: list) -> str:
        # JobID, Nodes, CPUs right-aligned; rest left-aligned
        right = {0, 5, 6}
        cells = [
            vals[i].rjust(widths[i]) if i in right else vals[i].ljust(widths[i])
            for i in range(len(vals))
        ]
        return "  " + "   ".join(cells)

    bar = "─" * (sum(widths) + 3 * (len(widths) - 1) + 2)
    lines = [fmt(headers), bar, *[fmt(r) for r in rows]]
    return "\n".join(lines)


def main() -> None:
    """Entry point for the ``slurm-queue`` command-line tool.

    Sub-commands
    ------------
    show  (default)
        Print a per-user queue summary table.
    list
        Print individual jobs, optionally filtered.
    wait
        Block until matching jobs leave the active queue.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="slurm-queue",
        description="Inspect and wait on the SLURM job queue.",
    )
    parser.add_argument(
        "--user", "-u",
        metavar="USER",
        default=None,
        help="Restrict all squeue calls to this user.",
    )
    sub = parser.add_subparsers(dest="cmd")

    # ---- show ---------------------------------------------------------------
    p_show = sub.add_parser("show", help="Print per-user queue summary (default).")
    p_show.add_argument("--user", "-u", metavar="USER", default=None,
                        help="Filter to this user.")

    # ---- list ---------------------------------------------------------------
    p_list = sub.add_parser("list", help="List individual jobs.")
    p_list.add_argument("--user", "-u", metavar="USER", default=None)
    p_list.add_argument("--job-name", "-n", metavar="PATTERN", default=None,
                        help="Filter by job name (glob patterns supported, e.g. 'train_*').")
    p_list.add_argument("--job-id", "-j", metavar="ID", type=int, default=None,
                        help="Filter to a specific job ID.")
    p_list.add_argument("--state", "-s", metavar="STATE", default=None,
                        help="Filter by state code, e.g. R, PD, CG.")

    # ---- wait ---------------------------------------------------------------
    p_wait = sub.add_parser("wait", help="Wait until matching jobs leave the active queue.")
    p_wait.add_argument("--job-name", "-n", metavar="PATTERN", default=None,
                        help="Job name or glob pattern to wait for (e.g. 'train_*').")
    p_wait.add_argument("--job-id", "-j", metavar="ID", type=int, default=None,
                        help="Wait for a specific job ID.")
    p_wait.add_argument("--user", "-u", metavar="USER", default=None,
                        help="Wait for all jobs belonging to this user.")
    p_wait.add_argument("--poll-interval", "-i", metavar="SECONDS", type=float, default=30.0,
                        help="Seconds between queue polls (default: 30).")
    p_wait.add_argument("--timeout", "-t", metavar="SECONDS", type=float, default=None,
                        help="Raise an error if jobs are still running after this many seconds.")
    p_wait.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress progress messages.")

    args = parser.parse_args()

    # Default sub-command: show
    if args.cmd is None or args.cmd == "show":
        user = getattr(args, "user", None)
        try:
            q = SQueue(user=user)
            print(q)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "list":
        try:
            q = SQueue(user=args.user)
            jobs = q.jobs(
                job_name=args.job_name,
                job_id=args.job_id,
                state=args.state,
            )
            print(_fmt_job_table(jobs))
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "wait":
        if args.job_name is None and args.job_id is None and args.user is None:
            p_wait.error("Specify at least one of: --job-name, --job-id, --user")
        try:
            q = SQueue()
            q.wait_until_done(
                job_name=args.job_name,
                job_id=args.job_id,
                user=args.user,
                poll_interval=args.poll_interval,
                timeout=args.timeout,
                verbose=not args.quiet,
            )
        except TimeoutError as e:
            print(f"Timeout: {e}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
