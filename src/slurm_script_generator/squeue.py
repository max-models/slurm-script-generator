import fnmatch
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

# ---------------------------------------------------------------------------
# ANSI color helpers — no dependencies, disabled when not writing to a TTY
# or when the NO_COLOR env-var is set (https://no-color.org).
# ---------------------------------------------------------------------------
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_GREEN = "\033[92m"  # bright green
_YELLOW = "\033[93m"  # bright yellow
_RED = "\033[91m"  # bright red
_CYAN = "\033[96m"  # bright cyan


def _supports_color() -> bool:
    return sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(text: str, *codes: str) -> str:
    """Wrap *text* in ANSI escape codes when color output is supported."""
    if not _supports_color():
        return text
    return "".join(codes) + str(text) + _RESET


def _pad(plain: str, colored: str, width: int, align: str = "l") -> str:
    """Pad *colored* to *width* visible characters using *plain* for length."""
    padding = " " * max(0, width - len(plain))
    return (colored + padding) if align == "l" else (padding + colored)


# State-code -> color bucket
_GREEN_STATES = {"R", "CG"}
_YELLOW_STATES = {"PD", "CF", "RQ", "RS", "RH", "RF", "S", "ST", "SI", "SO"}
_RED_STATES = {"F", "BF", "NF", "OOM", "TO", "DL", "PR"}


