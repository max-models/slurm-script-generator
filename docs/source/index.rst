
slurm-script-generator Documentation
====================================


.. code-block:: bash

   pip install slurm-script-generator


Generate scripts
----------------

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

To save the script to file ``my_script.sh`` use ``--output``:

.. code-block:: bash

   generate-slurm-script --nodes 1 --ntasks-per-node 16 --output my_script.sh

You can also generate scripts in Python programmatically:

.. code-block:: python

   from slurm_script_generator.slurm_script import SlurmScript

   slurm_script = SlurmScript(
      nodes=2,
      ntasks_per_core=16,
      custom_commands=[
         "# Run simulation",
         "srun ./bin > run.out",
      ],
   )

Print the generated script to console:

.. code-block:: python

   print(slurm_script)

This will produce:

.. code-block:: bash

   #!/bin/bash
   ########################################################
   #            This script was generated using           #
   #             slurm-script-generator v0.3.0            #
   # https://github.com/max-models/slurm-script-generator #
   #      `pip install slurm-script-generator==0.3.0`     #
   ########################################################

   ########################################################
   # Pragmas for Core Node And Task Allocation            #
   #SBATCH --nodes=2                                      # number of nodes on which to run
   #                                                      #
   # Pragmas for Cpu Topology And Binding                 #
   #SBATCH --ntasks-per-core=16                           # number of tasks to invoke on each core
   ########################################################
   # Run simulation
   srun ./bin > run.out

You can also save the script to file:

   slurm_script.save("my_script.sh")

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   tutorials
   api/index
