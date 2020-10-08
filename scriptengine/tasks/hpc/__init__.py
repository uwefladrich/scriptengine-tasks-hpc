"""ScriptEngine HPC tasks

This module provides a ScriptEngine task set with tasks useful on
High-Performance Computing (HPC) systems
"""

from .slurm import Sbatch


def task_loader_map():
    return {
        'sbatch': Sbatch,
        }
