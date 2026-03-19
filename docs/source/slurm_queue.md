# slurm-queue CLI

The `slurm-queue` command lets you inspect the SLURM job queue and wait for
jobs to finish — all from the terminal.

``` bash
slurm-queue [show]                  # per-user summary (default)
slurm-queue list   [filters]        # per-job table
slurm-queue wait   [filters]        # block until jobs are done
```

---

## show — queue summary

Running `slurm-queue` with no arguments (or with the explicit `show`
subcommand) prints a per-user summary of the current queue, sorted by
heaviest users first (running nodes, then running jobs):

``` bash
slurm-queue
# or equivalently:
slurm-queue show
```

    SLURM Queue  ·  42 jobs total  ·  30 running  ·  12 pending
    ════════════════════════════════════════════════════════════════════
      User    Jobs   Running   Pending   Nodes (R)   CPUs (R)
    ────────────────────────────────────────────────────────────────────
      alice     20        18         2          36        576
      bob       15        10         5          20        320
      carol      7         2         5           4         64
    ────────────────────────────────────────────────────────────────────
      TOTAL     42        30        12          60        960
    ════════════════════════════════════════════════════════════════════

`Nodes (R)` and `CPUs (R)` count only **running** jobs — pending jobs have
not yet been allocated resources.

Restrict the view to a single user with `--user` / `-u`:

``` bash
slurm-queue show --user alice
slurm-queue show -u alice
```

---

## list — per-job table

The `list` subcommand prints one row per job:

``` bash
slurm-queue list
```

      JobID   User    Job Name         State     Partition   Nodes   CPUs   Used        Limit
      ───────────────────────────────────────────────────────────────────────────────────────────
       1001   alice   train_resnet     Running   gpu             2     64   2:13:05     24:00:00
       1002   alice   train_bert       Running   gpu             2     64   1:07:22     24:00:00
       1003   bob     preprocess       Pending   cpu             1      8   0:00:00      2:00:00
       1004   carol   eval_run         Running   gpu             1     32   0:44:11      8:00:00
       1005   bob     postprocess      Completing gpu            1      8   1:02:30      2:00:00

### Filtering

Filter by **user**:

``` bash
slurm-queue list --user alice
slurm-queue list -u alice
```

Filter by **job name** (glob patterns supported):

``` bash
slurm-queue list --job-name "train_*"
slurm-queue list -n "train_*"
```

Filter by **job ID**:

``` bash
slurm-queue list --job-id 1001
slurm-queue list -j 1001
```

Filter by **state** (SLURM state codes):

``` bash
slurm-queue list --state PD    # pending jobs only
slurm-queue list -s R          # running jobs only
```

Filters can be combined:

``` bash
slurm-queue list --user alice --state R
```

Common state codes:

| Code | Meaning    |
|------|------------|
| `R`  | Running    |
| `PD` | Pending    |
| `CG` | Completing |
| `F`  | Failed     |
| `CD` | Completed  |
| `CA` | Cancelled  |
| `TO` | Timeout    |

---

## wait — block until jobs finish

The `wait` subcommand polls the queue and blocks until all matching jobs
leave the active queue (i.e. are no longer running, pending, completing,
etc.).

### Wait by job name

Glob patterns (`*`, `?`) are supported:

``` bash
slurm-queue wait --job-name "train_*"
slurm-queue wait -n "train_resnet"
```

    Waiting — 2 job(s) still active [1001, 1002]. Polling again in 30.0s.
    Waiting — 1 job(s) still active [1002]. Polling again in 30.0s.
    All matching jobs have finished.

### Wait by job ID

``` bash
slurm-queue wait --job-id 1001
slurm-queue wait -j 1001
```

### Wait for all jobs from a user

``` bash
slurm-queue wait --user alice
slurm-queue wait -u alice
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--poll-interval SECONDS` | `-i` | `30` | Seconds between queue polls |
| `--timeout SECONDS` | `-t` | none | Exit with error if jobs are still running after this many seconds |
| `--quiet` | `-q` | off | Suppress progress messages |

Set a custom poll interval and timeout:

``` bash
slurm-queue wait --job-name "train_*" --poll-interval 60 --timeout 3600
```

Suppress output (e.g. in scripts):

``` bash
slurm-queue wait --user alice --quiet
```

If `--timeout` is exceeded, `slurm-queue` prints an error to stderr and
exits with code **1**:

    Timeout: Timed out after 3600.0s. Still active job IDs: [1002]

---

## Global options

`--user` / `-u` can also be passed before the subcommand to restrict **all**
`squeue` calls to that user (useful when you only care about your own jobs):

``` bash
slurm-queue --user alice
slurm-queue --user alice list --state PD
```

---

## Use in shell scripts

Because `slurm-queue wait` blocks and returns a non-zero exit code on
timeout, it composes naturally in shell pipelines:

``` bash
# Submit a job, then wait for it to finish before running post-processing
sbatch my_job.sh
slurm-queue wait --job-name my_job --quiet && python analyse_results.py
```
