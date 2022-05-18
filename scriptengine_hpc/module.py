import os
from pathlib import Path

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
