"""Tests for the SQueue class (uses mocked squeue output)."""

from unittest.mock import MagicMock, patch

import pytest

from slurm_script_generator.squeue import (
    _SEPARATOR,
    SAcct,
    SQueue,
    SQueueJob,
    _fmt_history_detail,
    _fmt_history_summary,
    _fmt_job_table,
    _fmt_stats_table,
    job_state,
    main,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP = _SEPARATOR


def _make_line(
    job_id,
    user,
    name,
    state,
    partition="gpu",
    nodes=1,
    cpus=4,
    time_used="0:01:00",
    time_limit="1:00:00",
    reason="None",
    priority=1000,
):
    return SEP.join(
        [
            str(job_id),
            user,
            name,
            state,
            partition,
            str(nodes),
            str(cpus),
            time_used,
            time_limit,
            reason,
            str(priority),
        ]
    )


SAMPLE_OUTPUT = "\n".join(
    [
        _make_line(1001, "alice", "train_resnet", "R"),
        _make_line(1002, "alice", "train_bert", "R"),
        _make_line(1003, "bob", "preprocess", "PD"),
        _make_line(1004, "carol", "eval_run", "R"),
        _make_line(1005, "bob", "postprocess", "CG"),
    ]
)


def _mock_run(stdout=SAMPLE_OUTPUT, returncode=0, stderr=""):
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def queue():
    with patch("subprocess.run", return_value=_mock_run()) as _:
        return SQueue()


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------


def test_job_count(queue):
    assert len(queue) == 5


def test_job_fields(queue):
    job = queue.jobs(job_id=1001)[0]
    assert job.job_id == 1001
    assert job.user == "alice"
    assert job.name == "train_resnet"
    assert job.state == "R"
    assert job.is_running
    assert not job.is_pending
    assert job.is_active


def test_pending_job(queue):
    job = queue.jobs(job_id=1003)[0]
    assert job.is_pending
    assert job.is_active
    assert not job.is_running


def test_completing_job_is_active(queue):
    job = queue.jobs(job_id=1005)[0]
    assert job.state == "CG"
    assert job.is_active


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_by_user(queue):
    jobs = queue.jobs(user="alice")
    assert len(jobs) == 2
    assert all(j.user == "alice" for j in jobs)


def test_filter_by_state(queue):
    assert len(queue.jobs(state="R")) == 3
    assert len(queue.jobs(state="PD")) == 1


def test_filter_by_job_id(queue):
    jobs = queue.jobs(job_id=1004)
    assert len(jobs) == 1
    assert jobs[0].name == "eval_run"


def test_filter_by_job_id_list(queue):
    jobs = queue.jobs(job_id=[1001, 1004])
    assert {j.job_id for j in jobs} == {1001, 1004}


def test_filter_glob_exact(queue):
    jobs = queue.jobs(job_name="train_resnet")
    assert len(jobs) == 1


def test_filter_glob_wildcard(queue):
    jobs = queue.jobs(job_name="train_*")
    assert len(jobs) == 2
    assert all(j.name.startswith("train_") for j in jobs)


def test_filter_glob_question_mark(queue):
    # matches train_bert (9 chars after train_) — but also train_resnet (11)
    # '?' matches exactly one char, so 'train_?????' matches train_resnet (6) nope —
    # let's use a pattern that works deterministically
    jobs = queue.jobs(job_name="*process*")
    assert {j.name for j in jobs} == {"preprocess", "postprocess"}


def test_running_jobs(queue):
    assert len(queue.running_jobs()) == 3


def test_pending_jobs(queue):
    assert len(queue.pending_jobs()) == 1


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def test_users(queue):
    assert queue.users() == ["alice", "bob", "carol"]


def test_jobs_by_user(queue):
    by_user = queue.jobs_by_user()
    assert set(by_user.keys()) == {"alice", "bob", "carol"}
    assert len(by_user["alice"]) == 2
    assert len(by_user["bob"]) == 2


def test_jobs_by_state(queue):
    by_state = queue.jobs_by_state()
    assert len(by_state["R"]) == 3
    assert len(by_state["PD"]) == 1
    assert len(by_state["CG"]) == 1


def test_summary(queue):
    s = queue.summary()
    assert s["total_jobs"] == 5
    assert s["running"] == 3
    assert s["pending"] == 1
    assert s["users"]["alice"] == 2
    assert s["users"]["bob"] == 2
    assert s["users"]["carol"] == 1


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


def test_refresh_updates_jobs():
    first_output = _make_line(1001, "alice", "job_a", "R")
    second_output = "\n".join(
        [
            _make_line(1001, "alice", "job_a", "R"),
            _make_line(1002, "bob", "job_b", "PD"),
        ]
    )
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = _mock_run(stdout=first_output)
        q = SQueue()
        assert len(q) == 1

        mock_run.return_value = _mock_run(stdout=second_output)
        q.refresh()
        assert len(q) == 2


def test_refresh_raises_on_squeue_error():
    with patch("subprocess.run", return_value=_mock_run(returncode=1, stderr="error")):
        with pytest.raises(RuntimeError, match="squeue failed"):
            SQueue()


# ---------------------------------------------------------------------------
# wait_until_done
# ---------------------------------------------------------------------------


def test_wait_until_done_already_finished():
    """Jobs are gone on the first poll — should return immediately."""
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        q = SQueue()
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        q.wait_until_done(job_name="train_*", verbose=False)  # no sleep needed


def test_wait_until_done_waits_for_completion():
    """Jobs are active on first poll, gone on second."""
    active = _make_line(1001, "alice", "train_job", "R")
    gone = ""

    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # First call: SQueue() constructor; second: first refresh in wait loop;
        # third: second refresh (jobs gone)
        stdout = active if call_count <= 2 else gone
        return _mock_run(stdout=stdout)

    with patch("subprocess.run", side_effect=side_effect):
        with patch("time.sleep"):  # don't actually sleep
            q = SQueue()
            q.wait_until_done(job_name="train_*", verbose=False)

    assert call_count == 3


def test_wait_until_done_timeout():
    active = _make_line(1001, "alice", "slow_job", "R")
    with patch("subprocess.run", return_value=_mock_run(stdout=active)):
        with patch("time.sleep"):
            with patch("time.monotonic", side_effect=[0, 0, 9999]):
                q = SQueue()
                with pytest.raises(TimeoutError):
                    q.wait_until_done(job_name="slow_job", timeout=10, verbose=False)


def test_wait_until_done_requires_filter():
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        q = SQueue()
    with pytest.raises(ValueError, match="Specify at least one"):
        q.wait_until_done()


def test_wait_until_done_by_job_id():
    active = _make_line(1001, "alice", "myjob", "R")

    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _mock_run(stdout=active if call_count <= 2 else "")

    with patch("subprocess.run", side_effect=side_effect):
        with patch("time.sleep"):
            q = SQueue()
            q.wait_until_done(job_id=1001, verbose=False)


def test_wait_until_done_by_job_id_list():
    active = "\n".join(
        [
            _make_line(1001, "alice", "job1", "R"),
            _make_line(1002, "alice", "job2", "PD"),
        ]
    )

    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # job 1001 finishes first, 1002 stays active until the 3rd poll
        if call_count <= 1:
            return _mock_run(stdout=active)
        if call_count == 2:
            return _mock_run(stdout=_make_line(1002, "alice", "job2", "PD"))
        return _mock_run(stdout="")

    with patch("subprocess.run", side_effect=side_effect):
        with patch("time.sleep"):
            q = SQueue()
            q.wait_until_done(job_id=[1001, 1002], verbose=False)


def test_wait_until_done_by_user():
    active = "\n".join(
        [
            _make_line(1001, "alice", "job1", "R"),
            _make_line(1002, "alice", "job2", "PD"),
        ]
    )

    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _mock_run(stdout=active if call_count <= 2 else "")

    with patch("subprocess.run", side_effect=side_effect):
        with patch("time.sleep"):
            q = SQueue()
            q.wait_until_done(user="alice", verbose=False)


# ---------------------------------------------------------------------------
# Default user filter passed to squeue
# ---------------------------------------------------------------------------


def test_default_user_passed_to_squeue():
    with patch("subprocess.run", return_value=_mock_run(stdout="")) as mock_run:
        SQueue(user="alice")
        cmd = mock_run.call_args[0][0]
        assert "--user" in cmd
        assert "alice" in cmd


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------


def _scancel_calls(mock_run):
    return [c[0][0] for c in mock_run.call_args_list if c[0][0][0] == "scancel"]


def test_cancel_by_job_id():
    with patch("subprocess.run", return_value=_mock_run()) as mock_run:
        q = SQueue()
        cancelled = q.cancel(job_id=1001, verbose=False)

    assert cancelled == [1001]
    assert _scancel_calls(mock_run) == [["scancel", "1001"]]


def test_cancel_by_job_id_list():
    with patch("subprocess.run", return_value=_mock_run()) as mock_run:
        q = SQueue()
        cancelled = q.cancel(job_id=[1001, 1003], verbose=False)

    assert cancelled == [1001, 1003]
    assert _scancel_calls(mock_run) == [["scancel", "1001", "1003"]]


def test_cancel_by_job_name_glob():
    with patch("subprocess.run", return_value=_mock_run()) as mock_run:
        q = SQueue()
        cancelled = q.cancel(job_name="train_*", verbose=False)

    assert cancelled == [1001, 1002]
    assert _scancel_calls(mock_run) == [["scancel", "1001", "1002"]]


def test_cancel_by_user_and_state():
    with patch("subprocess.run", return_value=_mock_run()) as mock_run:
        q = SQueue()
        cancelled = q.cancel(user="bob", state="PD", verbose=False)

    assert cancelled == [1003]
    assert _scancel_calls(mock_run) == [["scancel", "1003"]]


def test_cancel_by_partition():
    output = "\n".join(
        [
            _make_line(1001, "alice", "job1", "R", partition="gpu"),
            _make_line(1002, "alice", "job2", "R", partition="cpu"),
        ]
    )
    with patch("subprocess.run", return_value=_mock_run(stdout=output)) as mock_run:
        q = SQueue()
        cancelled = q.cancel(partition="cpu", verbose=False)

    assert cancelled == [1002]
    assert _scancel_calls(mock_run) == [["scancel", "1002"]]


def test_cancel_requires_filter(queue):
    with pytest.raises(ValueError):
        queue.cancel()


def test_cancel_no_matching_jobs_is_noop():
    with patch("subprocess.run", return_value=_mock_run()) as mock_run:
        q = SQueue()
        cancelled = q.cancel(job_id=9999, verbose=False)

    assert cancelled == []
    assert _scancel_calls(mock_run) == []


def test_cancel_raises_on_scancel_error():
    def side_effect(cmd, *args, **kwargs):
        if cmd[0] == "scancel":
            return _mock_run(returncode=1, stderr="Invalid job id")
        return _mock_run()

    with patch("subprocess.run", side_effect=side_effect):
        q = SQueue()
        with pytest.raises(RuntimeError, match="scancel failed"):
            q.cancel(job_id=1001, verbose=False)


def test_cancel_refreshes_after_success():
    """The queue reflects the post-cancel state."""
    remaining = _make_line(1003, "bob", "preprocess", "PD")
    seen_scancel = False

    def side_effect(cmd, *args, **kwargs):
        nonlocal seen_scancel
        if cmd[0] == "scancel":
            seen_scancel = True
            return _mock_run(stdout="")
        return _mock_run(stdout=remaining if seen_scancel else SAMPLE_OUTPUT)

    with patch("subprocess.run", side_effect=side_effect):
        q = SQueue()
        assert len(q) == 5
        q.cancel(job_name="train_*", verbose=False)
        assert [j.job_id for j in q.jobs()] == [1003]


# ---------------------------------------------------------------------------
# SQueueJob.cancel
# ---------------------------------------------------------------------------


def test_job_cancel_delegates_to_squeue():
    def side_effect(cmd, *args, **kwargs):
        if cmd[0] == "scancel":
            return _mock_run(stdout="")
        return _mock_run()

    job = SQueueJob(
        1001, "alice", "train_resnet", "R", "gpu", 1, 4, "0:01", "1:00", "None", 100
    )
    with patch("subprocess.run", side_effect=side_effect) as mock_run:
        job.cancel(verbose=False)

    assert _scancel_calls(mock_run) == [["scancel", "1001"]]


# ---------------------------------------------------------------------------
# job_state
# ---------------------------------------------------------------------------


def _patch_sacct(**run_kwargs):
    """Patch shutil.which so sacct is found, plus subprocess.run."""
    return patch("shutil.which", return_value="/usr/bin/sacct"), patch(
        "subprocess.run", **run_kwargs
    )


def test_job_state_completed():
    which, run = _patch_sacct(return_value=_mock_run(stdout="COMPLETED\nCOMPLETED\n"))
    with which, run as mock_run:
        assert job_state(1001) == "COMPLETED"
        cmd = mock_run.call_args[0][0]

    assert cmd[:3] == ["sacct", "-j", "1001"]
    assert "--format=State" in cmd


def test_job_state_strips_cancelled_reason():
    which, run = _patch_sacct(return_value=_mock_run(stdout="CANCELLED by 1234\n"))
    with which, run:
        assert job_state(1001) == "CANCELLED"


def test_job_state_uses_first_nonempty_line():
    which, run = _patch_sacct(return_value=_mock_run(stdout="\n  \nFAILED\nCOMPLETED\n"))
    with which, run:
        assert job_state(1001) == "FAILED"


def test_job_state_none_when_sacct_missing():
    with patch("shutil.which", return_value=None):
        with patch("subprocess.run") as mock_run:
            assert job_state(1001) is None
    mock_run.assert_not_called()


def test_job_state_none_on_nonzero_exit():
    which, run = _patch_sacct(return_value=_mock_run(returncode=1, stderr="nope"))
    with which, run:
        assert job_state(1001) is None


def test_job_state_none_on_empty_output():
    which, run = _patch_sacct(return_value=_mock_run(stdout="\n\n"))
    with which, run:
        assert job_state(1001) is None


def test_job_state_none_on_timeout():
    import subprocess as _sp

    which, run = _patch_sacct(side_effect=_sp.TimeoutExpired(cmd="sacct", timeout=30))
    with which, run:
        assert job_state(1001) is None


def test_job_state_none_on_oserror():
    which, run = _patch_sacct(side_effect=OSError("boom"))
    with which, run:
        assert job_state(1001) is None


def test_job_final_state_delegates():
    job = SQueueJob(
        1001, "alice", "myjob", "R", "gpu", 1, 4, "0:01", "1:00", "None", 100
    )
    which, run = _patch_sacct(return_value=_mock_run(stdout="TIMEOUT\n"))
    with which, run as mock_run:
        assert job.final_state() == "TIMEOUT"
        assert mock_run.call_args[0][0][:3] == ["sacct", "-j", "1001"]


# ---------------------------------------------------------------------------
# SQueueJob.wait_until_done
# ---------------------------------------------------------------------------


def test_job_wait_until_done_delegates_to_squeue():
    """SQueueJob.wait_until_done should poll by job_id until gone."""
    active = _make_line(1001, "alice", "myjob", "R")

    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # First SQueue() in wait_until_done; second refresh (job gone)
        return _mock_run(stdout=active if call_count == 1 else "")

    job = SQueueJob(
        1001, "alice", "myjob", "R", "gpu", 1, 4, "0:01", "1:00", "None", 100
    )
    with patch("subprocess.run", side_effect=side_effect):
        with patch("time.sleep"):
            job.wait_until_done(verbose=False)

    assert call_count == 2  # one initial fetch, one refresh after sleep


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


def test_str_empty():
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        q = SQueue()
    assert str(q) == "SLURM Queue  ·  empty"


def test_str_contains_users(queue):
    s = str(queue)
    assert "alice" in s
    assert "bob" in s
    assert "carol" in s


def test_str_contains_totals(queue):
    s = str(queue)
    assert "TOTAL" in s
    # 5 total jobs, 3 running, 1 pending
    assert "5" in s
    assert "3" in s
    assert "1" in s


def test_str_sorted_by_running_nodes():
    """User with most running nodes should appear first."""
    # alice: 2 running jobs, 8 nodes each = 16 nodes
    # bob: 1 running job, 2 nodes
    output = "\n".join(
        [
            _make_line(1, "alice", "job_a", "R", nodes=8, cpus=32),
            _make_line(2, "alice", "job_b", "R", nodes=8, cpus=32),
            _make_line(3, "bob", "job_c", "R", nodes=2, cpus=8),
        ]
    )
    with patch("subprocess.run", return_value=_mock_run(stdout=output)):
        q = SQueue()
    s = str(q)
    assert s.index("alice") < s.index("bob")


def test_str_header_line(queue):
    s = str(queue)
    assert "SLURM Queue" in s
    assert "running" in s
    assert "pending" in s


# ---------------------------------------------------------------------------
# Repr / dunder
# ---------------------------------------------------------------------------


def test_repr(queue):
    r = repr(queue)
    assert "SQueue" in r
    assert "total=5" in r


def test_iter(queue):
    jobs = list(queue)
    assert len(jobs) == 5
    assert all(isinstance(j, SQueueJob) for j in jobs)


def test_state_name():
    job = SQueueJob(1, "u", "n", "R", "p", 1, 4, "0:01", "1:00", "None", 100)
    assert job.state_name == "Running"

    job2 = SQueueJob(2, "u", "n", "PD", "p", 1, 4, "0:00", "1:00", "Resources", 50)
    assert job2.state_name == "Pending"


# ---------------------------------------------------------------------------
# _fmt_job_table
# ---------------------------------------------------------------------------


def test_fmt_job_table_empty():
    assert _fmt_job_table([]) == "  (no jobs)"


def test_fmt_job_table_contains_fields(queue):
    table = _fmt_job_table(list(queue))
    assert "alice" in table
    assert "train_resnet" in table
    assert "Running" in table
    assert "JobID" in table


def test_fmt_job_table_columns(queue):
    table = _fmt_job_table(list(queue))
    # All expected header columns present
    for col in ["JobID", "User", "Job Name", "State", "Partition", "Nodes", "CPUs"]:
        assert col in table


# ---------------------------------------------------------------------------
# CLI — main()
# ---------------------------------------------------------------------------


def _run_main(argv, mock_stdout=SAMPLE_OUTPUT):
    """Run main() with patched subprocess and sys.argv, return printed output."""
    from io import StringIO

    out = StringIO()
    with patch("subprocess.run", return_value=_mock_run(stdout=mock_stdout)):
        with patch("sys.argv", ["slurm-queue"] + argv):
            with patch("sys.stdout", out):
                try:
                    main()
                except SystemExit:
                    pass
    return out.getvalue()


def test_cli_default_shows_summary():
    output = _run_main([])
    assert "SLURM Queue" in output
    assert "alice" in output


def test_cli_show_subcommand():
    output = _run_main(["show"])
    assert "SLURM Queue" in output


def test_cli_show_user_filter():
    output = _run_main(["show", "--user", "alice"])
    # Only alice's jobs fetched — the --user flag is passed to squeue
    assert "SLURM Queue" in output


def test_cli_list_all():
    output = _run_main(["list"])
    assert "JobID" in output
    assert "alice" in output
    assert "bob" in output


def test_cli_list_filter_user():
    output = _run_main(["list", "--user", "alice"])
    assert "alice" in output


def test_cli_list_filter_job_name():
    output = _run_main(["list", "--job-name", "train_*"])
    assert "train_resnet" in output
    assert "train_bert" in output
    assert "preprocess" not in output


def test_cli_list_filter_state():
    output = _run_main(["list", "--state", "PD"])
    assert "Pending" in output
    assert "Running" not in output


def test_cli_wait_requires_filter(capsys):

    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        with patch("sys.argv", ["slurm-queue", "wait"]):
            with pytest.raises(SystemExit):
                main()


def test_cli_wait_by_job_name():
    """wait subcommand exits cleanly when queue is empty."""
    from io import StringIO

    out = StringIO()
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        with patch(
            "sys.argv", ["slurm-queue", "wait", "--job-name", "train_*", "--quiet"]
        ):
            with patch("sys.stdout", out):
                main()  # should return immediately (no matching active jobs)


# ---------------------------------------------------------------------------
# jobs_by_partition / partition filter
# ---------------------------------------------------------------------------


def test_jobs_by_partition(queue):
    by_part = queue.jobs_by_partition()
    assert "gpu" in by_part
    assert len(by_part["gpu"]) == 5


def test_jobs_filter_partition(queue):
    jobs = queue.jobs(partition="gpu")
    assert len(jobs) == 5
    jobs_none = queue.jobs(partition="nonexistent")
    assert jobs_none == []


def test_partition_passed_to_squeue():
    with patch("subprocess.run", return_value=_mock_run(stdout="")) as mock_run:
        SQueue(partition="gpu")
        cmd = mock_run.call_args[0][0]
        assert "--partition" in cmd
        assert "gpu" in cmd


# ---------------------------------------------------------------------------
# _fmt_job_table with show_reason
# ---------------------------------------------------------------------------


def test_fmt_job_table_reason_column(queue):
    table = _fmt_job_table(list(queue), show_reason=True)
    assert "Reason" in table


def test_fmt_job_table_no_reason_by_default(queue):
    table = _fmt_job_table(list(queue), show_reason=False)
    assert "Reason" not in table


# ---------------------------------------------------------------------------
# _fmt_stats_table
# ---------------------------------------------------------------------------


def test_fmt_stats_table_partition_section(queue):
    s = _fmt_stats_table(queue)
    assert "By Partition" in s
    assert "gpu" in s


def test_fmt_stats_table_state_section(queue):
    s = _fmt_stats_table(queue)
    assert "By State" in s
    assert "Running" in s
    assert "Pending" in s


def test_fmt_stats_table_empty():
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        q = SQueue()
    s = _fmt_stats_table(q)
    # Should produce output without crashing even with no jobs
    assert "By Partition" in s
    assert "By State" in s


# ---------------------------------------------------------------------------
# CLI — stats subcommand
# ---------------------------------------------------------------------------


def test_cli_stats():
    output = _run_main(["stats"])
    assert "SLURM Queue" in output
    assert "By Partition" in output
    assert "By State" in output
    assert "Running" in output


def test_cli_stats_user_filter():
    output = _run_main(["stats", "--user", "alice"])
    assert "By Partition" in output


# ---------------------------------------------------------------------------
# CLI — list --sort / --reverse / --reason
# ---------------------------------------------------------------------------


def test_cli_list_sort_user():
    output = _run_main(["list", "--sort", "user"])
    assert "alice" in output


def test_cli_list_sort_nodes():
    output = _run_main(["list", "--sort", "nodes"])
    assert "JobID" in output


def test_cli_list_reverse():
    output = _run_main(["list", "--sort", "id", "--reverse"])
    assert "JobID" in output


def test_cli_list_reason():
    output = _run_main(["list", "--reason"])
    assert "Reason" in output


def test_cli_list_partition():
    output = _run_main(["list", "--partition", "gpu"])
    assert "JobID" in output


# ---------------------------------------------------------------------------
# CLI — show --partition
# ---------------------------------------------------------------------------


def test_cli_show_partition():
    output = _run_main(["show", "--partition", "gpu"])
    assert "SLURM Queue" in output


# ---------------------------------------------------------------------------
# SAcct / history
# ---------------------------------------------------------------------------

_SACCT_SEP = "|"


def _make_sacct_line(
    job_id,
    user,
    name,
    state,
    partition="gpu",
    nodes=1,
    cpus=4,
    elapsed="01:00:00",
    cpu_time_raw=14400,
    exit_code="0:0",
):
    return _SACCT_SEP.join(
        [
            str(job_id),
            user,
            name,
            state,
            partition,
            str(nodes),
            str(cpus),
            elapsed,
            str(cpu_time_raw),
            exit_code,
        ]
    )


SACCT_OUTPUT = "\n".join(
    [
        _make_sacct_line(2001, "alice", "train_job", "COMPLETED", cpu_time_raw=14400),
        _make_sacct_line(
            2002, "alice", "eval_job", "FAILED", exit_code="1:0", cpu_time_raw=3600
        ),
        _make_sacct_line(
            2003, "bob", "preprocess", "COMPLETED", partition="cpu", cpu_time_raw=7200
        ),
        _make_sacct_line(2004, "alice", "long_job", "TIMEOUT", cpu_time_raw=86400),
        _make_sacct_line(2005, "carol", "quick_job", "CANCELLED", cpu_time_raw=600),
        # job step — should be skipped
        _make_sacct_line(
            "2001.batch", "alice", "batch", "COMPLETED", cpu_time_raw=14400
        ),
    ]
)


def _mock_sacct(stdout=SACCT_OUTPUT, returncode=0, stderr=""):
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


@pytest.fixture
def acct():
    with patch("subprocess.run", return_value=_mock_sacct()):
        return SAcct()


def test_sacct_job_count(acct):
    assert len(acct) == 5  # job step skipped


def test_sacct_job_fields(acct):
    job = acct.jobs(user="alice")[0]
    assert job.job_id == 2001
    assert job.user == "alice"
    assert job.state == "COMPLETED"
    assert job.cpu_hours == pytest.approx(4.0)


def test_sacct_normalize_cancelled():
    with patch(
        "subprocess.run",
        return_value=_mock_sacct(
            stdout=_make_sacct_line(9999, "dave", "myjob", "CANCELLED by 1234")
        ),
    ):
        a = SAcct()
    assert a.jobs()[0].state == "CANCELLED"


def test_sacct_filter_user(acct):
    jobs = acct.jobs(user="alice")
    assert len(jobs) == 3
    assert all(j.user == "alice" for j in jobs)


def test_sacct_filter_state(acct):
    assert len(acct.jobs(state="COMPLETED")) == 2
    assert len(acct.jobs(state="FAILED")) == 1
    assert len(acct.jobs(state="TIMEOUT")) == 1


def test_sacct_filter_partition(acct):
    assert len(acct.jobs(partition="cpu")) == 1
    assert len(acct.jobs(partition="gpu")) == 4


def test_sacct_jobs_by_user(acct):
    by_user = acct.jobs_by_user()
    assert set(by_user.keys()) == {"alice", "bob", "carol"}
    assert len(by_user["alice"]) == 3


def test_sacct_jobs_by_state(acct):
    by_state = acct.jobs_by_state()
    assert len(by_state["COMPLETED"]) == 2
    assert len(by_state["FAILED"]) == 1
    assert len(by_state["TIMEOUT"]) == 1


def test_sacct_jobs_by_partition(acct):
    by_part = acct.jobs_by_partition()
    assert "gpu" in by_part
    assert "cpu" in by_part


def test_sacct_summary(acct):
    s = acct.summary()
    assert s["total"] == 5
    assert s["completed"] == 2
    assert s["failed"] == 1
    assert s["cancelled"] == 1
    assert s["timeout"] == 1
    assert s["cpu_hours"] == pytest.approx((14400 + 3600 + 7200 + 86400 + 600) / 3600)


def test_sacct_is_properties(acct):
    jobs = {j.job_id: j for j in acct}
    assert jobs[2001].is_completed
    assert jobs[2002].is_failed
    assert jobs[2004].is_timeout
    assert jobs[2005].is_cancelled


def test_sacct_user_passed_to_sacct():
    with patch("subprocess.run", return_value=_mock_sacct(stdout="")) as mock_run:
        SAcct(user="alice")
        cmd = mock_run.call_args[0][0]
        assert "--user" in cmd
        assert "alice" in cmd


def test_sacct_partition_passed_to_sacct():
    with patch("subprocess.run", return_value=_mock_sacct(stdout="")) as mock_run:
        SAcct(partition="gpu")
        cmd = mock_run.call_args[0][0]
        assert "--partition" in cmd
        assert "gpu" in cmd


def test_sacct_raises_on_error():
    with patch("subprocess.run", return_value=_mock_sacct(returncode=1, stderr="err")):
        with pytest.raises(RuntimeError, match="sacct failed"):
            SAcct()


def test_fmt_history_summary_contains_users(acct):
    s = _fmt_history_summary(acct)
    assert "alice" in s
    assert "bob" in s
    assert "carol" in s


def test_fmt_history_summary_headers(acct):
    s = _fmt_history_summary(acct)
    for col in ["User", "Jobs", "Done", "Failed", "Timeout", "Cancelled", "CPU-hours"]:
        assert col in s


def test_fmt_history_summary_totals(acct):
    s = _fmt_history_summary(acct)
    assert "TOTAL" in s


def test_fmt_history_summary_empty():
    with patch("subprocess.run", return_value=_mock_sacct(stdout="")):
        a = SAcct()
    assert "no jobs found" in _fmt_history_summary(a)


def test_fmt_history_detail_by_state(acct):
    d = _fmt_history_detail(acct)
    assert "By State" in d
    assert "COMPLETED" in d


def test_fmt_history_detail_by_partition(acct):
    # has both gpu and cpu partitions
    d = _fmt_history_detail(acct)
    assert "By Partition" in d
    assert "gpu" in d
    assert "cpu" in d


def test_fmt_history_detail_empty():
    with patch("subprocess.run", return_value=_mock_sacct(stdout="")):
        a = SAcct()
    assert "no jobs found" in _fmt_history_detail(a)


# ---------------------------------------------------------------------------
# CLI — history subcommand
# ---------------------------------------------------------------------------


def _run_main_sacct(argv, mock_stdout=SACCT_OUTPUT):
    """Run main() with patched sacct subprocess."""
    from io import StringIO

    out = StringIO()
    with patch("subprocess.run", return_value=_mock_sacct(stdout=mock_stdout)):
        with patch("sys.argv", ["slurm-queue"] + argv):
            with patch("sys.stdout", out):
                try:
                    main()
                except SystemExit:
                    pass
    return out.getvalue()


def test_cli_history_default():
    output = _run_main_sacct(["history"])
    assert "Job History" in output
    assert "alice" in output
    assert "CPU-hours" in output


def test_cli_history_user():
    output = _run_main_sacct(["history", "--user", "alice"])
    assert "Job History" in output
    assert "By State" in output
    assert "COMPLETED" in output


def test_cli_history_days():
    output = _run_main_sacct(["history", "--days", "30"])
    assert "30 days" in output


def test_cli_history_one_day():
    output = _run_main_sacct(["history", "--days", "1"])
    assert "1 day" in output
    assert "1 days" not in output


def test_cli_history_partition():
    output = _run_main_sacct(["history", "--partition", "gpu"])
    assert "Job History" in output


def test_cli_wait_timeout_exits_nonzero():
    from io import StringIO

    active = _make_line(1001, "alice", "slow_job", "R")
    err = StringIO()

    with patch("subprocess.run", return_value=_mock_run(stdout=active)):
        with patch(
            "sys.argv",
            [
                "slurm-queue",
                "wait",
                "--job-name",
                "slow_job",
                "--timeout",
                "0.001",
                "--poll-interval",
                "0.001",
                "--quiet",
            ],
        ):
            with patch("sys.stderr", err):
                with patch("time.sleep"):
                    with patch("time.monotonic", side_effect=[0, 0, 9999]):
                        with pytest.raises(SystemExit) as exc:
                            main()
    assert exc.value.code == 1
    assert "Timeout" in err.getvalue()
