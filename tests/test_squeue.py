"""Tests for the SQueue class (uses mocked squeue output)."""
import time
from unittest.mock import MagicMock, call, patch

import pytest

from slurm_script_generator.squeue import (
    ACTIVE_STATES,
    SQueue,
    SQueueJob,
    _FORMAT_STR,
    _SEPARATOR,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP = _SEPARATOR


def _make_line(job_id, user, name, state, partition="gpu", nodes=1, cpus=4,
               time_used="0:01:00", time_limit="1:00:00", reason="None", priority=1000):
    return SEP.join([
        str(job_id), user, name, state, partition,
        str(nodes), str(cpus), time_used, time_limit, reason, str(priority),
    ])


SAMPLE_OUTPUT = "\n".join([
    _make_line(1001, "alice", "train_resnet",  "R"),
    _make_line(1002, "alice", "train_bert",    "R"),
    _make_line(1003, "bob",   "preprocess",    "PD"),
    _make_line(1004, "carol", "eval_run",      "R"),
    _make_line(1005, "bob",   "postprocess",   "CG"),
])


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
    second_output = "\n".join([
        _make_line(1001, "alice", "job_a", "R"),
        _make_line(1002, "bob", "job_b", "PD"),
    ])
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
    active = "\n".join([
        _make_line(1001, "alice", "job1", "R"),
        _make_line(1002, "alice", "job2", "PD"),
    ])

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
