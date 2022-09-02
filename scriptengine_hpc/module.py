import os
from pathlib import Path

from scriptengine.tasks.core import Task, timed_runner
from scriptengine.exceptions import ScriptEngineTaskRunError

_DEFAULT_LMOD_ENVVAR = "LMOD_DIR"
_DEFAULT_ENV_MOD_PATH = Path("/usr/share/Modules")


def module_from_init_file(path):
    exec_vars = dict()
    try:
        exec(path.read_text(), exec_vars)
    except FileNotFoundError as e:
        raise RuntimeError(f"Could not initialise environment modules: {e}") from None

    if "module" in exec_vars:
        return exec_vars["module"]

    raise RuntimeError(
        "Could not initialise environment modules: Initialisation script does not define 'module' function"
    )


def module_from_lmod(lmod_path=None):
    """Returns 'module' function or None
    Lmod implementation, see
    https://lmod.readthedocs.io
    https://github.com/TACC/Lmod
    """
    if lmod_path:
        lmod_path = Path(lmod_path)
    elif _DEFAULT_LMOD_ENVVAR in os.environ:
        lmod_path = Path(os.environ[_DEFAULT_LMOD_ENVVAR]).parent
    else:
        return None
    return module_from_init_file(lmod_path / "init/env_modules_python.py")


def module_from_environment_modules(env_mod_path=None):
    """Returns 'module' function or None
    Implementation for Environment modules, see
    https://modules.readthedocs.io
    http://modules.sourceforge.net
    """
    if env_mod_path:
        env_mod_path = Path(env_mod_path)
    elif _DEFAULT_ENV_MOD_PATH.exists():
        env_mod_path = _DEFAULT_ENV_MOD_PATH
    else:
        return None
    return module_from_init_file(env_mod_path / "init/python.py")


class Module(Task):

    _required_arguments = ("cmd",)

    def __init__(self, arguments):
        Module.check_arguments(arguments)
        super().__init__(arguments)
        self._mod_func = None

    @timed_runner
    def run(self, context):
        self.log_info("Execute module command")

        init = self.getarg("init", default=None)
        cmd = self.getarg("cmd", context)
        args = self.getarg("args", default=[])

        self.log_debug(
            f"Run module cmd '{cmd}' with args {args} (initialised from '{init}')"
        )

        if not self._mod_func:
            self.log_debug("Initialising module system")
            try:
                mod_func = module_from_lmod(init) or module_from_environment_modules()
            except Exception as e:
                self.log_error(f"Error initialising the module system: {e}")
                raise ScriptEngineTaskRunError
            if not mod_func:
                self.log_error("Error initialising the module system")
                raise ScriptEngineTaskRunError

        try:
            mod_func(cmd, *args)
        except Exception as e:
            self.log_error(f"Error while running module command: {e}")
            raise ScriptEngineTaskRunError
