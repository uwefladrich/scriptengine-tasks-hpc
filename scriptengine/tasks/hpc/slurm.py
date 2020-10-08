import os
import subprocess

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import render as j2render
from scriptengine.exceptions import ScriptEngineStopException, \
                                    ScriptEngineTaskRunError


class Sbatch(Task):

    _required_arguments = ('scripts', )

    @timed_runner
    def run(self, context):

        # Default is to _not_ submit a job if we are already within a batch job
        submit_from_batch_job = False

        # Get all arguments from the task description
        # Almost all arguments are just passed to the 'sbatch' command, except
        # for the 'scripts' and 'submit_from_batch_job', which are used here
        opt_args = []
        for opt, arg in self.__dict__.items():
            if opt == 'scripts':
                if isinstance(arg, list):
                    scripts = [j2render(script, context) for script in arg]
                else:
                    scripts = [j2render(arg, context)]
                self.log_info(f'Submit job for {scripts}')
            elif opt == 'submit_from_batch_job':
                submit_from_batch_job = arg
            elif not opt.startswith('_'):
                opt_args.append(f'--{opt}')
                if arg:
                    opt_args.append(j2render(arg, context))

        # Check if we are within a SLURM batch job and if we want to submit a
        # job from within a job
        if os.environ.get('SLURM_JOB_NAME'):
            if not submit_from_batch_job:
                self.log_debug('Sbatch task from within a SLURM batch job '
                               'and "submit_from_batch_job" is not set or '
                               'false: not submitting new job')
                return

        # Build the sbatch command line
        sbatch_cmd = ['sbatch']
        sbatch_cmd.extend(map(str, opt_args))
        sbatch_cmd.append('se')
        sbatch_cmd.extend(map(str, scripts))

        self.log_debug(f'Sbatch command line: {sbatch_cmd}')

        # Run sbatch command, with handling of errors
        try:
            subprocess.run(sbatch_cmd, check=True)
        except subprocess.CalledProcessError as e:
            msg = f'The sbatch command returns an error: {e}'
            self.log_error(msg)
            raise ScriptEngineTaskRunError(e)
        else:
            raise ScriptEngineStopException(
                    'Sbatch task requests stop after submitting batch job')
