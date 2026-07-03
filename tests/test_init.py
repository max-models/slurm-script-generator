from slurm_script_generator import SAcct, SAcctJob, SlurmScript, SQueue, SQueueJob
from slurm_script_generator.slurm_script import SlurmScript as ModuleSlurmScript
from slurm_script_generator.squeue import SAcct as ModuleSAcct
from slurm_script_generator.squeue import SAcctJob as ModuleSAcctJob
from slurm_script_generator.squeue import SQueue as ModuleSQueue
from slurm_script_generator.squeue import SQueueJob as ModuleSQueueJob


def test_package_exports_core_classes():
    assert SlurmScript is ModuleSlurmScript
    assert SQueue is ModuleSQueue
    assert SQueueJob is ModuleSQueueJob
    assert SAcct is ModuleSAcct
    assert SAcctJob is ModuleSAcctJob
