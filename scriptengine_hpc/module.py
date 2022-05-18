import os
from pathlib import Path

_DEFAULT_LMOD_VAR = "LMOD_DIR"
_DEFAULT_ENV_MOD_PATH = Path("/usr/share/Modules")


def module_lmod():
    """Returns 'module' function or None
    Lmod implementation, see
    https://lmod.readthedocs.io
    https://github.com/TACC/Lmod
    """
    return None


def module_environment_modules(env_mod_path=None):
    """Returns 'module' function or None
    Implementation for Environment modules, see
    https://modules.readthedocs.io
    http://modules.sourceforge.net
    """
    env_mod_path = Path(env_mod_path) if env_mod_path else _DEFAULT_ENV_MOD_PATH
    if not env_mod_path.exists():
        return None

    exec_vars = dict()
    try:
        exec((env_mod_path / "init/python.py").read_text(), exec_vars)
    except FileNotFoundError as e:
        raise RuntimeError(f"Could not initialise environment modules: {e}") from None

    if "module" in exec_vars:
        return exec_vars["module"]

    raise RuntimeError(
        "Could not initialise environment modules: Initialisation script does not define 'module' function"
    )
