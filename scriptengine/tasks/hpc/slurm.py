import os
import sys
import subprocess

from scriptengine.tasks.core import Task, timed_runner
from scriptengine.jinja import render as j2render
from scriptengine.exceptions import ScriptEngineStopException, \
                                    ScriptEngineTaskRunError


_JOB_VAR = 'SLURM_JOB_NAME'
_SUBMIT_CMD = 'sbatch'


def is_batch_job():
    return os.environ.get(_JOB_VAR) is not None


class Sbatch(Task):

    @timed_runner
    def run(self, context):

        # No recursive job submission by default: check if we're already in a job
        if is_batch_job() and not self.getarg('submit_from_batch_job', default=False):
            self.log_debug(
                f'{self.__class__.__name__} task from within a batch '
                'job and "submit_from_batch_job" is not set or false: '
                'not submitting new job'
            )
            return

        # Append all opts,args that should go to the submit command to a list
        opt_args = []
        for opt, arg in self.__dict__.items():
            if opt in ('scripts', 'submit_from_batch_job') or opt.startswith('_'):
                continue
            opt_args.append(f'--{opt}')
            if arg:
                opt_args.append(j2render(arg, context))

        # Build the submit command line
        submit_cmd = [_SUBMIT_CMD]
        submit_cmd.extend(map(str, opt_args))
        scripts = self.getarg('scripts', default=None)
        if scripts:
            submit_cmd.append('se')
            submit_cmd.extend(
                map(str, scripts if isinstance(scripts, list) else [scripts])
            )
        else:
            # If no scripts were given, use the original SE command line
            submit_cmd.extend(sys.argv)
        self.log_debug(f'Command line for submitting job: {submit_cmd}')

        # Run submit command, with handling of errors
        try:
            subprocess.run(submit_cmd, check=True)
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
