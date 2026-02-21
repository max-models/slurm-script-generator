#!/bin/bash
########################################################
#SBATCH --nodes=2                                      # number of nodes on which to run
#SBATCH --ntasks-per-node=16                           # number of tasks to invoke on each node
#SBATCH --job-name=OLD_JOB_NAME                        # name of job
########################################################
srun ./myprog > prog.out
