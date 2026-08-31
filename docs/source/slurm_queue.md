# slurm-queue CLI

`slurm-queue`, `slurm-stats`, `slurm-history`, and `slurm-wait` are terminal
tools for inspecting the SLURM job queue, viewing per-user and per-partition
statistics, querying job history, and blocking until jobs finish — all
without writing a custom `squeue` or `sacct` one-liner.

```bash
slurm-queue   [filters]  # one row per job (default); --summary for per-user totals
slurm-stats   [filters]  # partition and state breakdown
slurm-history [filters]  # accounting history via sacct
slurm-wait    [filters]  # block until jobs are done
```

---

## slurm-queue — per-job table

Running `slurm-queue` with no arguments prints one row per job:

```bash
slurm-queue
```

```
  JobID   User    Job Name         State       Partition   Nodes   CPUs   Used        Limit
  ─────────────────────────────────────────────────────────────────────────────────────────
   1001   alice   train_resnet     Running     gpu             2     64   2:13:05     24:00:00
   1002   alice   train_bert       Running     gpu             2     64   1:07:22     24:00:00
   1003   bob     preprocess       Pending     cpu             1      8   0:00:00      2:00:00
   1004   carol   eval_run         Running     gpu             1     32   0:44:11      8:00:00
   1005   bob     postprocess      Completing  gpu             1      8   1:02:30      2:00:00
```

### Filtering

Filter by user, partition, job name (glob patterns supported), job ID, or
state — any combination works:

```bash
slurm-queue --user alice
slurm-queue --me                      # shortcut for --user <your username>
slurm-queue --partition gpu
slurm-queue --job-name "train_*"      # glob pattern
slurm-queue --job-id 1001
slurm-queue --state PD                # pending only
slurm-queue --user alice --state R    # alice's running jobs
```

`--user` and `--me` are mutually exclusive.

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

### Sorting

Sort the output by any field with `--sort` / `-S`:

```bash
slurm-queue --sort nodes          # fewest nodes first
slurm-queue --sort nodes --reverse  # most nodes first
slurm-queue --sort time           # least time used first
slurm-queue --user alice --sort priority --reverse
```

Available sort keys: `id`, `user`, `name`, `state`, `partition`, `nodes`,
`cpus`, `time`, `priority`.

### Pending reason

Add `--reason` to show why each job is waiting (very useful for debugging
stuck jobs):

```bash
slurm-queue --state PD --reason
```

```
  JobID   User    Job Name     State     Partition   Nodes   CPUs   Used       Limit      Reason
  ─────────────────────────────────────────────────────────────────────────────────────────────────────
   1003   bob     preprocess   Pending   cpu             1      8   0:00:00   2:00:00    Resources
   1006   dave    eval         Pending   gpu             2     64   0:00:00   8:00:00    Priority
```

### Per-user summary

Add `--summary` for a per-user summary instead of the per-job table, sorted
by heaviest users first (running nodes, then running jobs):

```bash
slurm-queue --summary
slurm-queue --summary --user alice
slurm-queue --summary --me                  # shortcut for --user <your username>
slurm-queue --summary --partition gpu
```

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
```

`Nodes (R)` and `CPUs (R)` count only **running** jobs — pending jobs have not
yet been allocated resources.

### Cancelling jobs

Add `--cancel` to cancel the matching jobs instead of listing them. At least
one filter is required, so a bare `slurm-queue --cancel` refuses to run
rather than cancelling the whole queue:

```bash
slurm-queue --job-name "sweep_*" --cancel   # prompts for confirmation
slurm-queue --job-id 1001 --cancel --yes    # skip the prompt
slurm-queue --me --state PD --cancel        # cancel your own pending jobs
```

The matching jobs are printed first, then you're prompted to confirm unless
`--yes`/`-y` is given:

```
  JobID   User    Job Name     State     Partition   Nodes   CPUs   Used       Limit
  ─────────────────────────────────────────────────────────────────────────────────
   1006   alice   sweep_lr01   Pending   gpu             1     16   0:00:00   4:00:00
   1007   alice   sweep_lr02   Pending   gpu             1     16   0:00:00   4:00:00
Cancel 2 job(s) above? [y/N]
```

---

## slurm-stats — partition and state breakdown

`slurm-stats` shows how the queue is distributed across partitions and
states — useful for spotting overloaded partitions or accumulating failures:

```bash
slurm-stats
slurm-stats --user alice
slurm-stats --me                 # shortcut for --user <your username>
slurm-stats --partition gpu
```

```
SLURM Queue  ·  42 jobs total  ·  30 running  ·  12 pending
══════════════════════════════════════════════════════════════
By Partition
──────────────────────────────────────────────────────────────
  Partition    Jobs   Running   Pending   Nodes (R)   CPUs (R)
──────────────────────────────────────────────────────────────
  gpu            35        28         7          56        896
  cpu             7         2         5           4         32
──────────────────────────────────────────────────────────────
  TOTAL          42        30        12          60        928
──────────────────────────────────────────────────────────────

