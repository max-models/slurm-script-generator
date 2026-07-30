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

   SQueue().wait_until_done(job_id=job_id)

**Cancel jobs:**

.. code-block:: python

   from slurm_script_generator.squeue import SQueue

   q = SQueue()
   q.cancel(job_id=job_id)          # a single job (or a list of IDs)
   q.cancel(job_name="train_*")     # every job matching a glob
   q.cancel(user="alice", state="PD")  # only alice's pending jobs

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
