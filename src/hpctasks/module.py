import os
from pathlib import Path

from scriptengine.exceptions import ScriptEngineTaskRunError
from scriptengine.tasks.core import Task, timed_runner

_DEFAULT_LMOD_ENVVAR = "LMOD_DIR"
_DEFAULT_ENV_MOD_PATH = Path("/usr/share/Modules")


def modfunc_from_ini_script(init_script):
    try:
        ini_script_code = init_script.read_text()
    except FileNotFoundError as e:
        raise RuntimeError(f"Init script not found: {e}")
    exec_globals = dict()
    try:
        exec(ini_script_code, exec_globals)
    except Exception as e:
        raise RuntimeError(f"Init script error: {e}")
    try:
        return exec_globals["module"]
    except KeyError:
        raise RuntimeError("Init script does not define 'module' function")


def modfunc_from_lmod(lmod_init_script=None):
    """Returns 'module' function or None
    Lmod implementation, see
    https://lmod.readthedocs.io
    https://github.com/TACC/Lmod
    """
    if lmod_init_script:
        lmod_init_script = Path(lmod_init_script)
    elif _DEFAULT_LMOD_ENVVAR in os.environ:
        lmod_init_script = (
            Path(os.environ[_DEFAULT_LMOD_ENVVAR]).parent / "init/env_modules_python.py"
        )
    else:
        return None
    return modfunc_from_ini_script(lmod_init_script)


def modfunc_from_environment_modules(env_mod_init_script=None):
    """Returns 'module' function or None
    Implementation for Environment modules, see
    https://modules.readthedocs.io
    http://modules.sourceforge.net
    """
    if env_mod_init_script:
        env_mod_init_script = Path(env_mod_init_script)
    elif _DEFAULT_ENV_MOD_PATH.exists():
        env_mod_init_script = _DEFAULT_ENV_MOD_PATH / "init/python.py"
    else:
        return None
    return modfunc_from_ini_script(env_mod_init_script)


class Module(Task):
    """hpc.module"""

    _required_arguments = ("cmd",)
    _module_func = None

    def __init__(self, arguments):
        Module.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        self.log_info("Execute module command")

        cmd = self.getarg("cmd", context)
        args = self.getarg("args", context, default=[])
        self.log_debug(f"Run module cmd '{cmd}' with args {args}")

        if not Module._module_func:
            init = self.getarg("init", context, default=None)
            self.log_debug(
                f"Module system not yet initialised. Initialising from '{init}'"
            )
            try:
                Module._module_func = modfunc_from_lmod(
                    init
                ) or modfunc_from_environment_modules(init)
            except RuntimeError as e:
                self.log_error(f"Error initialising the module system: {e}")
                raise ScriptEngineTaskRunError
            if not Module._module_func:
                self.log_error("Error initialising the module system")
                raise ScriptEngineTaskRunError

        try:
            Module._module_func(cmd, *args)
        except Exception as e:
            self.log_error(f"Error while running module command: {e}")
            raise ScriptEngineTaskRunError


class ModuleLoad(Module):
    """hpc.module.load"""

    _required_arguments = ("names",)

    def __init__(self, arguments):
        arguments["cmd"] = "load"
        ModuleLoad.check_arguments(arguments)
        load_args = arguments.pop("names")
        arguments["args"] = load_args if isinstance(load_args, list) else [load_args]
        super().__init__(arguments)
