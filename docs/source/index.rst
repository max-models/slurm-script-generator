
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

   #!/bin/bash
   ##########################################
   #SBATCH --nodes=1                        # number of nodes on which to run
   #SBATCH --ntasks-per-node=16             # number of tasks to invoke on each node
   ##########################################

To save the script to file ``my_script.sh`` use ``--output``:

.. code-block:: bash

   generate-slurm-script --nodes 1 --ntasks-per-node 16 --output my_script.sh

You can also generate scripts in Python programmatically:
 
.. code-block:: python

   from slurm_script_generator.pragmas import Nodes, Ntasks_per_node
   from slurm_script_generator.slurm_script import SlurmScript

   slurm_script = SlurmScript(
      custom_command="srun ./bin > run.out",
   )

   slurm_script.add_pragma(Nodes(value=2))
   slurm_script.add_pragma(Ntasks_per_node(value=16))

Print the generated script to console:

.. code-block:: python

   print(slurm_script)

This will produce:

.. code-block:: bash

   #!/bin/bash
   ##########################################
   #SBATCH --nodes=2                        # number of nodes on which to run
   #SBATCH --ntasks-per-node=16             # number of tasks to invoke on each node
   ##########################################
   srun ./bin > run.out

You can also save the script to file:

   slurm_script.save("my_script.sh")

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   tutorials
   api/index
