import os
import sys
import subprocess

from scriptengine.tasks.core import Task, timed_runner
from scriptengine.jinja import render as j2render
from scriptengine.exceptions import ScriptEngineStopException, \
                                    ScriptEngineTaskRunError


_JOB_VAR = 'SLURM_JOB_NAME'
_SBATCH_CMD = 'sbatch'


class Sbatch(Task):

    @timed_runner
    def run(self, context):

        def in_batch_job():
            return os.environ.get(_JOB_VAR) is not None

        def do_recursive_submit():
            return self.getarg(
                'submit_from_batch_job',
                context,
                default=False,
            )

        def is_sbatch_opt(opt):
            return opt not in (
                'scripts',
                'submit_from_batch_job',
                'hetjob_spec',
            ) and not opt.startswith('_')

        if in_batch_job() and not do_recursive_submit():
            self.log_debug(
                'Already running within a batch job and '
                '"submit_from_batch_job" is not set or false - '
                'not submitting new job'
            )
            return

        # Start building the sbatch command line
        sbatch_cmd_line = [_SBATCH_CMD]

        sbatch_general_args = []
        for opt, arg in self.__dict__.items():
            if is_sbatch_opt(opt):
                sbatch_general_args.append(f'--{opt}')
                if arg:
                    sbatch_general_args.append(j2render(arg, context))
        sbatch_cmd_line.extend(map(str, sbatch_general_args))

        hetjob_spec = self.getarg('hetjob_spec', context, default=[])
        if hetjob_spec:
            self.log_debug('Submitting a hetereogeneous SLURM job with SBATCH')
            sbatch_hetjob_args = []
            for job_args in hetjob_spec:
                if len(sbatch_hetjob_args) > 0:
                    sbatch_hetjob_args.append(':')
                for opt, arg in job_args.items():
                    sbatch_hetjob_args.append(f'--{opt}')
                    if arg:
                        sbatch_hetjob_args.append(j2render(arg, context))
            sbatch_cmd_line.extend(map(str, sbatch_hetjob_args))

        scripts = self.getarg('scripts', context, default=None)
        if scripts:
            sbatch_cmd_line.append('se')
            sbatch_cmd_line.extend(
                map(
                    str,
                    scripts if isinstance(scripts, list) else [scripts],
                )
            )
        else:
            # If no scripts were given, use the original SE command line
            sbatch_cmd_line.extend(sys.argv)
        self.log_debug(f'Command line for submitting job: {sbatch_cmd_line}')

        # Run sbatch command, with handling of errors
        try:
            subprocess.run(sbatch_cmd_line, check=True)
        except subprocess.CalledProcessError as e:
            self.log_error(
                f'Submit command returns error: {e}'
            )
            raise ScriptEngineTaskRunError
        else:
            self.log_info(
                'Requesting stop after submitting batch job to SLURM'
            )
            raise ScriptEngineStopException
