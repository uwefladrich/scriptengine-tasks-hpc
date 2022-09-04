Environment module tasks
========================

The ScriptEngine HPC Task package allows interaction with environment modules,
often used on HPC systems to configure the user's environment for installed
software packages. This task package supports the two most common module
implementations: `Lmod` (https://lmod.readthedocs.io) and `Environment Modules`
(https://modules.readthedocs.io).

The ScriptEngine tasks in this package allow modules to be loaded or unloaded in
SE scripts and can thus modify the environment and available software during the
execution of scripts.


Prerequisites
-------------

A fairly recent version of either `Lmod` (source code at
https://github.com/TACC/Lmod) or `Environment modules`
(http://modules.sourceforge.net) is needed. In particular, the module version
should provide Python3 initialisation scripts.

If, however, the module version installed on an HPC system does not provide
Python3 init scripts, it is possible to initialise the tasks from a
user-provided initialisation script. This allows to use the ScriptEngine module
tasks even on systems with an outdated module system. See `The init argument`_
below.


The ``hpc.module`` task
-----------------------

Runs any module command.

Usage::

    - hpc.module:
        cmd: <COMMAND_NAME>
        args: <LIST_OF_ARGS>  # optional

Note that `no checking is done` as to wether the command and arguments are
valid! In particular, there is no guarantee that the command will run given the
particular module implementation (Environment modules or Lmod) and the version
installed on the HPC system. The command name and arguments are passed to the
underlying module system and runtime errors reported via ScriptEngine.

For example::

    - hpc.module:
        cmd: list

will run ``module list`` and write the result to standard output.

If the module command requires arguments, they are given via the task argument
``args``. The arguments have to be specified as a list (even if there is only
one)::

    - hpc.module:
        cmd: show
        args: [ gcc/10.2 ]


The ``hpc.module.load`` task
----------------------------

This task is provided for convenience, as it allows for a shorter syntax to load
modules (compared to the ``hpc.module`` task using ``cmd: load``)

Usage::

    - hpc.module.load:
        names: <MODULE_NAME | LIST_OF_MODULE_NAMES>

Examples::

    - hpc.module.load:
        names:
        - gcc/10.2
        - netcdf/4.3.0


If there is only a single module to be loaded, the name can be given without
using a list::

    - hpc.module.load:
        names: git/2.19.3


The ``init`` argument
---------------------

As mentioned under Prerequisites_, the ``hpc.module`` tasks need Python3
initialisation scripts, usually provided by recent versions of the module
systems. Sometimes, however, older module versions are installed on some HPC
systems and Python3 support is missing. What the ``hpc.module`` scripts really
need is an initialisation script, the rest of the implementation usually works
fine even with older module versions. Hence, it is possible to manually provide
the initialisation scripts.

In order to provide a user defined initialisation script, the ``init`` argument
can be added to any of the module tasks (``hpc.module`` or ``hpc.module.load``).
Since the initialisation is only done once, the ``init`` argument is only needed
at the `first task executed`. If the ``init`` argument is present at any
subsequent task, it is ignored. If the ``init`` argument is missing at the first
executed task (and default initialisation does not work) initialisation will
fail.

The ``init`` argument must specify the path at which the initialisation script
can be found, for example::

    - hpc.module.load:
        init: /home/user/lmod/init/env_modules_python.py 
        names: gcc/10.2

    - hpc.module:
        cmd: list

In order to follow which task is initialising the module system and from what
location, run ScriptEngine with ``se --loglevel debug [...]``.
