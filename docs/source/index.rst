slurm-script-generator
======================

A Python library and command-line toolkit for generating, managing, and
monitoring SLURM jobs.

Install with pip:

.. code-block:: bash

   pip install slurm-script-generator

---

Quickstart
----------

**Generate a SLURM script from the command line:**

.. code-block:: bash

   generate-slurm-script --nodes 2 --ntasks-per-node 16 --job-name my_job --output-path job.sh

**Or from Python:**

.. code-block:: python

   from slurm_script_generator.slurm_script import SlurmScript

   script = SlurmScript(
       job_name="my_job",
       nodes=2,
       ntasks_per_node=16,
       time="04:00:00",
       custom_commands=["srun ./myprog > output.txt"],
   )
   script.save("job.sh")

**Submit and wait for it to finish:**

.. code-block:: python

   import subprocess
   from slurm_script_generator.squeue import SQueue

   result = subprocess.run(["sbatch", "job.sh"], capture_output=True, text=True, check=True)
   job_id = int(result.stdout.strip().split()[-1])

   states = SQueue().wait_until_done(job_id=job_id)
   # {12345: 'COMPLETED'}

``wait_until_done`` returns the final accounting state of every job it waited on.
Pass ``check=True`` to turn a failed job into an exception:

.. code-block:: python

   SQueue().wait_until_done(job_name="train_*", check=True)
   # RuntimeError: Job(s) did not complete successfully: 12346=FAILED

**Check how a job ended:**

.. code-block:: python

   from slurm_script_generator.squeue import job_state, job_states

   state = job_state(job_id)          # 'COMPLETED', 'FAILED', 'TIMEOUT', ...
   if state == "FAILED":
       raise RuntimeError(f"job {job_id} failed")

   job_states([12345, 12346])         # one sacct call for many jobs
   # {12345: 'COMPLETED', 12346: 'FAILED'}

Both return ``None`` for a job whose state cannot be determined (no accounting
configured, ``sacct`` missing, or the job not yet recorded) — treat that as
"unknown", not as a failure. That is also why ``check=True`` ignores such jobs.

**Cancel jobs:**

.. code-block:: python

   from slurm_script_generator.squeue import SQueue

   q = SQueue()
   q.cancel(job_id=job_id)          # a single job (or a list of IDs)
   q.cancel(job_name="train_*")     # every job matching a glob
   q.cancel(user="alice", state="PD")  # only alice's pending jobs

**Get an interactive allocation from a batch script:**

.. code-block:: bash

   slurm-alloc job.sh              # salloc with the script's resource request
   slurm-alloc job.sh --run        # run the script's commands in the allocation
   slurm-alloc job.sh --dry-run    # just print the salloc command
   slurm-alloc job.sh -- --x11     # pass extra arguments to salloc

Options that ``salloc`` does not accept (``--output``, ``--array``, …) are
skipped and reported on stderr.

**Inspect the live queue:**

.. code-block:: bash

   slurm-queue              # per-user summary
   slurm-queue list         # one row per job
   slurm-queue stats        # partition and state breakdown
   slurm-queue history      # job accounting (sacct)

---

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   cli.md
   slurm_queue.md
   tutorials
   slurm_queue.md
   tutorials
   api/index
