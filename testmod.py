from scriptengine_hpc.module import module_from_lmod, module_from_environment_modules

module = module_from_lmod() or module_from_environment_modules()

module("list")