def _color_state(state_name: str, state_code: str) -> str:
    if state_code in _GREEN_STATES:
        return _c(state_name, _GREEN)
    if state_code in _YELLOW_STATES:
        return _c(state_name, _YELLOW)
    if state_code in _RED_STATES:
        return _c(state_name, _RED)
    return state_name


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
    >>> q.wait_until_done(job_id=[12345, 12346])
    >>> q.wait_until_done(user='alice')
    """

    def __init__(
        self, user: Optional[str] = None, partition: Optional[str] = None
    ) -> None:
        self._default_user = user
        self._default_partition = partition
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
        if self._default_partition:
            cmd += ["--partition", self._default_partition]

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
        job_id: Optional[Union[int, str, List[Union[int, str]]]] = None,
        user: Optional[str] = None,
        state: Optional[str] = None,
        partition: Optional[str] = None,
    ) -> List[SQueueJob]:
        """Return jobs matching the given criteria.

        Parameters
        ----------
        job_name : str, optional
            Job name or glob pattern (e.g. ``'train_*'``).
        job_id : int, str, or list of int/str, optional
            Exact job ID, or a list of job IDs.
        user : str, optional
            Username to filter by.
        state : str, optional
            SLURM state code, e.g. ``'R'`` or ``'PD'``.
        partition : str, optional
            Partition name to filter by.

        Returns
        -------
        list of SQueueJob
        """
        result = list(self._jobs)
        if job_id is not None:
            job_ids = (
                {int(j) for j in job_id} if isinstance(job_id, list) else {int(job_id)}
            )
            result = [j for j in result if j.job_id in job_ids]
        if user is not None:
            result = [j for j in result if j.user == user]
        if state is not None:
            result = [j for j in result if j.state == state]
        if partition is not None:
            result = [j for j in result if j.partition == partition]
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
        job_id: Optional[Union[int, str, List[Union[int, str]]]] = None,
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
        job_id : int, str, or list of int/str, optional
            A specific job ID, or a list of job IDs, to wait for.
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
                    print(_c("✓", _GREEN) + " All matching jobs have finished.")
                return

            if timeout is not None and (time.monotonic() - start) > timeout:
                ids = [j.job_id for j in active]
                raise TimeoutError(
                    f"Timed out after {timeout}s. Still active job IDs: {ids}"
                )

            if verbose:
                ids = [j.job_id for j in active]
                print(
                    _c("~", _YELLOW)
                    + f" Waiting — {_c(str(len(active)), _YELLOW)} job(s) still active {ids}."
                    f" Polling again in {poll_interval}s."
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

    def jobs_by_partition(self) -> Dict[str, List[SQueueJob]]:
        """Return a mapping of partition name -> list of jobs in that partition."""
        result: Dict[str, List[SQueueJob]] = {}
        for job in self._jobs:
            result.setdefault(job.partition, []).append(job)
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
            return _c("SLURM Queue", _BOLD, _CYAN) + "  ·  " + _c("empty", _DIM)

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
        totals_plain = [
            "TOTAL",
            str(len(self._jobs)),
            str(total_running),
            str(total_pending),
            str(total_nodes),
            str(total_cpus),
        ]

        # Column widths computed on plain text so ANSI codes don't shift columns
        str_rows = [
            [r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5])] for r in rows
        ]
        widths = [
            max(
                len(headers[i]),
                len(totals_plain[i]),
                max((len(r[i]) for r in str_rows), default=0),
            )
            for i in range(len(headers))
        ]

        def fmt_header() -> str:
            cells = [_pad(headers[0], _c(headers[0], _BOLD), widths[0], "l")]
            for i in range(1, len(headers)):
                cells.append(_pad(headers[i], _c(headers[i], _BOLD), widths[i], "r"))
            return "  " + "   ".join(cells)

        def fmt_data_row(r: list) -> str:
            cells = [_pad(r[0], r[0], widths[0], "l")]
            cells.append(_pad(r[1], r[1], widths[1], "r"))
            run_c = _c(r[2], _GREEN) if r[2] != "0" else r[2]
            cells.append(_pad(r[2], run_c, widths[2], "r"))
            pend_c = _c(r[3], _YELLOW) if r[3] != "0" else r[3]
            cells.append(_pad(r[3], pend_c, widths[3], "r"))
            cells.append(_pad(r[4], r[4], widths[4], "r"))
            cells.append(_pad(r[5], r[5], widths[5], "r"))
            return "  " + "   ".join(cells)

        def fmt_totals() -> str:
            p = totals_plain
            cells = [_pad(p[0], _c(p[0], _BOLD), widths[0], "l")]
            cells.append(_pad(p[1], _c(p[1], _BOLD), widths[1], "r"))
            cells.append(_pad(p[2], _c(p[2], _BOLD, _GREEN), widths[2], "r"))
            cells.append(_pad(p[3], _c(p[3], _BOLD, _YELLOW), widths[3], "r"))
            cells.append(_pad(p[4], _c(p[4], _BOLD), widths[4], "r"))
            cells.append(_pad(p[5], _c(p[5], _BOLD), widths[5], "r"))
            return "  " + "   ".join(cells)

        table_width = sum(widths) + 3 * (len(widths) - 1) + 2
        title_plain = (
            f"SLURM Queue  \u00b7  {len(self._jobs)} jobs total"
            f"  \u00b7  {total_running} running"
            f"  \u00b7  {total_pending} pending"
        )
        title = (
            _c("SLURM Queue", _BOLD, _CYAN)
            + "  \u00b7  "
            + f"{len(self._jobs)} jobs total"
            + "  \u00b7  "
            + _c(f"{total_running} running", _GREEN)
            + "  \u00b7  "
            + _c(f"{total_pending} pending", _YELLOW)
        )

        width = max(table_width, len(title_plain))
        bar_heavy = _c("\u2550" * width, _DIM)
        bar_light = _c("\u2500" * width, _DIM)

        lines = [
            title,
            bar_heavy,
            fmt_header(),
            bar_light,
            *[fmt_data_row(r) for r in str_rows],
            bar_light,
            fmt_totals(),
            bar_heavy,
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        s = self.summary()
        return (
            f"SQueue(total={s['total_jobs']}, running={s['running']}, "
            f"pending={s['pending']}, users={list(s['users'].keys())})"
        )


_REASON_MAX = 32  # truncate long scheduling-reason strings to this many characters


def _fmt_job_table(jobs: List[SQueueJob], show_reason: bool = False) -> str:
    """Format a list of jobs as an aligned table string."""
    if not jobs:
        return "  (no jobs)"
    headers = [
        "JobID",
        "User",
        "Job Name",
        "State",
        "Partition",
        "Nodes",
        "CPUs",
        "Used",
        "Limit",
    ]
    if show_reason:
        headers.append("Reason")

    def _trunc(s: str) -> str:
        return s[:_REASON_MAX] + "\u2026" if len(s) > _REASON_MAX else s

    # Plain rows for width calculation; colored rows for display
    rows_plain = [
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
        + ([_trunc(j.reason)] if show_reason else [])
        for j in jobs
    ]
    rows_colored = [
        list(plain[:3]) + [_color_state(plain[3], j.state)] + list(plain[4:])
        for j, plain in zip(jobs, rows_plain)
    ]
    widths = [
        max(len(headers[i]), max(len(r[i]) for r in rows_plain))
        for i in range(len(headers))
    ]
    right = {0, 5, 6}

    def fmt_header() -> str:
        cells = []
        for i, h in enumerate(headers):
            align = "r" if i in right else "l"
            cells.append(_pad(h, _c(h, _BOLD), widths[i], align))
        return "  " + "   ".join(cells)

    def fmt_row(plain: list, colored: list) -> str:
        cells = []
        for i in range(len(plain)):
            align = "r" if i in right else "l"
            cells.append(_pad(plain[i], colored[i], widths[i], align))
        return "  " + "   ".join(cells)

    bar = _c("─" * (sum(widths) + 3 * (len(widths) - 1) + 2), _DIM)
    lines = [
        fmt_header(),
        bar,
        *[fmt_row(p, c) for p, c in zip(rows_plain, rows_colored)],
    ]
    return "\n".join(lines)


def _fmt_stats_table(q: SQueue) -> str:
    """Format a partition-breakdown and state-breakdown view for the stats subcommand."""
    lines: List[str] = []

    # --- By Partition --------------------------------------------------------
    by_part = q.jobs_by_partition()
    total_jobs = len(q)
    total_running = sum(1 for j in q if j.is_running)
    total_pending = sum(1 for j in q if j.is_pending)
    total_nodes = sum(j.num_nodes for j in q if j.is_running)
    total_cpus = sum(j.num_cpus for j in q if j.is_running)

    p_rows: list = []
    for part, jobs in by_part.items():
        r = [j for j in jobs if j.is_running]
        p = [j for j in jobs if j.is_pending]
        p_rows.append(
            (
                part,
                len(jobs),
                len(r),
                len(p),
                sum(j.num_nodes for j in r),
                sum(j.num_cpus for j in r),
            )
        )
    p_rows.sort(key=lambda r: (-r[4], -r[2], r[0]))

    p_headers = ["Partition", "Jobs", "Running", "Pending", "Nodes (R)", "CPUs (R)"]
    p_tot = [
        "TOTAL",
        str(total_jobs),
        str(total_running),
        str(total_pending),
        str(total_nodes),
        str(total_cpus),
    ]
    p_str_rows = [
        [r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5])] for r in p_rows
    ]
    p_widths = [
        max(
            len(p_headers[i]),
            len(p_tot[i]),
            max((len(r[i]) for r in p_str_rows), default=0),
        )
        for i in range(len(p_headers))
    ]

    def _ph() -> str:
        cells = [_pad(p_headers[0], _c(p_headers[0], _BOLD), p_widths[0], "l")]
        for i in range(1, len(p_headers)):
            cells.append(_pad(p_headers[i], _c(p_headers[i], _BOLD), p_widths[i], "r"))
        return "  " + "   ".join(cells)

    def _pr(r: list) -> str:
        cells = [_pad(r[0], r[0], p_widths[0], "l")]
        cells.append(_pad(r[1], r[1], p_widths[1], "r"))
        cells.append(
            _pad(r[2], _c(r[2], _GREEN) if r[2] != "0" else r[2], p_widths[2], "r")
        )
        cells.append(
            _pad(r[3], _c(r[3], _YELLOW) if r[3] != "0" else r[3], p_widths[3], "r")
        )
        cells.append(_pad(r[4], r[4], p_widths[4], "r"))
        cells.append(_pad(r[5], r[5], p_widths[5], "r"))
        return "  " + "   ".join(cells)

    def _pt() -> str:
        cells = [_pad(p_tot[0], _c(p_tot[0], _BOLD), p_widths[0], "l")]
        cells.append(_pad(p_tot[1], _c(p_tot[1], _BOLD), p_widths[1], "r"))
        cells.append(_pad(p_tot[2], _c(p_tot[2], _BOLD, _GREEN), p_widths[2], "r"))
        cells.append(_pad(p_tot[3], _c(p_tot[3], _BOLD, _YELLOW), p_widths[3], "r"))
        cells.append(_pad(p_tot[4], _c(p_tot[4], _BOLD), p_widths[4], "r"))
        cells.append(_pad(p_tot[5], _c(p_tot[5], _BOLD), p_widths[5], "r"))
        return "  " + "   ".join(cells)

    p_bar = _c("\u2500" * (sum(p_widths) + 3 * (len(p_widths) - 1) + 2), _DIM)
    lines += [
        _c("By Partition", _BOLD),
        p_bar,
        _ph(),
        p_bar,
        *[_pr(r) for r in p_str_rows],
        p_bar,
        _pt(),
        p_bar,
    ]

    # --- By State ------------------------------------------------------------
    by_state = q.jobs_by_state()
    s_rows = sorted(
        [
            (JOB_STATES.get(code, code), code, len(jobs))
            for code, jobs in by_state.items()
        ],
        key=lambda r: -r[2],
    )
    s_headers = ["State", "Count"]
    s_str_rows = [[r[0], str(r[2])] for r in s_rows]
    s_widths = [
        max(len(s_headers[i]), max((len(r[i]) for r in s_str_rows), default=0))
        for i in range(len(s_headers))
    ]

    def _sh() -> str:
        return (
            "  "
            + _pad(s_headers[0], _c(s_headers[0], _BOLD), s_widths[0], "l")
            + "   "
            + _pad(s_headers[1], _c(s_headers[1], _BOLD), s_widths[1], "r")
        )

    def _sr(state_name: str, state_code: str, count: str) -> str:
        name_c = _color_state(state_name, state_code)
        if state_code in _GREEN_STATES:
            count_c = _c(count, _GREEN)
        elif state_code in _YELLOW_STATES:
            count_c = _c(count, _YELLOW)
        elif state_code in _RED_STATES:
            count_c = _c(count, _RED)
        else:
            count_c = count
        return (
            "  "
            + _pad(state_name, name_c, s_widths[0], "l")
            + "   "
            + _pad(count, count_c, s_widths[1], "r")
        )

    s_bar = _c("\u2500" * (s_widths[0] + s_widths[1] + 5), _DIM)
    lines += [
        "",
        _c("By State", _BOLD),
        s_bar,
        _sh(),
        s_bar,
        *[_sr(s_rows[i][0], s_rows[i][1], r[1]) for i, r in enumerate(s_str_rows)],
        s_bar,
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SLURM accounting (sacct)
# ---------------------------------------------------------------------------

_SACCT_FIELDS = [
    "JobID",
    "User",
    "JobName",
    "State",
    "Partition",
    "AllocNodes",
    "AllocCPUS",
    "Elapsed",
    "CPUTimeRAW",
    "ExitCode",
]
_SACCT_FORMAT = ",".join(_SACCT_FIELDS)

# sacct state -> color bucket (separate from squeue states)
_SACCT_GREEN = {"COMPLETED"}
_SACCT_YELLOW = {"TIMEOUT", "PREEMPTED", "CANCELLED"}
_SACCT_RED = {"FAILED", "NODE_FAIL", "OUT_OF_MEMORY"}


def _normalize_sacct_state(state: str) -> str:
    """Normalize sacct state strings — e.g. 'CANCELLED by 1234' -> 'CANCELLED'."""
    state = state.strip()
    if state.startswith("CANCELLED"):
        return "CANCELLED"
    return state


def _fmt_cpu_hours(hours: float) -> str:
    """Format a CPU-hour value for display."""
    h = int(hours)
    if h >= 1_000_000:
        return f"{h / 1_000_000:.1f}M"
    if h >= 10_000:
        s = str(h)
        # insert thousands separators manually for portability
        parts = []
        while len(s) > 3:
            parts.append(s[-3:])
            s = s[:-3]
        parts.append(s)
        return ",".join(reversed(parts))
    return str(h)


def _color_sacct_state(state: str, text: str) -> str:
    if state in _SACCT_GREEN:
        return _c(text, _GREEN)
    if state in _SACCT_YELLOW:
        return _c(text, _YELLOW)
    if state in _SACCT_RED:
        return _c(text, _RED)
    return text


@dataclass
class SAcctJob:
    """A single job record from SLURM accounting (``sacct``)."""

    job_id: int
    user: str
    name: str
    state: str  # normalized, e.g. "COMPLETED", "FAILED", "CANCELLED"
    partition: str
    num_nodes: int
    num_cpus: int
    elapsed: str  # wall-clock time as HH:MM:SS
    cpu_time_raw: int  # CPU-seconds = AllocCPUS * elapsed_seconds
    exit_code: str  # e.g. "0:0" or "1:0"

    @property
    def cpu_hours(self) -> float:
        return self.cpu_time_raw / 3600.0

    @property
    def is_completed(self) -> bool:
        return self.state == "COMPLETED"

    @property
    def is_failed(self) -> bool:
        return self.state in {"FAILED", "NODE_FAIL", "OUT_OF_MEMORY"}

    @property
    def is_cancelled(self) -> bool:
        return self.state == "CANCELLED"

    @property
    def is_timeout(self) -> bool:
        return self.state == "TIMEOUT"

    def __repr__(self) -> str:
        return (
            f"SAcctJob(job_id={self.job_id}, user={self.user!r}, "
            f"name={self.name!r}, state={self.state!r}, elapsed={self.elapsed!r})"
        )


class SAcct:
    """Interface to SLURM job accounting via ``sacct``.

    Parameters
    ----------
    user : str, optional
        If given, fetch only jobs for this user.
    days : int
        Number of days of history to look back (default: 7).
    partition : str, optional
        If given, filter to this partition.

    Examples
    --------
    >>> a = SAcct(user='alice', days=30)
    >>> a.summary()
    {'total': 42, 'completed': 30, 'failed': 5, ...}
    """

    def __init__(
        self,
        user: Optional[str] = None,
        days: int = 7,
        partition: Optional[str] = None,
    ) -> None:
        self._user = user
        self._days = days
        self._partition = partition
        self._jobs: List[SAcctJob] = []
        self.refresh()

    def refresh(self) -> "SAcct":
        """Re-run ``sacct`` and update the cached job list."""
        start = (datetime.now() - timedelta(days=self._days)).strftime(
            "%Y-%m-%dT00:00:00"
        )
        cmd = [
            "sacct",
            f"--format={_SACCT_FORMAT}",
            "--noheader",
            "--parsable2",
            f"--starttime={start}",
            "--allocations",  # main job entries only, no sub-steps
        ]
        if self._user:
            cmd += ["--user", self._user]
        if self._partition:
            cmd += ["--partition", self._partition]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"sacct failed: {result.stderr.strip()}")

        self._jobs = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) < len(_SACCT_FIELDS):
                continue
            job_id_str = parts[0].strip()
            if not job_id_str or "." in job_id_str:
                continue  # skip job steps (e.g. 12345.batch)
            try:
                self._jobs.append(
                    SAcctJob(
                        job_id=_parse_int(job_id_str),
                        user=parts[1].strip(),
                        name=parts[2].strip(),
                        state=_normalize_sacct_state(parts[3]),
                        partition=parts[4].strip(),
                        num_nodes=_parse_int(parts[5]),
                        num_cpus=_parse_int(parts[6]),
                        elapsed=parts[7].strip(),
                        cpu_time_raw=_parse_int(parts[8]),
                        exit_code=parts[9].strip(),
                    )
                )
            except (ValueError, IndexError):
                continue
        return self

    def jobs(
        self,
        user: Optional[str] = None,
        state: Optional[str] = None,
        partition: Optional[str] = None,
    ) -> List[SAcctJob]:
        """Return accounting records matching the given criteria."""
        result = list(self._jobs)
        if user is not None:
            result = [j for j in result if j.user == user]
        if state is not None:
            result = [j for j in result if j.state == state]
        if partition is not None:
            result = [j for j in result if j.partition == partition]
        return result

    def jobs_by_user(self) -> Dict[str, List[SAcctJob]]:
        """Return a mapping of username -> list of their historical jobs."""
        result: Dict[str, List[SAcctJob]] = {}
        for job in self._jobs:
            result.setdefault(job.user, []).append(job)
        return result

    def jobs_by_state(self) -> Dict[str, List[SAcctJob]]:
        """Return a mapping of state -> list of jobs in that state."""
        result: Dict[str, List[SAcctJob]] = {}
        for job in self._jobs:
            result.setdefault(job.state, []).append(job)
        return result

    def jobs_by_partition(self) -> Dict[str, List[SAcctJob]]:
        """Return a mapping of partition -> list of jobs in that partition."""
        result: Dict[str, List[SAcctJob]] = {}
        for job in self._jobs:
            result.setdefault(job.partition, []).append(job)
        return result

    def summary(self) -> dict:
        """Return a summary dict of job counts and CPU usage.

        Returns
        -------
        dict
            Keys: ``total``, ``completed``, ``failed``, ``cancelled``,
            ``timeout``, ``cpu_hours``, ``by_state``, ``users``.
        """
        by_state = self.jobs_by_state()
        by_user = self.jobs_by_user()
        return {
            "total": len(self._jobs),
            "completed": len(by_state.get("COMPLETED", [])),
            "failed": sum(1 for j in self._jobs if j.is_failed),
            "cancelled": len(by_state.get("CANCELLED", [])),
            "timeout": len(by_state.get("TIMEOUT", [])),
            "cpu_hours": sum(j.cpu_hours for j in self._jobs),
            "by_state": {s: len(jobs) for s, jobs in sorted(by_state.items())},
            "users": {u: len(jobs) for u, jobs in sorted(by_user.items())},
        }

    def __len__(self) -> int:
        return len(self._jobs)

    def __iter__(self):
        return iter(self._jobs)

    def __repr__(self) -> str:
        s = self.summary()
        return (
            f"SAcct(total={s['total']}, completed={s['completed']}, "
            f"failed={s['failed']}, cpu_hours={s['cpu_hours']:.1f})"
        )


def _fmt_history_summary(acct: SAcct) -> str:
    """Per-user summary table — shown when no specific user is requested."""
    by_user = acct.jobs_by_user()
    if not by_user:
        return "  (no jobs found in the requested time window)"

    headers = ["User", "Jobs", "Done", "Failed", "Timeout", "Cancelled", "CPU-hours"]

    rows = []
    for user, jobs in by_user.items():
        done = sum(1 for j in jobs if j.is_completed)
        failed = sum(1 for j in jobs if j.is_failed)
        timeout = sum(1 for j in jobs if j.is_timeout)
        cancelled = sum(1 for j in jobs if j.is_cancelled)
        cpu_h = _fmt_cpu_hours(sum(j.cpu_hours for j in jobs))
        rows.append((user, len(jobs), done, failed, timeout, cancelled, cpu_h))
    rows.sort(key=lambda r: -r[1])  # heaviest users first

    total_done = sum(1 for j in acct if j.is_completed)
    total_failed = sum(1 for j in acct if j.is_failed)
    total_timeout = sum(1 for j in acct if j.is_timeout)
    total_cancelled = sum(1 for j in acct if j.is_cancelled)
    totals_plain = [
        "TOTAL",
        str(len(acct)),
        str(total_done),
        str(total_failed),
        str(total_timeout),
        str(total_cancelled),
        _fmt_cpu_hours(sum(j.cpu_hours for j in acct)),
    ]
    str_rows = [
        [r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5]), r[6]]
        for r in rows
    ]
    widths = [
        max(
            len(headers[i]),
            len(totals_plain[i]),
            max((len(r[i]) for r in str_rows), default=0),
        )
        for i in range(len(headers))
    ]

    def fmt_header() -> str:
        cells = [_pad(headers[0], _c(headers[0], _BOLD), widths[0], "l")]
        for i in range(1, len(headers)):
            cells.append(_pad(headers[i], _c(headers[i], _BOLD), widths[i], "r"))
        return "  " + "   ".join(cells)

    def fmt_row(r: list) -> str:
        cells = [_pad(r[0], r[0], widths[0], "l")]
        cells.append(_pad(r[1], r[1], widths[1], "r"))
        cells.append(
            _pad(r[2], _c(r[2], _GREEN) if r[2] != "0" else r[2], widths[2], "r")
        )
        cells.append(
            _pad(r[3], _c(r[3], _RED) if r[3] != "0" else r[3], widths[3], "r")
        )
        cells.append(
            _pad(r[4], _c(r[4], _YELLOW) if r[4] != "0" else r[4], widths[4], "r")
        )
        cells.append(_pad(r[5], r[5], widths[5], "r"))
        cells.append(_pad(r[6], r[6], widths[6], "r"))
        return "  " + "   ".join(cells)

    def fmt_totals() -> str:
        p = totals_plain
        cells = [_pad(p[0], _c(p[0], _BOLD), widths[0], "l")]
        cells.append(_pad(p[1], _c(p[1], _BOLD), widths[1], "r"))
        cells.append(_pad(p[2], _c(p[2], _BOLD, _GREEN), widths[2], "r"))
        f_c = _BOLD + _RED if p[3] != "0" else _BOLD
        cells.append(_pad(p[3], _c(p[3], f_c), widths[3], "r"))
        t_c = _BOLD + _YELLOW if p[4] != "0" else _BOLD
        cells.append(_pad(p[4], _c(p[4], t_c), widths[4], "r"))
        cells.append(_pad(p[5], _c(p[5], _BOLD), widths[5], "r"))
        cells.append(_pad(p[6], _c(p[6], _BOLD), widths[6], "r"))
        return "  " + "   ".join(cells)

    bar = _c("\u2500" * (sum(widths) + 3 * (len(widths) - 1) + 2), _DIM)
    return "\n".join(
        [fmt_header(), bar, *[fmt_row(r) for r in str_rows], bar, fmt_totals(), bar]
    )


def _fmt_history_detail(acct: SAcct) -> str:
    """Detailed breakdown for a single user — shown when --user is given."""
    if not len(acct):
        return "  (no jobs found in the requested time window)"

    total = len(acct)
    total_cpu = sum(j.cpu_hours for j in acct)
    lines: List[str] = []

    # --- By State ------------------------------------------------------------
    by_state = acct.jobs_by_state()
    s_rows = sorted(
        [
            (s, len(jobs), sum(j.cpu_hours for j in jobs))
            for s, jobs in by_state.items()
        ],
        key=lambda r: -r[1],
    )
    s_tot_plain = ["TOTAL", str(total), "100%", _fmt_cpu_hours(total_cpu)]
    s_str_rows = [
        [r[0], str(r[1]), f"{100 * r[1] // total}%", _fmt_cpu_hours(r[2])]
        for r in s_rows
    ]
    s_headers = ["State", "Jobs", "%", "CPU-hours"]
    s_widths = [
        max(
            len(s_headers[i]),
            len(s_tot_plain[i]),
            max((len(r[i]) for r in s_str_rows), default=0),
        )
        for i in range(len(s_headers))
    ]

    def fmt_s_header() -> str:
        cells = [_pad(s_headers[0], _c(s_headers[0], _BOLD), s_widths[0], "l")]
        for i in range(1, len(s_headers)):
            cells.append(_pad(s_headers[i], _c(s_headers[i], _BOLD), s_widths[i], "r"))
        return "  " + "   ".join(cells)

    def fmt_s_row(state: str, r: list) -> str:
        name_c = _color_sacct_state(state, r[0])
        count_c = _color_sacct_state(state, r[1])
        pct_c = _color_sacct_state(state, r[2])
        cpu_c = _color_sacct_state(state, r[3])
        cells = [
            _pad(r[0], name_c, s_widths[0], "l"),
            _pad(r[1], count_c, s_widths[1], "r"),
            _pad(r[2], pct_c, s_widths[2], "r"),
            _pad(r[3], cpu_c, s_widths[3], "r"),
        ]
        return "  " + "   ".join(cells)

    def fmt_s_totals() -> str:
        p = s_tot_plain
        cells = [_pad(p[0], _c(p[0], _BOLD), s_widths[0], "l")]
        for i in range(1, len(p)):
            cells.append(_pad(p[i], _c(p[i], _BOLD), s_widths[i], "r"))
        return "  " + "   ".join(cells)

    s_bar = _c("\u2500" * (sum(s_widths) + 3 * (len(s_widths) - 1) + 2), _DIM)
    lines += [
        _c("By State", _BOLD),
        s_bar,
        fmt_s_header(),
        s_bar,
        *[fmt_s_row(s_rows[i][0], r) for i, r in enumerate(s_str_rows)],
        s_bar,
        fmt_s_totals(),
        s_bar,
    ]

    # --- By Partition --------------------------------------------------------
    by_part = acct.jobs_by_partition()
    if len(by_part) > 1 or list(by_part.keys()) != [""]:
        p_rows = sorted(
            [
                (p, len(jobs), sum(j.cpu_hours for j in jobs))
                for p, jobs in by_part.items()
            ],
            key=lambda r: -r[2],
        )
        p_str_rows = [[r[0], str(r[1]), _fmt_cpu_hours(r[2])] for r in p_rows]
        p_headers = ["Partition", "Jobs", "CPU-hours"]
        p_widths = [
            max(len(p_headers[i]), max((len(r[i]) for r in p_str_rows), default=0))
            for i in range(len(p_headers))
        ]

        def fmt_p_header() -> str:
            cells = [_pad(p_headers[0], _c(p_headers[0], _BOLD), p_widths[0], "l")]
            for i in range(1, len(p_headers)):
                cells.append(
                    _pad(p_headers[i], _c(p_headers[i], _BOLD), p_widths[i], "r")
                )
            return "  " + "   ".join(cells)

        def fmt_p_row(r: list) -> str:
            cells = [_pad(r[0], r[0], p_widths[0], "l")]
            for i in range(1, len(r)):
                cells.append(_pad(r[i], r[i], p_widths[i], "r"))
            return "  " + "   ".join(cells)

        p_bar = _c("\u2500" * (sum(p_widths) + 3 * (len(p_widths) - 1) + 2), _DIM)
        lines += [
            "",
            _c("By Partition", _BOLD),
            p_bar,
            fmt_p_header(),
            p_bar,
            *[fmt_p_row(r) for r in p_str_rows],
            p_bar,
        ]

    return "\n".join(lines)


# Sort-key functions for the `list --sort` option
_SORT_KEYS = {
    "id": lambda j: j.job_id,
    "user": lambda j: j.user,
    "name": lambda j: j.name,
    "state": lambda j: j.state,
    "partition": lambda j: j.partition,
    "nodes": lambda j: j.num_nodes,
    "cpus": lambda j: j.num_cpus,
    "time": lambda j: j.time_used,
    "priority": lambda j: j.priority,
}


def main() -> None:
    """Entry point for the ``slurm-queue`` command-line tool.

    Sub-commands
    ------------
    show  (default)
        Print a per-user queue summary table.
    list
        Print individual jobs, optionally filtered and sorted.
    stats
        Print partition and state breakdown statistics.
    wait
        Block until matching jobs leave the active queue.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="slurm-queue",
        description="Inspect and wait on the SLURM job queue.",
    )
    sub = parser.add_subparsers(dest="cmd")

    # ---- show ---------------------------------------------------------------
    p_show = sub.add_parser("show", help="Print per-user queue summary (default).")
    p_show.add_argument(
        "--user", "-u", metavar="USER", default=None, help="Filter to this user."
    )
    p_show.add_argument(
        "--partition",
        "-p",
        metavar="PARTITION",
        default=None,
        help="Filter to this partition.",
    )

    # ---- list ---------------------------------------------------------------
    p_list = sub.add_parser("list", help="List individual jobs.")
    p_list.add_argument("--user", "-u", metavar="USER", default=None)
    p_list.add_argument(
        "--partition",
        "-p",
        metavar="PARTITION",
        default=None,
        help="Filter to this partition.",
    )
    p_list.add_argument(
        "--job-name",
        "-n",
        metavar="PATTERN",
        default=None,
        help="Filter by job name (glob patterns supported, e.g. 'train_*').",
    )
    p_list.add_argument(
        "--job-id",
        "-j",
        metavar="ID",
        type=int,
        default=None,
        help="Filter to a specific job ID.",
    )
    p_list.add_argument(
        "--state",
        "-s",
        metavar="STATE",
        default=None,
        help="Filter by state code, e.g. R, PD, CG.",
    )
    p_list.add_argument(
        "--sort",
        "-S",
        metavar="KEY",
        default=None,
        choices=list(_SORT_KEYS),
        help="Sort by: id, user, name, state, partition, nodes, cpus, time, priority.",
    )
    p_list.add_argument(
        "--reverse", "-r", action="store_true", help="Reverse the sort order."
    )
    p_list.add_argument(
        "--reason",
        action="store_true",
        help="Show the scheduling/pending reason column.",
    )

    # ---- stats --------------------------------------------------------------
    p_stats = sub.add_parser(
        "stats", help="Print partition and state breakdown statistics."
    )
    p_stats.add_argument(
        "--user", "-u", metavar="USER", default=None, help="Filter to this user."
    )
    p_stats.add_argument(
        "--partition",
        "-p",
        metavar="PARTITION",
        default=None,
        help="Filter to this partition.",
    )

    # ---- history ------------------------------------------------------------
    p_hist = sub.add_parser(
        "history", help="Show job submission history from accounting records (sacct)."
    )
    p_hist.add_argument(
        "--user",
        "-u",
        metavar="USER",
        default=None,
        help="Show detailed per-state breakdown for this user; omit for all-users summary.",
    )
    p_hist.add_argument(
        "--days",
        "-d",
        metavar="N",
        type=int,
        default=7,
        help="Number of days to look back (default: 7).",
    )
    p_hist.add_argument(
        "--partition",
        "-p",
        metavar="PARTITION",
        default=None,
        help="Filter to this partition.",
    )

    # ---- wait ---------------------------------------------------------------
    p_wait = sub.add_parser(
        "wait", help="Wait until matching jobs leave the active queue."
    )
    p_wait.add_argument(
        "--job-name",
        "-n",
        metavar="PATTERN",
        default=None,
        help="Job name or glob pattern to wait for (e.g. 'train_*').",
    )
    p_wait.add_argument(
        "--job-id",
        "-j",
        metavar="ID",
        type=int,
        default=None,
        help="Wait for a specific job ID.",
    )
    p_wait.add_argument(
        "--user",
        "-u",
        metavar="USER",
        default=None,
        help="Wait for all jobs belonging to this user.",
    )
    p_wait.add_argument(
        "--poll-interval",
        "-i",
        metavar="SECONDS",
        type=float,
        default=30.0,
        help="Seconds between queue polls (default: 30).",
    )
    p_wait.add_argument(
        "--timeout",
        "-t",
        metavar="SECONDS",
        type=float,
        default=None,
        help="Raise an error if jobs are still running after this many seconds.",
    )
    p_wait.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress messages."
    )

    args = parser.parse_args()

    # Default sub-command: show
    if args.cmd is None or args.cmd == "show":
        user = getattr(args, "user", None)
        partition = getattr(args, "partition", None)
        try:
            q = SQueue(user=user, partition=partition)
            print(q)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "list":
        try:
            q = SQueue(user=args.user, partition=args.partition)
            jobs = q.jobs(
                job_name=args.job_name,
                job_id=args.job_id,
                state=args.state,
            )
            if args.sort:
                jobs = sorted(jobs, key=_SORT_KEYS[args.sort], reverse=args.reverse)
            print(_fmt_job_table(jobs, show_reason=args.reason))
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "stats":
        try:
            q = SQueue(user=args.user, partition=args.partition)
            n_running = sum(1 for j in q if j.is_running)
            n_pending = sum(1 for j in q if j.is_pending)
            title_plain = (
                f"SLURM Queue  \u00b7  {len(q)} jobs total"
                f"  \u00b7  {n_running} running"
                f"  \u00b7  {n_pending} pending"
            )
            title = (
                _c("SLURM Queue", _BOLD, _CYAN)
                + "  \u00b7  "
                + f"{len(q)} jobs total"
                + "  \u00b7  "
                + _c(f"{n_running} running", _GREEN)
                + "  \u00b7  "
                + _c(f"{n_pending} pending", _YELLOW)
            )
            print(title)
            print(_c("\u2550" * len(title_plain), _DIM))
            print(_fmt_stats_table(q))
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "history":
        try:
            acct = SAcct(user=args.user, days=args.days, partition=args.partition)
            n = args.days
            day_s = "day" if n == 1 else "days"
            part_s = f"  \u00b7  {args.partition}" if args.partition else ""
            user_s = f"  \u00b7  {args.user}" if args.user else ""
            title_plain = f"Job History  \u00b7  last {n} {day_s}  \u00b7  {len(acct)} jobs{part_s}{user_s}"
            title = (
                _c("Job History", _BOLD, _CYAN)
                + "  \u00b7  "
                + _c(f"last {n} {day_s}", _DIM)
                + "  \u00b7  "
                + f"{len(acct)} jobs"
                + (f"  \u00b7  {args.partition}" if args.partition else "")
                + ("  \u00b7  " + _c(args.user, _BOLD) if args.user else "")
            )
            print(title)
            print(_c("\u2550" * len(title_plain), _DIM))
            if args.user:
                print(_fmt_history_detail(acct))
            else:
                print(_fmt_history_summary(acct))
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