By State
────────────────────
  State       Count
────────────────────
  Running        30
  Pending        12
────────────────────
```

### Per-user highlights

Filtering to a single user (`--user`/`--me`) adds extra detail beyond the
partition/state tables: their longest-running job, their longest-waiting
pending job, and a breakdown of their jobs by name — handy for checking on
what a specific user (yourself or someone else) has going on:

```bash
slurm-stats --user alice
slurm-stats --me
```

```
Longest running:  train_resnet (#1001)  —  2:13:05 elapsed on gpu
Longest waiting:  sweep_lr03 (#1009)  —  waiting 00:42:10, reason: Priority

By Job Name
──────────────────────────────────
  Job Name     Jobs   Running   Pending
──────────────────────────────────
  train_*         2         2         0
  sweep_*         3         0         3
──────────────────────────────────
```

---

## slurm-history — job accounting

`slurm-history` queries `sacct` to show completed, failed, and cancelled
jobs from recent history. It shows CPU-hours consumed alongside job counts,
making it easy to spot which users or experiments used the most compute.

```bash
slurm-history                      # all users, last 7 days
slurm-history --days 30            # last 30 days
slurm-history --user alice         # detailed breakdown for alice
slurm-history --me                 # detailed breakdown for the current user
slurm-history --partition gpu      # filter to GPU partition
```

**All-users summary** (no `--user`):

```
Job History  ·  last 7 days  ·  87 jobs
══════════════════════════════════════════════════════════════════════
  User     Jobs   Done   Failed   Timeout   Cancelled   CPU-hours
──────────────────────────────────────────────────────────────────────
  alice      45     40        3         1           1       3,240
  bob        30     25        2         2           1       1,800
  carol      12     12        0         0           0         540
──────────────────────────────────────────────────────────────────────
  TOTAL      87     77        5         3           2       5,580
──────────────────────────────────────────────────────────────────────
```

**Single-user detail** (`--user alice`):

```
Job History  ·  last 7 days  ·  45 jobs  ·  alice
══════════════════════════════════════════════════
By State
──────────────────────────────────────────────────
  State        Jobs    %   CPU-hours
──────────────────────────────────────────────────
  COMPLETED      40   89%      3,100
  FAILED          3    7%         80
  TIMEOUT         1    2%         60
  CANCELLED       1    2%          0
──────────────────────────────────────────────────
  TOTAL          45  100%      3,240
──────────────────────────────────────────────────

By Partition
──────────────────────────────
  Partition   Jobs   CPU-hours
──────────────────────────────
  gpu           40      3,100
  cpu            5        140
──────────────────────────────
```

> **Note:** `sacct` only returns data for jobs you own unless you have SLURM
> operator or admin privileges. Querying another user's history requires
> elevated SLURM permissions on the cluster.

---

## slurm-wait — block until jobs finish

`slurm-wait` polls the queue and blocks until all matching jobs leave
the active queue (running, pending, completing, etc.). It is designed to be
used in shell scripts and Python workflows.

### Wait by job name (glob patterns supported)

```bash
slurm-wait --job-name "train_*"
slurm-wait -n "train_resnet"
```

```
~ Waiting — 2 job(s) still active [1001, 1002]. Polling again in 30.0s.
~ Waiting — 1 job(s) still active [1002]. Polling again in 30.0s.
✓ All matching jobs have finished.
```

### Wait by job ID

```bash
slurm-wait --job-id 1001
slurm-wait -j 1001
```

### Wait for all jobs from a user

```bash
slurm-wait --user alice
slurm-wait -u alice
slurm-wait --me           # shortcut for --user <your username>
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--poll-interval SECONDS` | `-i` | `30` | Seconds between queue polls |
| `--timeout SECONDS` | `-t` | none | Exit with error after this many seconds |
| `--quiet` | `-q` | off | Suppress progress messages |

```bash
# Poll every 60 s, give up after 2 hours
slurm-wait --job-name "train_*" --poll-interval 60 --timeout 7200

# Silent — useful in automation scripts
slurm-wait --user alice --quiet
```

If `--timeout` is exceeded, `slurm-wait` prints to stderr and exits with
code `1`:

```
Timeout: Timed out after 7200.0s. Still active job IDs: [1002]
```

---

## Use in shell scripts

`slurm-wait` blocks and exits non-zero on timeout, so it composes
naturally in shell pipelines:

```bash
# Submit, wait, post-process
sbatch train.sh
slurm-wait --job-name train --quiet && python analyse.py

# Submit a batch, wait for all, then clean up
for config in small medium large; do
    sbatch --job-name "sweep_${config}" train.sh
done
slurm-wait --job-name "sweep_*" && echo "All sweeps done"
```

---

## Python API

All the functionality above is available as a Python API. See the
[Queue Management & History tutorial](tutorials/02_queue_and_history) for
comprehensive examples covering:

- Inspecting and filtering the live queue
- Submitting a parameter sweep and waiting for results
- Analysing job history with `SAcct`
- End-to-end workflow from script generation to completion
