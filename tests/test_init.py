from slurm_script_generator import SAcct, SAcctJob, SQueue, SQueueJob, SlurmScript
from slurm_script_generator.slurm_script import SlurmScript as ModuleSlurmScript
from slurm_script_generator.squeue import (
    SAcct as ModuleSAcct,
    SAcctJob as ModuleSAcctJob,
    SQueue as ModuleSQueue,
    SQueueJob as ModuleSQueueJob,
)


def test_package_exports_core_classes():
    assert SlurmScript is ModuleSlurmScript
    assert SQueue is ModuleSQueue
    assert SQueueJob is ModuleSQueueJob
    assert SAcct is ModuleSAcct
    assert SAcctJob is ModuleSAcctJob
