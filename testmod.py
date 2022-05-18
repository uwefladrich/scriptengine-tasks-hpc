from operator import mod
from scriptengine_hpc.module import module_lmod, module_environment_modules

module = module_lmod() or module_environment_modules()

module("list")
