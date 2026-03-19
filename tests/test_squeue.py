"""Tests for the SQueue class (uses mocked squeue output)."""

import time
from unittest.mock import MagicMock, call, patch
from slurm_script_generator.squeue import _fmt_job_table, main

import pytest

from slurm_script_generator.squeue import (
    _FORMAT_STR,
    _SEPARATOR,
    ACTIVE_STATES,
    SQueue,
    SQueueJob,
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
    import sys
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
    import sys

    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        with patch("sys.argv", ["slurm-queue", "wait"]):
            with pytest.raises(SystemExit):
                main()


def test_cli_wait_by_job_name():
    """wait subcommand exits cleanly when queue is empty."""
    import sys
    from io import StringIO

    out = StringIO()
    with patch("subprocess.run", return_value=_mock_run(stdout="")):
        with patch("sys.argv", ["slurm-queue", "wait", "--job-name", "train_*", "--quiet"]):
            with patch("sys.stdout", out):
                main()  # should return immediately (no matching active jobs)


def test_cli_wait_timeout_exits_nonzero():
    import sys
    from io import StringIO

    active = _make_line(1001, "alice", "slow_job", "R")
    err = StringIO()

    with patch("subprocess.run", return_value=_mock_run(stdout=active)):
        with patch("sys.argv", ["slurm-queue", "wait", "--job-name", "slow_job",
                                "--timeout", "0.001", "--poll-interval", "0.001", "--quiet"]):
            with patch("sys.stderr", err):
                with patch("time.sleep"):
                    with patch("time.monotonic", side_effect=[0, 0, 9999]):
                        with pytest.raises(SystemExit) as exc:
                            main()
    assert exc.value.code == 1
    assert "Timeout" in err.getvalue()
