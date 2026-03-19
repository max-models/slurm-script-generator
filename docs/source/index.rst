
slurm-script-generator Documentation
====================================


.. code-block:: bash

   pip install slurm-script-generator


Quickstart
----------

Generate a slurm script to ``slurm_script.sh`` with:

.. code-block:: bash

   generate-slurm-script --nodes 1 --ntasks-per-node 16

This will produce:

.. code-block:: bash

   !/bin/bash
   ########################################################
   #            This script was generated using           #
   #             slurm-script-generator v0.3.0            #
   # https://github.com/max-models/slurm-script-generator #
   #      `pip install slurm-script-generator==0.3.0`     #
   ########################################################

   ########################################################
   # Pragmas for Core Node And Task Allocation            #
   #SBATCH --nodes=1                                      # number of nodes on which to run
   #SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
   ########################################################

Check out the pages below for more detailed documentation on the Command Line Interface, the Python API, and some tutorials to get you started!

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   cli.md
   tutorials
   slurm_queue.md
   api/index
