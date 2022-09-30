import os
import subprocess
import sys

from scriptengine.context import ContextUpdate
from scriptengine.exceptions import ScriptEngineStopException, ScriptEngineTaskRunError
from scriptengine.jinja import render as j2render
from scriptengine.tasks.core import Task, timed_runner

_JOB_VAR = "SLURM_JOB_NAME"
_SBATCH_CMD = "sbatch"


class Sbatch(Task):
    @timed_runner
    def run(self, context):
        def in_batch_job():
            return os.environ.get(_JOB_VAR) is not None

        def do_recursive_submit():
            return self.getarg(
                "submit_from_batch_job",
                context,
                default=False,
            )

        def is_sbatch_opt(opt):
            return opt not in (
                "scripts",
                "hetjob_spec",
                "stop_after_submit",
                "submit_from_batch_job",
                "set_jobid",
            ) and not opt.startswith("_")

        if in_batch_job() and not do_recursive_submit():
            self.log_debug(
                "Already running within a batch job and "
                '"submit_from_batch_job" is not set or false - '
                "not submitting new job"
            )
            return

        # Start building the sbatch command line
        sbatch_cmd_line = [_SBATCH_CMD]

        sbatch_general_args = ["--parsable"]
        for opt, arg in self.__dict__.items():
            if is_sbatch_opt(opt):
                sbatch_general_args.append(f"--{opt}")
                if arg:
                    sbatch_general_args.append(j2render(arg, context))
        sbatch_cmd_line.extend(map(str, sbatch_general_args))

        hetjob_spec = self.getarg("hetjob_spec", context, default=[])
        if hetjob_spec:
            self.log_debug("Submiting hetereogeneous SLURM job with sbatch")
            sbatch_hetjob_args = []
            for job_args in hetjob_spec:
                if len(sbatch_hetjob_args) > 0:
                    sbatch_hetjob_args.append(":")
                for opt, arg in job_args.items():
                    sbatch_hetjob_args.append(f"--{opt}")
                    if arg:
                        sbatch_hetjob_args.append(j2render(arg, context))
            sbatch_cmd_line.extend(map(str, sbatch_hetjob_args))

        scripts = self.getarg("scripts", context, default=None)
        if scripts:
            sbatch_cmd_line.append("se")
            sbatch_cmd_line.extend(
                map(
                    str,
                    scripts if isinstance(scripts, list) else [scripts],
                )
            )
        else:
            # If no scripts were given, use the original SE command line
            sbatch_cmd_line.extend(sys.argv)
        self.log_debug(f"SLURM sbatch command line: {sbatch_cmd_line}")

        self.log_info("Submitting job to SLURM queue")

        # Run sbatch command, with handling of errors
        try:
            p = subprocess.run(sbatch_cmd_line, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.log_error(f"SLURM sbatch error: {e}")
            raise ScriptEngineTaskRunError

        try:
            jobid = int(p.stdout.decode())
        except ValueError:
            self.log_warning(
                "Job submitted to SLURM queue, but JOBID could not be parsed "
                f"from stdout: '{p.stdout.decode()}'"
            )
            jobid = None
        else:
            self.log_info(f"Job submitted to SLURM queue, JOBID is {jobid}")

        if self.getarg("stop_after_submit", context, default=True):
            self.log_info("Request STOP after job submission with SLURM sbatch")
            raise ScriptEngineStopException
        else:
            self.log_info(
                "Job submitted but no stop requested (stop_after_submit=False)"
            )

        set_jobid = self.getarg("set_jobid", context, default=False)
        if set_jobid:
            if jobid:
                return ContextUpdate({set_jobid: jobid})
            else:
                self.log_error(
                    "Setting the JOBID was requested, but JOBID could not be parsed"
                )
                raise ScriptEngineTaskRunError
