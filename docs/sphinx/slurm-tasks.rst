SLURM tasks
===========

Support for the SLURM workload manager.


The ``hpc.slurm.sbatch`` task
-----------------------------

This task allows to send ScriptEngine jobs to SLURM queues by providing the
functionallity of the SLURM ``sbatch`` command to ScriptEngine scripts. The
usage pattern is::

    - hpc.slurm.sbatch:
        scripts: <SE_SCRIPT | LIST_OF_SE_SCRIPTS>  # optional
        hetjob_spec: <LIST_OF_SBATCH_OPTIONS>  # optional
        submit_from_sbatch: <true | false>  # optional, default False
        stop_after_submit:  <true | false>  # optional, default True

        <SBATCH_OPTIONS>  # optional


The main usage principle of ``hpc.slurm.sbatch`` is that a new batch job is
created and sent into a SLURM queue. Once SLURM executes the job, one or more
ScriptEngine scripts are run.

There are two ways to specify which scripts are run in the batch job. By default
(no ``script`` argument is given), the batch job runs the script(s) given on the
``se`` command line. For example, if the following script (assumed name
``sbatch.yml``)::

    - hpc.slurm.sbatch:
        account: <MY_SLURM_ACCOUNT>
        time: !noparse 0:10:00

    - base.echo:
        msg: Hello world, from batch job!

is run with ``se batch.yml``, a batch job will be queued, which eventually
writes "Hello world, from batch job!" to the default job logfile. Using this
default will be the desired behavior in most use cases. However, it is possible
to have the batch job run a different script (or scripts) and not the initiall
one, by specifying one or more other ScriptEngine scripts with the ``scripts``
arguments. More than one scripts have to specified as a list.

Most of the ``hpc.slurm.sbatch`` arguments will be passed right through to the
``sbatch`` command. Thus, in the above example, the command executed under the
hood is::

    sbatch --account MY_SLURM_ACCOUNT --time 0:10:00 se sbatch.yml

Only few arguments are processed by the ``hpc.slurm.sbatch`` task itself, see
the usage pattern above. Thus, it is possible to use any ``sbatch`` argument, as
long as they are valid long arguments (i.e. with the double dash syntax).  Note
that `no checking is done` for validity of the ``sbatch`` arguments and options!

An important principle of ``hpc.slurm.sbatch`` is that on the initial execution,
it will stop the processing of the current script once the batch job is queued.
Hence, when the above example script is run, a job is put in the batch queue
(first task), but the ``base.echo`` task is not executed. When the script is run
(again) from within the batch job, the ``hpc.slurm.sbatch`` task detects that it
is in a batch job and does nothing. Therefore, the following echo task is run as
part of the job.

Again, this behavior will be appropriate in most use cases. The script is run
until the sbatch task, a job is queued and processing stops. Once the job is
running, ``hpc.slurm.sbatch`` does nothing and all other tasks are run.

Sometimes, though, it makes sense to submit a batch job even if the current
script already runs in a batch job itself. For example, one may want to queue a
follow-on job at the end of the script. In order to do this, one needs to set::
    
    - hpc.slurm.sbatch:
        [...]
        submit_from_sbatch: true
        [...]

If ``submit_from_sbatch`` is set to ``true`` a new job is queued, even if the
current script is itself running in a batch job on its own.

A related switch is ``stop_after_submit``, which defaults to ``True``. If it is
set to ``False`` the script will continue after a new SLURM job was submitted.
If ``stop_after_submit`` is not explicitly set (or set to ``True``) the scripte
execution will be stopped, as described above.


SLURM Heterogeneous Job Support
-------------------------------

The ``hpc.slurm.sbatch`` task support submitting `heterogeneous SLURM jobs
<https://slurm.schedmd.com/heterogeneous_jobs.html>`_ by providing the
``hetjob_spec`` option::

    - hpc.slurm.sbatch:
        - time: 10
        - hetjob_spec:
            - nodes: 1
            - nodes: 2

    - base.command:
        name: srun
        args: [
            -l,
            --ntasks, 1, /usr/bin/hostname, ':',
            --ntasks, 10, --ntasks-per-node, 5, /usr/bin/hostname
        ]

In this example, a heterogeneous job with two components is submitted to SLURM,
the first requesting one node and the second two nodes. The ``srun`` command in
the second task of the script starts executables on this allocated nodes while
specifying further job characteristigs (such as the number of tasks and tasks
per node).

The ``hetjob_spec`` argument takes a list of dictionaries and passes the keys of
each dictionary on to ``sbatch`` as specification for each respective component
of the heterogeneous job. Note that in the example above, each dictionary
contains only one key-value pair, the number of requested nodes.
