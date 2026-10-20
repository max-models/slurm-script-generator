---
title: Installation
description: Install slurm-script-generator from PyPI or from GitHub.
---

From PyPI:

```bash
pip install slurm-script-generator
```

The latest development version, from the `devel` branch:

```bash
pip install git+https://github.com/max-models/slurm-script-generator@devel
```

The package has no dependencies. It installs the command-line tools `generate-slurm-script`,
`slurm-template`, `slurm-alloc`, `slurm-queue`, `slurm-stats`, `slurm-history` and `slurm-wait`,
and the Python package:

```python
from slurm_script_generator.slurm_script import SlurmScript
```

Continue with the [quickstart](/slurm-script-generator/getting-started/quickstart/).
